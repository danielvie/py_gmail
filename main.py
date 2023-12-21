"""Program to read emails and archive them"""

import os.path
import os
import tempfile

from gmail import Gmail


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


app = Gmail()
app.in_test(False)

for found_messages in app.get_messages():
    if not found_messages:
        print("No messages found in INBOX.")
        continue

    temp_message: str = ""
    for i, m in enumerate(found_messages):
        sender, subject = app.get_message_details(m["id"])

        subject = subject.replace("\n", "")
        mi = f"{i+1}: {sender} | {subject} | {m['id']}"
        temp_message += f"{mi}\n"

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
