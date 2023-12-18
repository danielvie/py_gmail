
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit import PromptSession

from rich.console import Console
from rich.progress import track
import os

history = InMemoryHistory()
session = PromptSession(history=history)
console = Console()

class Gmail():
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
    creds = None
    service = None
    items = []
    test: bool = False
    msgid = {}
    
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

    def in_test(self, value):
        if value:
            tam = 40
            bar = '-'*tam
            msg_ = 'APP IN TEST!!!'
            msg = f'[red]{msg_}[/red]'
            console.print(bar, style='bold red')
            console.print(bar, style='bold red')
            console.print(f'{msg: ^{tam+len(msg_)}}')
            console.print(bar, style='bold red')
            console.print(bar, style='bold red')
        self.test = value

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
        messages = results.get('messages', [])
        self.msgid = {}
        for m in messages:
            self.msgid[m['id']] = True

        return messages
        

    def get_message_details(self, message_id):
        msg = self.service.users().messages().get(userId='me', id=message_id).execute()
        headers = msg['payload']['headers']

        subject = next((header['value'] for header in headers if header['name'] == 'Subject'), None)
        sender = next((header['value'] for header in headers if header['name'] == 'From'), None)
        return sender, subject

    def get_first_query(self):
        items_with_from = " ".join([f"from:'{i}'" for i in self.items])
        return f'{{{items_with_from}}}'

    def get_messages(self):
        value = self.get_first_query()
        yield self.query(value)
        
        while True:
            # prompt new query with history
            try:
                value = session.prompt("\nEnter a string value to search for in message titles/subjects or 'exit' to quit: ")
            except KeyboardInterrupt:
                break

            # Exit condition
            if not value or value.lower() == 'exit':
                break
            
            if value == ".":
                yield self.query(self.get_first_query())
                continue
            
            if value == "!t":
                self.in_test(True)
                yield self.query(self.get_first_query())
                continue

            if value == "~t":
                self.in_test(False)
                yield self.query(self.get_first_query())
                continue

            yield self.query(value)
        
        print('\n')
        
    def mark_as_read(self, msg_id):
        if self.test:
            _, subject = self.get_message_details(msg_id)
            console.print(f'\n[blue]mark read for[/blue]: {subject}')
            return

        self.service.users().messages().modify(userId='me', id=msg_id, body={'removeLabelIds': ['UNREAD']}).execute()

    def mark_as_arquived(self, msg_id):
        if self.test:
            _, subject = self.get_message_details(msg_id)
            console.print(f'\n[blue]mark arquived for[/blue]: {subject}')
            return

        self.service.users().messages().modify(userId='me', id=msg_id, body={'removeLabelIds': ['INBOX']}).execute()

    def remove_messages(self, ids):
        for m_id in track(ids, description="processing... "):
            # Mark as read
            self.mark_as_read(m_id)
            # Archive
            self.mark_as_arquived(m_id)


    def __del__(self) -> None:
        pass