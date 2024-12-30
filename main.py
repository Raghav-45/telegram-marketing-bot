from pyrogram import Client, filters
from pyrogram.errors import PeerIdInvalid, FloodWait, InviteHashExpired, UsernameNotOccupied
import time

# Constants
API_ID = 954660
API_HASH = "722f3cedf17305b3955a545b28b53995"
BOT_TOKEN = "6652489556:AAFfNjVvXEOwVqLBulDpSvMQfmSgYVf-44U"  # Replace with your bot token

# Color codes for status messages
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# Initialize the bot
bot = Client(
    name="my_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@bot.on_message(filters.command("start"))
def start_command(client, message):
    """Handle the /start command"""
    message.reply("Welcome! I'm your bot. Use /sendmessage <username> to send a message, or /joingroup <link or username> to join a group.")
    
@bot.on_message(filters.command("sendmessage"))
def send_message(client, message):
    """Handle the /sendmessage command"""
    try:
        # Extract username from the command
        target_username = message.text.split(" ", 1)[1].lstrip('@')
        print(f"Sending message to @{target_username}...", end=" ")
        bot.send_message(target_username, "Hello!")
        message.reply(f"{GREEN}Message sent to @{target_username}!{RESET}")
    except IndexError:
        message.reply("Please provide a username after the command.")
    except PeerIdInvalid:
        message.reply("Invalid username. Could not send message.")
    except FloodWait as e:
        message.reply(f"{YELLOW}Delayed - waiting {e.x}s...{RESET}")
        time.sleep(e.x)
        try:
            bot.send_message(target_username, "Hello!")
            message.reply(f"{GREEN}Message sent to @{target_username}!{RESET}")
        except:
            message.reply(f"{RED}Failed to send message.{RESET}")
    except Exception as e:
        message.reply(f"Error: {str(e)}")

# def send_message_with_status(bot, target_username):
#     """Send message and display status with color coding"""
#     try:
#         print(f"Sending message to @{target_username}...", end=" ")
#         bot.send_message(target_username, "Hello!")
#         print(f"{GREEN}{{done}}{RESET}")
#     except PeerIdInvalid:
#         print(f"{RED}{{failed - Invalid username}}{RESET}")
#     except FloodWait as e:
#         print(f"{YELLOW}{{delayed - waiting {e.x}s}}{RESET}")
#         time.sleep(e.x)
#         try:
#             bot.send_message(target_username, "Hello!")
#             print(f"{GREEN}{{done}}{RESET}")
#         except:
#             print(f"{RED}{{failed}}{RESET}")
#     except Exception as e:
#         print(f"{RED}{{failed - {str(e)}}}{RESET}")

# def join_group(bot, group_link):
#     """Join a group using invite link or username"""
#     try:
#         print(f"Joining group...", end=" ")
        
#         if group_link.startswith('https://t.me/'):
#             identifier = group_link.split('/')[-1]
#         else:
#             identifier = group_link.lstrip('@')
        
#         bot.join_chat(identifier)
#         print(f"{GREEN}{{joined}}{RESET}")
#     except InviteHashExpired:
#         print(f"{RED}{{failed - Invite link expired}}{RESET}")
#     except UsernameNotOccupied:
#         print(f"{RED}{{failed - Invalid username}}{RESET}")
#     except FloodWait as e:
#         print(f"{YELLOW}{{delayed - waiting {e.x}s}}{RESET}")
#         time.sleep(e.x)
#         try:
#             bot.join_chat(identifier)
#             print(f"{GREEN}{{joined}}{RESET}")
#         except:
#             print(f"{RED}{{failed}}{RESET}")
#     except Exception as e:
#         print(f"{RED}{{failed - {str(e)}}}{RESET}")

def main():
    """Main function to handle user input and operations"""
    bot.run()

        # while True:
        #     print("\nOptions:")
        #     print("1. Send message to user")
        #     print("2. Join group")
        #     print("3. Exit")
            
        #     choice = input("Enter your choice (1-3): ")
            
        #     if choice == "1":
        #         target_username = input("Enter the username to send message (without @): ")
        #         send_message_with_status(bot, target_username)
        #     elif choice == "2":
        #         group_link = input("Enter group link or @ username: ")
        #         join_group(bot, group_link)
        #     elif choice == "3":
        #         print("Exiting program...")
        #         break
        #     else:
        #         print(f"{RED}Invalid choice. Please try again.{RESET}")

if __name__ == "__main__":
    main()