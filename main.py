# import base64
import pickle
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

import re
import os
import tempfile


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

class Gmail():
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
    creds = None
    service = None
    items = []
    q:str = None
    
    def __init__(self) -> None:
        # get token from previous session
        if os.path.exists('token.pickle'):
            with open ('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
                
        # ask login if there is no token
        if not self.creds or not self.creds.valid:
            self.creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credential.json', self.SCOPES)
            self.creds = flow.run_local_server(port=0)
            with open('open.pickle', 'wb') as token:
                pickle.dump(self.creds, token)
            
        self.service = build('gmail', 'v1', credentials=self.creds)
        
        # get list of queries
        file = "query_list.txt"
        
        with open(file, "r") as f:
            while l := f.readline():
                self.items.append(l.replace("\n", ""))


    def query(self, qry:str):
        if qry.lower() == 'inbox':
            print(f'query inbox')
            results = self.service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
            return results.get('messages', [])

        if qry.lower() == 'unread':
            print(f'query unread')
            results = self.service.users().messages().list(userId='me', labelIds=['UNREAD']).execute()
            return results.get('messages', [])

        print(f'query: {qry}')
        results = self.service.users().messages().list(userId='me', q=qry, labelIds=['INBOX']).execute()
        return results.get('messages', [])
        

    def get_message_details(self, message_id):
        msg = app.service.users().messages().get(userId='me', id=message_id).execute()
        headers = msg['payload']['headers']

        subject = next((header['value'] for header in headers if header['name'] == 'Subject'), None)
        sender = next((header['value'] for header in headers if header['name'] == 'From'), None)
        return sender, subject

    def get_first_query(self):
        items_with_from = " ".join([f"from:'{i}'" for i in app.items])
        return f'{{{items_with_from}}}'

    def __del__(self) -> None:
        print('destructor')


app = Gmail()

q = app.get_first_query()

while True:
    
    if not q:
        value = input("\nEnter a string value to search for in message titles/subjects or 'exit' to quit: ")
    else:
        value = q
        q = ""

    # Exit condition
    if not value or value.lower() == 'exit':
        break

    # Searching messages based on the value in INBOX
    # found_messages = search_messages(f'subject:{value} OR from:{value}')
    found_messages = app.query(value)

    if not found_messages:
        print("No messages found in INBOX.")
        continue

    temp_message:str = "" 

    print("\nFound Messages:")
    messages_list = []
    for m in found_messages:
        sender, subject = app.get_message_details(m['id'])
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
                app.service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()
                # Archive
                app.service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['INBOX']}).execute()

        print("Messages have been marked as read and archived.")
        