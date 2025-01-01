from pyrogram import Client
from pyrogram.raw import functions
from pyrogram.errors import PeerIdInvalid, FloodWait, InviteHashExpired, UsernameNotOccupied
import time
import csv
import os

# Constants
API_ID = 954660
API_HASH = "722f3cedf17305b3955a545b28b53995"
SESSIONS_DIR = "sessions"
CSV_FILE = "accounts.csv"
DEFAULT_PHONE = "9315988300"

# Color codes for status messages
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# Create sessions directory
if not os.path.exists(SESSIONS_DIR):
    os.makedirs(SESSIONS_DIR)

# Global variable to store loaded accounts
accounts = []

def load_accounts():
    """Load phone numbers from CSV file or create a default one if not exists"""
    global accounts
    try:
        with open(CSV_FILE, 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header
            for row in csv_reader:
                if row:
                    phone = row[0].strip()
                    phone = phone if phone.startswith('91') else f"91{phone}"
                    accounts.append({"phone": phone})
        print(f"{GREEN}{len(accounts)} Accounts loaded successfully!{RESET}")
    except FileNotFoundError:
        print(f"{RED}{CSV_FILE} not found. Creating a sample file...{RESET}")
        with open(CSV_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['phone'])
            writer.writerow([DEFAULT_PHONE])
        accounts = [{'phone': f"91{DEFAULT_PHONE}"}]
        print(f"{GREEN}Sample file created with default account!{RESET}")

def login_to_telegram(phone_number):
    """Initialize and start Telegram client for a given phone number"""
    try:
        client = Client(
            name=f"{SESSIONS_DIR}/session_{phone_number}",
            api_id=API_ID,
            api_hash=API_HASH,
            phone_number=phone_number
        )
        client.start()
        return client
    except Exception as e:
        print(f"{RED}{{failed - {str(e)}}}{RESET}")
        return None

def login_all_clients():
    """Log in all clients."""
    clients = []
    
    for account in accounts:
        print(f"Logging in to account: {account['phone']}", end=" ")
        client = login_to_telegram(account["phone"])
        if client:
            clients.append(client)
            print(f"{GREEN}{{Success}}{RESET}")
            time.sleep(1)  # Delay between logins
        else:
            print(f"{RED}{{Failed to log in}}{RESET}")

    return clients

def mark_channel_as_read(client, channel_id):
    try:
        phone = client.get_me().phone_number
        print(f"Marking messages read for {phone}...", end=' ')
        
        # Get channel entity
        channel = client.get_chat(channel_id)
        channel_peer = client.resolve_peer(channel_id)
        
        # Get messages in smaller chunks
        batch_size = 100
        message_ids = []
        total_messages_processed = 0
        
        for message in client.get_chat_history(channel.id):
            message_ids.append(message.id)
            if len(message_ids) >= batch_size:
                try:
                    # Mark messages as read in batches
                    client.invoke(
                        functions.channels.ReadMessageContents(
                            channel=channel_peer,
                            id=message_ids
                        )
                    )
                    
                    # Increment view counts
                    client.invoke(
                        functions.messages.GetMessagesViews(
                            peer=channel_peer,
                            id=message_ids,
                            increment=True
                        )
                    )
                    
                    total_messages_processed += len(message_ids)
                    print(f"{GREEN}{total_messages_processed} messages as read{RESET}")
                    message_ids = []  # Reset for next batch
                    time.sleep(2)  # Delay between batches to avoid rate limits
                except FloodWait as e:
                    print(f"{YELLOW}Rate limited, waiting {e.x}s{RESET}")
                    time.sleep(e.x)
                    continue
        
        # Process any remaining messages
        if message_ids:
            try:
                client.invoke(
                    functions.channels.ReadMessageContents(
                        channel=channel_peer,
                        id=message_ids
                    )
                )
                client.invoke(
                    functions.messages.GetMessagesViews(
                        peer=channel_peer,
                        id=message_ids,
                        increment=True
                    )
                )
                total_messages_processed += len(message_ids)
                print(f"{GREEN}{len(message_ids)} messages as read{RESET}")
            except FloodWait as e:
                print(f"{YELLOW}Rate limited, waiting {e.x}s{RESET}")
                time.sleep(e.x)
        
        # Mark entire history as read
        client.invoke(
            functions.channels.ReadHistory(
                channel=channel_peer,
                max_id=max(message_ids) if message_ids else 0
            )
        )
            
    except Exception as e:
        print(f"{RED}Failed: {str(e)}{RESET}")
    time.sleep(2)

def process_clients(clients, action, target):
    """Process all clients with proper cleanup"""
    for client in clients:
        if action == "mark_channel_as_read":
            mark_channel_as_read(client, target)

def main():
    load_accounts()
    if not accounts:
        return

    clients = []

    while True:
        print("\nOptions:")
        print("1. Login Clients")
        print("2. Mark all channel messages as read")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == "1":
            print(f"\n{GREEN}Logging in all clients...{RESET}")
            clients = login_all_clients()
            if clients:
                print(f"{GREEN}All clients are logged in successfully.{RESET}")
            else:
                print(f"{RED}No clients logged in.{RESET}")
        elif choice == "2":
            if len(clients) == 0:
                print("Please execute option 1 first.")
            else:
                channel_link = input("Enter channel link or @ username: ")
                process_clients(clients, "mark_channel_as_read", channel_link)
        elif choice == "3":
            print("Exiting...")
            for client in clients:
                try:
                    client.stop()
                except:
                    pass
            break

if __name__ == "__main__":
    main()