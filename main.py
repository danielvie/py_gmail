"""Program to read emails and archive them"""

from gmail import Gmail, call_vim

app = Gmail()
app.in_test(False)


val = [
    "--new values--",
    '"bla"',
    '"ble"',
    "--end new values--",
    '"#WeAreSST"',
    '"nederlandse"',
    '"dhl"',
    '"adidas"',
    '"flying blue"',
    '"ADPList"',
    '"Airalo"',
    '"bol.com"',
    '"Bowl"',
    '"chessly"',
    '"chess"',
    '"codesandbox"',
    '"Costa Cruzeiros"',
    '"Coursera"',
    '"crosshill"',
    '"DHL Parcel"',
    '"Amazon.nl"',
    '"disney"',
    '"disney"',
    '"duolingo"',
    '"estadao"',
    '"eurostar"',
    '"flixbus"',
    '"fusion 360"',
    '"grammarly"',
    '"latam"',
    '"leetcode"',
    '"lego"',
    '"linkedin"',
    '"masterclass"',
    '"mathworks"',
    '"medium"',
    '"meetup"',
    '"microsoft"',
    '"modular"',
    '"nelogica"',
    '"ninjatrader"',
    '"nomad"',
    '"nordvpn"',
    '"Nubank"',
    '"nubank"',
    '"nuinvest"',
    '"nvidia"',
    '"paris 2024"',
    '"Pathé"',
    '"prime"',
    '"ptc.com"',
    '"reclameaqui"',
    '"renpho"',
    '"Ryanair"',
    '"seedtable"',
    '"shaping"',
    '"skillshare"',
    '"SNCF"',
    '"splitwise"',
    '"strava"',
    '"swapfiets"',
    '"thalys"',
    '"threejs"',
    '"thuisbezorgd"',
    '"trek"',
    '"trivago"',
    '"Twitch"',
    '"valor.com.br"',
]


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
