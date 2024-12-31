from pyrogram import Client
from pyrogram.errors import FloodWait
from pyrogram.raw import functions
import time
import csv
import os

API_ID = 954660
API_HASH = "722f3cedf17305b3955a545b28b53995"
SESSIONS_DIR = "sessions"
CSV_FILE = "accounts.csv"

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

if not os.path.exists(SESSIONS_DIR):
    os.makedirs(SESSIONS_DIR)

def load_accounts():
    accounts = []
    try:
        with open(CSV_FILE, 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)
            for row in csv_reader:
                if row:
                    phone = row[0].strip()
                    phone = phone if phone.startswith('91') else f"91{phone}"
                    accounts.append({"phone": phone})
        print(f"{GREEN}{len(accounts)} Accounts loaded{RESET}")
        return accounts
    except FileNotFoundError:
        print(f"{RED}{CSV_FILE} not found. Create it with phone numbers.{RESET}")
        return []

def login_account(phone_number):
    try:
        client = Client(
            f"{SESSIONS_DIR}/session_{phone_number}",
            api_id=API_ID,
            api_hash=API_HASH,
            phone_number=phone_number
        )
        client.start()
        return client
    except Exception as e:
        print(f"{RED}Login failed for {phone_number}: {str(e)}{RESET}")
        return None

def mark_channel_read(client, channel_id):
    try:
        phone = client.get_me().phone_number
        print(f"Marking channel messages read for {phone}...", end=" ")
        
        # Get channel entity
        channel = client.get_chat(channel_id)
        channel_peer = client.resolve_peer(channel_id)
        
        # Get latest message
        messages = client.get_chat_history(channel.id, limit=1)
        latest_message = next(messages, None)
        
        if latest_message:
            # Mark channel messages as read
            client.invoke(
                functions.channels.ReadMessageContents(
                    channel=channel_peer,
                    id=[latest_message.id]
                )
            )
            
            # Also mark history as read
            client.invoke(
                functions.channels.ReadHistory(
                    channel=channel_peer,
                    max_id=latest_message.id
                )
            )
            print(f"{GREEN}Done{RESET}")
        else:
            print(f"{YELLOW}No messages found{RESET}")
            
    except FloodWait as e:
        print(f"{YELLOW}Rate limited, waiting {e.x}s{RESET}")
        time.sleep(e.x)
    except Exception as e:
        print(f"{RED}Failed: {str(e)}{RESET}")
    time.sleep(2)

def main():
    accounts = load_accounts()
    if not accounts:
        return

    clients = []
    print("\nLogging in to accounts...")
    for account in accounts:
        client = login_account(account["phone"])
        if client:
            clients.append(client)
            time.sleep(1)

    while True:
        print("\nOptions:")
        print("1. Login Clients")
        print("2. Mark channel messages as read")
        print("3. Exit")
        
        choice = input("Choice (1-3): ")
        
        if choice == "1":
            channel = input("Enter channel username or link: ")
            for client in clients:
                mark_channel_read(client, channel)
        elif choice == "2":
            print("Exiting...")
            for client in clients:
                try:
                    client.stop()
                except:
                    pass
            break

if __name__ == "__main__":
    main()