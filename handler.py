import email
from email.header import Header, decode_header, make_header
import os
import re
import requests
import imaplib
import json
import boto3

if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

EMAIL = os.environ["EMAIL"]
PASSWORD = os.environ["PASSWORD"]
SERVER = os.environ["SERVER"]
MAX_DEPTH = int(os.environ["MAX_DEPTH"])
API_KEY = os.environ["API_KEY"]
CHAT_ID = os.environ["CHAT_ID"]
LAST_ID = int(os.environ["LAST_ID"])
CHANNEL_NAME = os.environ["CHANNEL_NAME"]
BUCKETNAME = os.environ["BUCKETNAME"]
CONFIG = os.environ["CONFIG"]
BLACKLIST = os.environ["BLACKLIST"]
MAILBOX = os.environ["MAILBOX"]
ROOT = ""

s3 = boto3.resource("s3")
obj = s3.Object(BUCKETNAME, CONFIG)
try:
    BLACKLIST = s3.Object(BUCKETNAME, BLACKLIST).get()["Body"].read().decode("utf8")
    BLACKLIST = [line.replace("\r", "") for line in BLACKLIST.split("\n")]
except Exception:
    BLACKLIST = []
try:
    config = obj.get()["Body"].read()
except Exception:
    config = json.dumps({"MAX_DEPTH": MAX_DEPTH, "LAST_ID": LAST_ID})


def telegram_bot(event, context):
    global config
    status = main()
    body = {"message": status, "input": event}

    response = {"statusCode": 200, "body": json.dumps(body)}

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """


def login():
    update_config()
    print("Starting", SERVER, "server")
    mail = imaplib.IMAP4_SSL(SERVER)
    print("Logging in with", EMAIL)
    mail.login(EMAIL, PASSWORD)
    print("Logged in")
    mail.select(MAILBOX)
    return mail


def main():
    mail = login()
    global EMAIL, PASSWORD, SERVER, MAX_DEPTH, LAST_ID, ROOT
    update_config()

    _, data = mail.search(None, "All")

    mail_ids = []

    for block in data:
        mail_ids += block.split()

    messages = [""]
    subject_arr = [""]
    set_config(len(mail_ids))

    print("Email amount:", len(mail_ids), "-", LAST_ID, "=", len(mail_ids) - LAST_ID)
    for i in range(len(mail_ids), 1, -1):
        if (
            (abs(len(mail_ids) - i) >= MAX_DEPTH and MAX_DEPTH != 0)
            or i == LAST_ID
            or LAST_ID > len(mail_ids)
        ):
            break
        i = bytes(str(i), encoding="utf-8")

        _, data = mail.fetch(i, "(RFC822)")
        for response_part in data:

            if isinstance(response_part, tuple):
                message = email.message_from_bytes(response_part[1])
                mail_from = message["from"]

                # validate if the mail is in blacklist
                if is_black_listed(mail_from):
                    continue

                mail_from = (
                    re.sub("<.*>", "", mail_from)
                    .replace('"', "")
                    .replace("_", "")
                    .replace("*", "")
                )
                mail_subject = message["subject"]
                mail_subject = make_header(decode_header(mail_subject))
                mail_subject = f"{mail_subject}".replace("_", "").replace("*", "")

                # avoid duplicate subject
                if mail_subject in subject_arr:
                    continue

                subject_arr.append(mail_subject)

                email_from = f"📧 From: `{mail_from}`"
                subject = f"_Subject_:\n\t> \t\t*{mail_subject}*"
                content = f"{email_from}\n{subject}\n\n"

                for j in range(len(messages)):
                    if len(content) + len(messages[j]) < 4096:
                        messages[j] += content
                        break
                else:
                    print("Message too large, send in a new message")
                    messages.append((email_from, content))
                print("Appended", email_from)

    for message in messages:
        send_message(message)
    string = (
        "All latest emails notification sent."
        if LAST_ID != len(mail_ids)
        else "No new emails"
    )
    print(string)
    return True


def is_black_listed(mail_from):
    global ROOT, BLACKLIST
    for blacklist in BLACKLIST:
        blacklist = blacklist.strip()
        if blacklist in mail_from:
            return True
    return False


def send_message(mail_contents):
    global API_KEY, CHAT_ID
    if not CHAT_ID:
        CHAT_ID = f"@{CHANNEL_NAME}"
    data = {"chat_id": CHAT_ID, "text": mail_contents, "parse_mode": "Markdown"}
    res = requests.post(
        f"https://api.telegram.org/bot{API_KEY}/sendMessage?chat_id={CHAT_ID}",
        data=data,
        json=data,
    )


def update_config():
    global MAX_DEPTH, CHAT_ID, LAST_ID, config, obj
    json_payload = json.loads(config)

    # Only apply when there is no last id
    if int(json_payload["LAST_ID"]) == 0:
        MAX_DEPTH = json_payload["MAX_DEPTH"]
    else:
        MAX_DEPTH = json_payload["MAX_DEPTH"] * 100000

    LAST_ID = json_payload["LAST_ID"]


def set_config(last_id):
    global MAX_DEPTH, CHAT_ID, ROOT, obj

    json_payload = json.dumps(
        {"MAX_DEPTH": int(MAX_DEPTH / 100000), "CHAT_ID": CHAT_ID, "LAST_ID": last_id},
        indent=2,
    )
    try:
        obj.delete()
    except Exception:
        pass

    obj = s3.Object(os.environ["BUCKETNAME"], os.environ["CONFIG"])
    obj.put(Body=json_payload)


if __name__ == "__main__":
    telegram_bot(None, None)
