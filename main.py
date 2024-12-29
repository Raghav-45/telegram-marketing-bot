from pyrogram import Client
from pyrogram.errors import PeerIdInvalid, FloodWait
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
    client = Client(
        name=f"{SESSIONS_DIR}/session_{phone_number}",
        api_id=API_ID,
        api_hash=API_HASH,
        phone_number=phone_number
    )

    try:
        client.start()
        return client
    except Exception as e:
        print(f"Error logging in to {phone_number}: {e}")
        return None

def send_message_with_status(client, target_username):
    """Send message and display status with color coding"""
    try:
        phone = client.get_me().phone_number
        print(f"Sending message from {phone} to @{target_username}...", end=" ")
        client.send_message(target_username, "Hello!")
        print(f"{GREEN}{{done}}{RESET}")
        time.sleep(1)
    except PeerIdInvalid:
        print(f"{RED}{{failed - Invalid username}}{RESET}")
    except FloodWait as e:
        print(f"{YELLOW}{{delayed - waiting {e.x}s}}{RESET}")
        time.sleep(e.x)
        try:
            client.send_message(target_username, "Hello!")
            print(f"Sending message from {phone} to @{target_username}... {GREEN}{{done}}{RESET}")
        except:
            print(f"Sending message from {phone} to @{target_username}... {RED}{{failed}}{RESET}")
    except Exception as e:
        print(f"{RED}{{failed - {str(e)}}}{RESET}")

def send_hello_message(target_username):
    """Main function to handle client initialization and message sending"""
    clients = []
    accounts = load_accounts()

    # Initialize clients
    for account in accounts:
        print(f"Logging in to account: {account['phone']}", end=" ")
        client = login_to_telegram(account["phone"])
        if client:
            clients.append(client)
            print(f"{GREEN}{{Success}}{RESET}")

    # Send messages
    for client in clients:
        send_message_with_status(client, target_username)

if __name__ == "__main__":
    target_username = input("Enter the username you want to send 'Hello' to (without @): ")
    send_hello_message(target_username)