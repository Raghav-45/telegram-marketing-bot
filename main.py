from pyrogram import Client
from pyrogram.errors import PeerIdInvalid, FloodWait
import time
import csv
import os

api_id = 954660
api_hash = "722f3cedf17305b3955a545b28b53995"

if not os.path.exists("sessions"):
    os.makedirs("sessions")

def load_accounts():
    accounts = []
    try:
        with open('accounts.csv', 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)
            for row in csv_reader:
                if row:
                    phone = row[0].strip()
                    if phone.startswith('91'):
                        accounts.append({"phone": phone})
                    else:
                        accounts.append({"phone": f"91{phone}"})
        return accounts
    except FileNotFoundError:
        print("accounts.csv not found. Creating a sample file...")
        with open('accounts.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['phone'])
            writer.writerow(['9315988300'])
        return [{'phone': '919315988300'}]

def login_to_telegram(phone_number):
    client = Client(
        name=f"sessions/session_{phone_number}",
        api_id=api_id,
        api_hash=api_hash,
        phone_number=phone_number
    )

    try:
        client.start()
        return client
    except Exception as e:
        print(f"Error logging in to {phone_number}: {e}")
        return None

def send_hello_message(target_username):
    clients = []
    accounts = load_accounts()

    for account in accounts:
        print(f"Logging in to account: {account['phone']}")
        client = login_to_telegram(account["phone"])
        if client:
            clients.append(client)
            print(f"Successfully logged in to {account['phone']}")

    for client in clients:
        try:
            phone = client.get_me().phone_number
            print(f"Sending message from {phone} to @{target_username}...", end=" ")
            client.send_message(target_username, "Hello!")
            print("\033[92m{done}\033[0m")  # Green color for success
            time.sleep(1)
        except PeerIdInvalid:
            print("\033[91m{failed - Invalid username}\033[0m")  # Red color for failure
        except FloodWait as e:
            print(f"\033[93m{{delayed - waiting {e.x}s}}\033[0m")  # Yellow for delay
            time.sleep(e.x)
            try:
                client.send_message(target_username, "Hello!")
                print(f"Sending message from {phone} to @{target_username}... \033[92m{done}\033[0m")
            except:
                print(f"Sending message from {phone} to @{target_username}... \033[91m{failed}\033[0m")
        except Exception as e:
            print(f"\033[91m{{failed - {str(e)}}}\033[0m")  # Red color with error message

if __name__ == "__main__":
    target_username = input("Enter the username you want to send 'Hello' to (without @): ")
    send_hello_message(target_username)