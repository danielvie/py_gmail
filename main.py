# import base64
import pickle
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

import re
import os
import tempfile


# Set up the Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

creds = None

# token.pickle stores the users access
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)

# if there are no valid credentials, let the user log in
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credential.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            # service = build('gmail', 'v1', credentials=creds)
            pickle.dump(creds, token)

service = build('gmail', 'v1', credentials=creds)

def search_messages(query:str):
    
    if query.lower() == 'inbox':
        print(f'query inbox')
        results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
        return results.get('messages', [])

    if query.lower() == 'unread':
        print(f'query unread')
        results = service.users().messages().list(userId='me', labelIds=['UNREAD']).execute()
        return results.get('messages', [])

    print(f'query: {query}')
    results = service.users().messages().list(userId='me', q=query, labelIds=['INBOX']).execute()
    return results.get('messages', [])


def get_message_details(message_id):
    msg = service.users().messages().get(userId='me', id=message_id).execute()
    headers = msg['payload']['headers']

    subject = next((header['value'] for header in headers if header['name'] == 'Subject'), None)
    sender = next((header['value'] for header in headers if header['name'] == 'From'), None)
    return sender, subject

def call_vim(temp_message:str) -> str:
    # create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False, mode="w") as tf:
        temp_message += "\n"
        temp_message += "\n"
        temp_message += "// r: remove message\n"
        temp_message += "// k: keep message"
        tf.write(temp_message)
        temp_file_name = tf.name

    # open the temporary file with vim
    os.system(f'v {temp_file_name}')
    
    # read the contents of the temporary file
    with open(temp_file_name, 'r') as tf:
        content = tf.read()
        
    # delete the temporary file
    os.remove(temp_file_name)

    return content

def get_email_position(content):
    res = []
    for msg in content.split("\n"):
        if match := re.match('(?P<type>^\w)\s+(?P<message>.*)', msg):
            values = match.groupdict()
            res.append(int(values['type']))
    
    return res

# first try
items = ["DHL Parcel", "Coursera", "#WeAreSST", "Nubank", "Pathé", "Airalo", "Twitch", "Costa Cruzeiros", 
         "Ryanair", "ADPList", "Bowl", "SNCF", "reclameaqui", "thuisbezorgd", "microsoft",
         "mathworks", "disney", "swapfiets", "chessly", "thalys", "nubank", "trivago", "grammarly",
         "nuinvest", "renpho", "seedtable", "nordvpn", "meetup", "shaping", "trek", "prime", "nomad",
         "latam", "estadao", "medium", "duolingo", "modular", "ninjatrader", "ptc.com", "nvidia",
         "codesandbox", "fusion 360", "paris 2024", "crosshill", "valor.com.br", "bol.com", "nelogica",
         "skillshare", "threejs", "linkedin", "adidas", "splitwise", "eurostar", "lego", "masterclass", 
         "leetcode", "strava", "flixbus"]

# adding `from:` to itens
items_from = " ".join([f"from:'{i}'" for i in items])

query = f'{{{items_from}}}'
# print(query)

while True:
    
    if not query:
        value = input("\nEnter a string value to search for in message titles/subjects or 'exit' to quit: ")
    else:
        value = query
        query = ""

    # Exit condition
    if not value or value.lower() == 'exit':
        break

    # Searching messages based on the value in INBOX
    # found_messages = search_messages(f'subject:{value} OR from:{value}')
    found_messages = search_messages(value)

    if not found_messages:
        print("No messages found in INBOX.")
        continue


    temp_message:str = "" 

    print("\nFound Messages:")
    messages_list = []
    for m in found_messages:
        sender, subject = get_message_details(m['id'])
        # print(f"Sender: {sender} | Subject: {subject}")
        mi = f"{sender} | Subject: {subject}"
        temp_message += f"remove {mi}\n"

        N = 100
        if len(mi) > N:
            mi = f"{mi[:N]}..."

        messages_list.append(f"-> {mi}")

    content = call_vim(temp_message)
    action = [(re.match(r'(\w+)', line).group() == 'remove') for line in content.split('\n') if re.match(r'(\w+)', line)]
    
    # display messages to be filtered
    count_messages = 0
    for m, a in zip(messages_list, action): 
        if a:
            count_messages += 1
            print(m)


    choice = input(f"\nDo you want to mark these ({count_messages}) as read and archive them? (yes/No): ").strip().lower()
    
    if choice == 'yes' or choice == 'y':
        for message, action in zip(found_messages, action):
            if action == 1:
                # Mark as read
                service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()
                # Archive
                service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['INBOX']}).execute()

        print("Messages have been marked as read and archived.")
        