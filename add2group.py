#!/bin/env python3
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, InputPeerUser
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError,FloodWaitError
from telethon.tl.functions.channels import InviteToChannelRequest
import configparser
import os, sys
import csv
import traceback
import time
import random
import logging
import json



re="\033[1;31m"
gr="\033[1;32m"
cy="\033[1;36m"

def banner():
    print(f"""
{re}╔╦╗{cy}┌─┐┬  ┌─┐{re}╔═╗  ╔═╗{cy}┌─┐┬─┐┌─┐┌─┐┌─┐┬─┐
{re} ║ {cy}├┤ │  ├┤ {re}║ ╦  ╚═╗{cy}│  ├┬┘├─┤├─┘├┤ ├┬┘
{re} ╩ {cy}└─┘┴─┘└─┘{re}╚═╝  ╚═╝{cy}└─┘┴└─┴ ┴┴  └─┘┴└─

            version : 1.0
        """)

cpass = configparser.RawConfigParser()
cpass.read('config.data')
phone_number = sys.argv[1]

# Set up the logging configuration
logging.basicConfig(filename= phone_number+'.log', level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')



def get_credentials(phone_number):
    # Read credentials from the JSON file
    try:
        with open('credentials.json', 'r') as f:
            credentials = json.load(f)
    except FileNotFoundError:
        print("Credentials file not found.")
        sys.exit(1)

    # Retrieve credentials for the provided phone number
    user_credentials = credentials.get(phone_number, None)

    if user_credentials is None:
        print(f"Credentials not found for phone number: {phone_number}")
        sys.exit(1)

    return user_credentials

try:
    # api_id = cpass['cred']['id']
    # api_hash = cpass['cred']['hash']
    # phone = cpass['cred']['phone']
    creds = get_credentials(phone_number)
    api_id = creds['id']
    api_hash = creds['hash']
    phone = creds['phone']
    client = TelegramClient(phone, api_id, api_hash)
except KeyError:
    os.system('clear')
    banner()
    print(re+"[!] run python3 setup.py first !!\n")
    sys.exit(1)

client.connect()
if not client.is_user_authorized():
    client.send_code_request(phone)
    # os.system('clear')
    # banner()
    client.sign_in(phone, input())
 
# os.system('clear')
# banner()
input_file = sys.argv[2]

users = []
with open(input_file, encoding='UTF-8') as f:
    rows = csv.reader(f,delimiter=",",lineterminator="\n")
    next(rows, None)
    for row in rows:
        user = {}
        user['username'] = row[0]
        user['id'] = int(row[1])
        user['access_hash'] = int(row[2])
        user['name'] = row[3]
        users.append(user)
 
chats = []
last_date = None
chunk_size = 200
groups=[]
 
result = client(GetDialogsRequest(
             offset_date=last_date,
             offset_id=0,
             offset_peer=InputPeerEmpty(),
             limit=chunk_size,
             hash = 0
         ))
chats.extend(result.chats)
 
for chat in chats:
    try:
        if chat.megagroup== True:
            groups.append(chat)
    except:
        continue
 
# i=0
# for group in groups:
#     print(gr+'['+cy+str(i)+gr+']'+cy+' - '+group.title)
#     i+=1

# print(gr+'[+] Choose a group to add members')
g_index = input()
target_group=groups[int(g_index)]
 
target_group_entity = InputPeerChannel(target_group.id,target_group.access_hash)
 
# print(gr+"[1] add member by user ID\n[2] add member by username ")
# mode = int(input()) 
n = 0
mode = 2
msg = ''
stop_runing = False


for user in users:
    n += 1
    if stop_runing:
        logging.info(msg)
        sys.exit(0)

    if n % 50 == 0:
        time.sleep(5)
        try:
            if mode == 1:
                if user['username'] == "":
                    continue
                user_to_add = client.get_input_entity(user['username'])
            elif mode == 2:
                user_to_add = InputPeerUser(user['id'], user['access_hash'])
            else:
                sys.exit(re + "[!] Invalid Mode Selected. Please Try Again.")
            
            client(InviteToChannelRequest(target_group_entity, [user_to_add]))
            time.sleep(random.randrange(50, 90))
        except PeerFloodError:
            logging.warning("[!] Peer flood error.")
            continue
        except UserPrivacyRestrictedError:
            logging.warning("[!] The user's privacy settings do not allow you to do this. Skipping.")
            continue
        except FloodWaitError:
            msg = "this account has flood wait error, wait for at least 24 hours to use it again"
            stop_runing = True
            logging.error(msg)
        except Exception as e:
            logging.exception("[!] Unexpected Error: %s", e)
            continue
 
# for user in users:
#     n += 1
#     if stop_runing:
#         print(msg)
#         sys.exit(0)
        
#     if n % 50 == 0:
#         time.sleep(5)
#         try:
#             # print ("Adding {}".format(user['id']))
#             if mode == 1:
#                 if user['username'] == "":
#                     continue
#                 user_to_add = client.get_input_entity(user['username'])
#             elif mode == 2:
#                 user_to_add = InputPeerUser(user['id'], user['access_hash'])
#             else:
#                 sys.exit(re + "[!] Invalid Mode Selected. Please Try Again.")
#             client(InviteToChannelRequest(target_group_entity, [user_to_add]))
#             # print(gr + "[+] Waiting for 5-10 Seconds...")
#             time.sleep(random.randrange(20, 50))
#         except PeerFloodError:
#             # print(re + "[!] peer flood error.")
#             print("")
#             # continue
#         except UserPrivacyRestrictedError:
#             # print(re + "[!] The user's privacy settings do not allow you to do this. Skipping.")
#             # continue
#             print("")
#         except FloodWaitError:
#             msg = "this account has flood wait error, wait for at least 24 hours to use it again"
#             stop_runing = True
#             print(msg)
#         except:
#             # traceback.print_exc()
#             # print(re + "[!] Unexpected Error")
#             continue
