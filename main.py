from pyrogram import Client
from pyrogram.raw import functions
from pyrogram.errors import PeerIdInvalid, FloodWait, InviteHashExpired, UsernameNotOccupied, ApiIdInvalid
import time
import csv
import os
import random

# Constants
SESSIONS_DIR = "sessions"
ACCOUNTS_CSV = "accounts.csv"
API_CSV = "api.csv"

# Color codes for status messages
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# Create sessions directory
if not os.path.exists(SESSIONS_DIR):
    os.makedirs(SESSIONS_DIR)

# Global variables
accounts = []
api_credentials = []

def load_api_credentials():
    """Load API credentials from api.csv file"""
    global api_credentials
    try:
        with open(API_CSV, 'r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                if row:
                    # Handle both comma-separated and space-separated formats
                    creds = ','.join(row).replace(' ', ',').split(',')
                    if len(creds) >= 2:
                        api_credentials.append({
                            "api_id": int(creds[0].strip()),
                            "api_hash": creds[1].strip()
                        })
        print(f"{GREEN}{len(api_credentials)} API credentials loaded successfully!{RESET}")
    except FileNotFoundError:
        print(f"{RED}{API_CSV} not found. Please create it with API credentials.{RESET}")
        exit(1)
    except Exception as e:
        print(f"{RED}Error loading API credentials: {str(e)}{RESET}")
        exit(1)

def load_accounts():
    """Load phone numbers from CSV file or create a default one if not exists"""
    global accounts
    try:
        with open(ACCOUNTS_CSV, 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header
            for row in csv_reader:
                if row:
                    phone = row[0].strip()
                    phone = phone if phone.startswith('91') else f"91{phone}"
                    accounts.append({"phone": phone})
        print(f"{GREEN}{len(accounts)} Accounts loaded successfully!{RESET}")
    except FileNotFoundError:
        print(f"{RED}{ACCOUNTS_CSV} not found. Please create it with mobile numbers in it.{RESET}")
        exit(1)
    except Exception as e:
        print(f"{RED}Error loading accounts credentials: {str(e)}{RESET}")
        exit(1)

def get_random_api_credentials():
    """Get random API credentials from loaded ones"""
    if not api_credentials:
        print(f"{RED}No API credentials available!{RESET}")
        return None
    return random.choice(api_credentials)

def login_to_telegram(phone_number):
    """Initialize and start Telegram client for a given phone number"""
    try:
        creds = get_random_api_credentials()
        if not creds:
            return None

        client = Client(
            name=f"{SESSIONS_DIR}/session_{phone_number}",
            api_id=creds["api_id"],
            api_hash=creds["api_hash"],
            phone_number=phone_number
        )
        client.start()
        return client
    except ApiIdInvalid:
        print(f"{RED}Invalid API credentials for {phone_number}{RESET}")
        return None
    except FloodWait as e:
        print(f"{YELLOW}Rate limited for {phone_number}, waiting {e.x}s{RESET}")
        time.sleep(e.x)
        return None
    except Exception as e:
        print(f"{RED}Error logging in {phone_number}: {str(e)}{RESET}")
        return None

def login_all_clients():
    """Log in all clients with error handling"""
    clients = []
    
    for account in accounts:
        print(f"Logging in to account: {account['phone']}", end=" ")
        retry_count = 3
        client = None
        
        while retry_count > 0 and not client:
            client = login_to_telegram(account["phone"])
            if not client:
                print(f"{YELLOW}Retrying... ({retry_count-1} attempts left){RESET}")
                retry_count -= 1
                time.sleep(2)
        
        if client:
            clients.append(client)
            print(f"{GREEN}{{Success}}{RESET}")
            time.sleep(1)
        else:
            print(f"{RED}{{Failed to log in after all attempts}}{RESET}")

    return clients

def mark_channel_as_read(client, channel_id, start_id=None, last_n_messages=None, view_delay=1):
    try:
        phone = client.get_me().phone_number
        print(f"Marking messages read for {phone}...", end=' ')
        
        # Get channel entity with error handling
        try:
            channel = client.get_chat(channel_id)
            channel_peer = client.resolve_peer(channel_id)
        except (PeerIdInvalid, UsernameNotOccupied):
            print(f"{RED}Invalid channel ID or username{RESET}")
            return
        except Exception as e:
            print(f"{RED}Error accessing channel: {str(e)}{RESET}")
            return
        
        # Get all message IDs with error handling
        all_message_ids = []
        try:
            for message in client.get_chat_history(channel.id):
                all_message_ids.append(message.id)
                if last_n_messages and len(all_message_ids) >= last_n_messages:
                    break
        except Exception as e:
            print(f"{RED}Error getting message history: {str(e)}{RESET}")
            return
            
        if not all_message_ids:
            print(f"{YELLOW}No messages found in channel{RESET}")
            return
            
        # Filter messages based on start_id or last_n_messages
        if start_id is not None:
            try:
                start_index = all_message_ids.index(start_id)
                all_message_ids = all_message_ids[:start_index + 1]
            except ValueError:
                print(f"{YELLOW}Start message ID {start_id} not found in channel{RESET}")
                return
        elif last_n_messages is not None:
            all_message_ids = all_message_ids[:last_n_messages]
        
        # Process messages in batches with error handling
        batch_size = 100
        total_messages_processed = 0
        
        for i in range(0, len(all_message_ids), batch_size):
            batch_ids = all_message_ids[i:i + batch_size]
            
            try:
                # Mark messages as read in batches
                client.invoke(
                    functions.channels.ReadMessageContents(
                        channel=channel_peer,
                        id=batch_ids
                    )
                )
                
                # Increment view counts
                client.invoke(
                    functions.messages.GetMessagesViews(
                        peer=channel_peer,
                        id=batch_ids,
                        increment=True
                    )
                )
                
                total_messages_processed += len(batch_ids)
                print(f"{GREEN}{total_messages_processed} messages marked as read{RESET}")
                time.sleep(view_delay)  # Delay between views as per user input
                
            except FloodWait as e:
                print(f"{YELLOW}Rate limited, waiting {e.x}s{RESET}")
                time.sleep(e.x)
                continue
            except Exception as e:
                print(f"{RED}Error processing batch: {str(e)}{RESET}")
                continue
        
        # Mark entire history as read
        client.invoke(
            functions.channels.ReadHistory(
                channel=channel_peer,
                max_id=max(all_message_ids) if all_message_ids else 0
            )
        )
            
    except Exception as e:
        print(f"{RED}Failed: {str(e)}{RESET}")

def process_clients(clients, action, target, start_id=None, last_n_messages=None, view_delay=1):
    """Process all clients with proper cleanup"""
    if not clients:
        print(f"{RED}No active clients available{RESET}")
        return
        
    for client in clients:
        if action == "mark_channel_as_read":
            mark_channel_as_read(client, target, start_id, last_n_messages, view_delay)

def main():
    print(f"{GREEN}Loading API credentials...{RESET}")
    load_api_credentials()
    
    print(f"{GREEN}Loading accounts...{RESET}")
    load_accounts()
    
    if not accounts or not api_credentials:
        return

    clients = []
    
    while True:
        try:
            print("\nOptions:")
            print("1. Login Clients")
            print("2. Mark last X messages as read")
            print("3. Mark messages as read from specific ID to latest")
            print("4. Mark all channel messages as read")
            print("5. Exit")
            
            choice = input("Enter your choice (1-5): ")
            
            if choice == "1":
                print(f"\n{GREEN}Logging in all clients...{RESET}")
                clients = login_all_clients()
                if clients:
                    print(f"{GREEN}All clients are logged in successfully.{RESET}")
                else:
                    print(f"{RED}No clients logged in.{RESET}")
            elif choice == "2":
                if len(clients) == 0:
                    print(f"{YELLOW}Please execute option 1 first.{RESET}")
                else:
                    channel_link = input("Enter channel link or @ username: ")
                    try:
                        num_messages = int(input("Enter number of latest messages to mark as read: "))
                        view_delay = float(input("Enter delay (in seconds) for each view increment (default is 1 second): ") or 1)
                        process_clients(clients, "mark_channel_as_read", channel_link, None, num_messages, view_delay)
                    except ValueError:
                        print(f"{RED}Invalid number. Please enter a valid number.{RESET}")
            elif choice == "3":
                if len(clients) == 0:
                    print(f"{YELLOW}Please execute option 1 first.{RESET}")
                else:
                    channel_link = input("Enter channel link or @ username: ")
                    try:
                        start_id = int(input("Enter the message ID to start from: "))
                        view_delay = float(input("Enter delay (in seconds) for each view increment (default is 1 second): ") or 1)
                        process_clients(clients, "mark_channel_as_read", channel_link, start_id, None, view_delay)
                    except ValueError:
                        print(f"{RED}Invalid message ID. Please enter a number.{RESET}")
            elif choice == "4":
                if len(clients) == 0:
                    print(f"{YELLOW}Please execute option 1 first.{RESET}")
                else:
                    channel_link = input("Enter channel link or @ username: ")
                    view_delay = float(input("Enter delay (in seconds) for each view increment (default is 1 second): ") or 1)
                    process_clients(clients, "mark_channel_as_read", channel_link, None, None, view_delay)
            elif choice == "5":
                print(f"{GREEN}Cleaning up and exiting...{RESET}")
                for client in clients:
                    try:
                        client.stop()
                    except:
                        pass
                break
            else:
                print(f"{YELLOW}Invalid choice. Please enter a number between 1 and 5.{RESET}")
                
        except KeyboardInterrupt:
            print(f"\n{YELLOW}Interrupted by user. Cleaning up...{RESET}")
            for client in clients:
                try:
                    client.stop()
                except:
                    pass
            break
        except Exception as e:
            print(f"{RED}Unexpected error: {str(e)}{RESET}")

if __name__ == "__main__":
    main()
