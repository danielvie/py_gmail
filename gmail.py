"""program to read emails and archive them"""

import pickle

import re
import os
import os.path
import tempfile

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory

from rich.console import Console
from rich.progress import track


history = InMemoryHistory()
session = PromptSession(history=history)
console = Console()


def call_vim(message: str) -> str:
    """Function that calls vim to edit messages"""
    # create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False, mode="w") as tf:
        tf.write(message)
        temp_file_name = tf.name

    # open the temporary file with vim
    os.system(f"v {temp_file_name}")

    # read the contents of the temporary file
    with open(temp_file_name, "r", encoding="utf-8") as tf:
        res = tf.read()

    # delete the temporary file
    os.remove(temp_file_name)

    return res


class Gmail:
    """Class that reads the gmails ans manages logic"""

    SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
    creds = None
    service = None
    items = []
    test: bool = False
    msgid = {}
    query_history = set()

    def __init__(self) -> None:
        # get token from previous session
        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                self.creds = pickle.load(token)

        # ask login if there is no token
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credential.json", self.SCOPES
                )
                self.creds = flow.run_local_server(port=0)
                with open("token.pickle", "wb") as token:
                    pickle.dump(self.creds, token)

        self.service = build("gmail", "v1", credentials=self.creds)

        # get list of queries
        file = "query_list.txt"

        with open(file, "r", encoding="utf-8") as f:
            while l := f.readline():
                self.items.append(l.replace("\n", ""))

    def in_test(self, value):
        """sets module to test mode"""
        if value:
            tam = 40
            barra = "-" * tam
            msg_ = "APP IN TEST!!!"
            msg = f"[red]{msg_}[/red]"
            console.print(barra, style="bold red")
            console.print(barra, style="bold red")
            console.print(f"{msg: ^{tam+len(msg_)}}")
            console.print(barra, style="bold red")
            console.print(barra, style="bold red")
        self.test = value

    def query(self, qry: str):
        """calls a query for messages in gmail"""

        if qry.lower() == "inbox":
            print("query inbox")
            results = (
                self.service.users()
                .messages()
                .list(userId="me", labelIds=["INBOX"])
                .execute()
            )
            return results.get("messages", [])

        if qry.lower() == "unread":
            print("query unread")
            results = (
                self.service.users()
                .messages()
                .list(userId="me", labelIds=["UNREAD"])
                .execute()
            )
            return results.get("messages", [])

        print(f"query: {qry}")
        results = (
            self.service.users()
            .messages()
            .list(userId="me", q=qry, labelIds=["INBOX"])
            .execute()
        )
        messages = results.get("messages", [])
        self.msgid = {}
        for m in messages:
            self.msgid[m["id"]] = True

        return messages

    def get_message_details(self, message_id):
        """get details from message from id"""
        msg = self.service.users().messages().get(userId="me", id=message_id).execute()
        headers = msg["payload"]["headers"]

        subject = next(
            (header["value"] for header in headers if header["name"] == "Subject"), None
        )
        sender = next(
            (header["value"] for header in headers if header["name"] == "From"), None
        )
        return sender, subject

    def get_first_query(self):
        """get the query using `query_list.txt` values"""
        items_with_from = " ".join([f"from:'{i}'" for i in self.items])
        return f"{{{items_with_from}}}"

    def get_messages(self):
        """get messages from gmail"""
        value = self.get_first_query()
        yield self.query(value)

        while True:
            # prompt new query with history
            try:
                value = session.prompt("\nSearch for ... or 'exit' to quit: ")
            except KeyboardInterrupt:
                break

            # Exit condition
            if not value or value.lower() == "exit":
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

            if value == "e":
                print("eu deveria editar algo aqui")
                print(self.query_history)

                with open("query_list.txt", "r", encoding="utf-8") as f:
                    temp_message = "--new values--\n"
                    temp_message += "\n".join(f'"{q}"' for q in self.query_history)

                    temp_message += "\n--end new values--\n"
                    temp_message += f.read()

                    res = call_vim(temp_message)

                    new_file = "\n".join(
                        filter(lambda x: not re.match(r"^--.+--$", x), res.split("\n"))
                    )

                with open("query_list.txt", "w", encoding="utf-8") as f:
                    f.write(new_file)

                continue

            self.query_history.add(value)
            yield self.query(value)

        print("\n")

    def mark_as_read(self, msg_id):
        """mark message as read"""
        if self.test:
            _, subject = self.get_message_details(msg_id)
            console.print(f"\n[blue]mark read for[/blue]: {subject}")
            return

        self.service.users().messages().modify(
            userId="me", id=msg_id, body={"removeLabelIds": ["UNREAD"]}
        ).execute()

    def mark_as_arquived(self, msg_id):
        """remove label inbox from message"""
        if self.test:
            _, subject = self.get_message_details(msg_id)
            console.print(f"\n[blue]mark arquived for[/blue]: {subject}")
            return

        self.service.users().messages().modify(
            userId="me", id=msg_id, body={"removeLabelIds": ["INBOX"]}
        ).execute()

    def remove_messages(self, ids):
        """call all methods to remove messages"""
        for m_id in track(ids, description="processing... "):
            # Mark as read
            self.mark_as_read(m_id)
            # Archive
            self.mark_as_arquived(m_id)

    def __del__(self) -> None:
        pass
