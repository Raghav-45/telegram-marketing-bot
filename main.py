from pyrogram import Client
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

def load_accounts():
    """Load phone numbers from CSV file or create a default one if not exists"""
    accounts = []
    try:
        with open(CSV_FILE, 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header
            for row in csv_reader:
                if row:
                    phone = row[0].strip()
                    phone = phone if phone.startswith('91') else f"91{phone}"
                    accounts.append({"phone": phone})
        return accounts
    except FileNotFoundError:
        print(f"{CSV_FILE} not found. Creating a sample file...")
        with open(CSV_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['phone'])
            writer.writerow([DEFAULT_PHONE])
        return [{'phone': f"91{DEFAULT_PHONE}"}]

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
        time.sleep(0.5)  # Add small delay between client starts
        return client
    except Exception as e:
        print(f"{RED}{{failed - {str(e)}}}{RESET}")
        return None

def join_group(client, group_link):
    """Join a group using invite link or username"""
    try:
        phone = client.get_me().phone_number
        print(f"Joining group with {phone}...", end=" ")
        
        if group_link.startswith('https://t.me/'):
            identifier = group_link.split('/')[-1]
        else:
            identifier = group_link.lstrip('@')
        
        client.join_chat(identifier)
        print(f"{GREEN}{{joined}}{RESET}")
        time.sleep(2)  # Increased delay between joins
    except InviteHashExpired:
        print(f"{RED}{{failed - Invite link expired}}{RESET}")
    except UsernameNotOccupied:
        print(f"{RED}{{failed - Invalid username}}{RESET}")
    except FloodWait as e:
        print(f"{YELLOW}{{delayed - waiting {e.x}s}}{RESET}")
        time.sleep(e.x)
        try:
            client.join_chat(identifier)
            print(f"{GREEN}{{joined}}{RESET}")
        except:
            print(f"{RED}{{failed}}{RESET}")
    except Exception as e:
        print(f"{RED}{{failed - {str(e)}}}{RESET}")
    finally:
        time.sleep(1)  # Ensure delay after each join attempt
        
def read_chats(client, group_link):
    """Join a group using invite link or username"""
    # try:
    phone = client.get_me().phone_number
    print(f"Reading chats with {phone}...", end=" ")
    
    if group_link.startswith('https://t.me/'):
        identifier = group_link.split('/')[-1]
    else:
        identifier = group_link.lstrip('@')
    
    chat = client.get_chat(identifier)
    client.read_chat_history(chat.id)
    print(f"{GREEN}{chat.id}{RESET}")
    time.sleep(2)  # Increased delay between joins
    # except InviteHashExpired:
    #     print(f"{RED}{{failed - Invite link expired}}{RESET}")
    # except UsernameNotOccupied:
    #     print(f"{RED}{{failed - Invalid username}}{RESET}")
    # except FloodWait as e:
    #     print(f"{YELLOW}{{delayed - waiting {e.x}s}}{RESET}")
    #     time.sleep(e.x)
    #     try:
    #         client.join_chat(identifier)
    #         print(f"{GREEN}{{joined}}{RESET}")
    #     except:
    #         print(f"{RED}{{failed}}{RESET}")
    # except Exception as e:
    #     print(f"{RED}{{failed - {str(e)}}}{RESET}")
    # finally:
    #     time.sleep(1)  # Ensure delay after each join attempt

def send_message_with_status(client, target_username):
    """Send message and display status with color coding"""
    try:
        phone = client.get_me().phone_number
        print(f"Sending message from {phone} to @{target_username}...", end=" ")
        client.send_message(target_username, "Hello!")
        print(f"{GREEN}{{done}}{RESET}")
        time.sleep(2)  # Increased delay between messages
    except PeerIdInvalid:
        print(f"{RED}{{failed - Invalid username}}{RESET}")
    except FloodWait as e:
        print(f"{YELLOW}{{delayed - waiting {e.x}s}}{RESET}")
        time.sleep(e.x)
        try:
            client.send_message(target_username, "Hello!")
            print(f"{GREEN}{{done}}{RESET}")
        except:
            print(f"{RED}{{failed}}{RESET}")
    except Exception as e:
        print(f"{RED}{{failed - {str(e)}}}{RESET}")
    finally:
        time.sleep(1)  # Ensure delay after each message attempt

def process_clients(action, target):
    """Process all clients with proper cleanup"""
    clients = []
    accounts = load_accounts()

    # Login phase
    for account in accounts:
        print(f"Logging in to account: {account['phone']}", end=" ")
        client = login_to_telegram(account["phone"])
        if client:
            clients.append(client)
            print(f"{GREEN}{{Success}}{RESET}")
            time.sleep(1)  # Delay between logins

    # Action phase
    try:
        for client in clients:
            if action == "message":
                send_message_with_status(client, target)
            elif action == "join":
                join_group(client, target)
            elif action == "read_chats":
                read_chats(client, target)
    finally:
        # Cleanup phase
        for client in clients:
            try:
                client.stop()
            except:
                pass
            time.sleep(0.5)  # Delay between client stops

def main():
    """Main function to handle user input and operations"""
    while True:
        print("\nOptions:")
        print("1. Send message to user")
        print("2. Join group")
        print("3. Read chats")
        print("4. Exit")
        
        choice = input("Enter your choice (1-4): ")
        
        if choice == "1":
            target_username = input("Enter the username to send message (without @): ")
            process_clients("message", target_username)
        elif choice == "2":
            group_link = input("Enter group link or @ username: ")
            process_clients("join", group_link)
        elif choice == "3":
            group_link = input("Enter group link or @ username: ")
            process_clients("read_chats", group_link)
        elif choice == "4":
            print("Exiting program...")
            break
        else:
            print(f"{RED}Invalid choice. Please try again.{RESET}")

if __name__ == "__main__":
    main()