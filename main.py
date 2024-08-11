"""Program to read emails and archive them"""

import sys
from gmail import Gmail, call_vim


def main(in_test=False):
    """Main function to read emails and archive them"""
    app = Gmail()
    app.in_test(in_test)

    for found_messages in app.get_messages():
        if not found_messages:
            print("No messages found in INBOX.")
            continue

        temp_message: str = ""
        messages = []
        for m in found_messages:
            sender, subject, date = app.get_message_details(m["id"])

            subject = subject.replace("\n", "")
            messages.append(f"{sender} | {subject} | ({date}) | {m['id']}")

        messages.sort()
        for i, mi in enumerate(messages):
            temp_message += f"{i+1}: {mi}\n"

        content = call_vim(temp_message)

        # display messages to be filtered
        list_of_msg_ids = []
        for line in content.split("\n"):
            if line:
                list_of_msg_ids.append(line.split("| ")[-1].strip())

        print("\n\n")
        print(content)
        choice = (
            input(
                f"\nMark these ({len(list_of_msg_ids)}) as read and archive them? (yes/No): "
            )
            .strip()
            .lower()
        )

        if choice in ("yes", "y"):
            app.remove_messages(list_of_msg_ids)


if __name__ == "__main__":

    # read parameters from file call
    IN_TEST = "--test" in sys.argv

    main(in_test=IN_TEST)
