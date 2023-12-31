from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import (
    InputPeerEmpty,
    UserStatusLastWeek,
    UserStatusOnline,
    UserStatusRecently,
    ChannelParticipantsAdmins,
)

from telethon.tl.types import InputPeerEmpty
import os, sys
import configparser
import csv
import time
import json
from datetime import date, datetime,timedelta


re="\033[1;31m"
gr="\033[1;32m"
cy="\033[1;36m"

def banner():
    print(f"""
{re}╔╦╗{cy}┌─┐┬  ┌─┐{re}╔═╗  ╔═╗{cy}┌─┐┬─┐┌─┐┌─┐┌─┐┬─┐
{re} ║ {cy}├┤ │  ├┤ {re}║ ╦  ╚═╗{cy}│  ├┬┘├─┤├─┘├┤ ├┬┘
{re} ╩ {cy}└─┘┴─┘└─┘{re}╚═╝  ╚═╝{cy}└─┘┴└─┴ ┴┴  └─┘┴└─

            version : 3.1
youtube.com/channel/UCnknCgg_3pVXS27ThLpw3xQ
        """)

cpass = configparser.RawConfigParser()
cpass.read('config.data')

phone_number = sys.argv[1]


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
    
    if len(sys.argv) > 3 and sys.argv[3] in ['-s', '--signin']:
            # print("Enter the code2")
            # banner()
            code = input()
            client.sign_in(phone, code)
    else:
        print("Enter the code")
        sys.exit(1)
 
# os.system('clear')
# banner()
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
 
# print(gr+'[+] Choose a group to scrape members :'+re)
# i=0
# for g in groups:
#     print(gr+'['+cy+str(i)+gr+']'+cy+' - '+ g.title)
#     i+=1
 
# print('')

if len(sys.argv) > 2 and sys.argv[2] in ['--listing', '-l']:
    groups_data = []
    for group in groups:
        group_info = {
            'id': group.id,
            'title': getattr(group, 'title', "Null"),
            'access_hash': getattr(group, 'access_hash', "Null")
        }
        groups_data.append(group_info)

    print(json.dumps(groups_data))
    sys.exit(0)
    
    
admin_only = False
if len(sys.argv) > 2 and sys.argv[2] in ['--admins', '-a']:
    admin_only = True

    
    
    
g_index = input()
target_group=groups[int(g_index)]
 
# print(gr+'[+] Fetching Members...')
time.sleep(1)
all_participants = []
all_participants = client.get_participants(target_group, aggressive=True)
 
# print(gr+'[+] Saving In file...')
time.sleep(1)

admin_ids = set()
if admin_only:
    admins = client.get_participants(target_group, filter=ChannelParticipantsAdmins())
    admin_ids = {admin.id for admin in admins}

    
admin_ids = set()
if admin_only:
    admins = client.get_participants(target_group, filter=ChannelParticipantsAdmins())
    admin_ids = {admin.id for admin in admins}

with open("members.csv", "w", encoding='UTF-8') as f:
    writer = csv.writer(f, delimiter=",", lineterminator="\n")
    writer.writerow(['username', 'user id', 'access hash', 'name', 'group', 'group id'])

    for user in all_participants:
        if admin_only and user.id not in admin_ids:
            continue  # Skip non-admins if admin_only is True

        accept = True
        if not admin_only:
            try:
                lastDate = user.status.was_online
                # time_difference = datetime.now() - lastDate
                # if time_difference > timedelta(days=15):
                #     accept = False
        
                num_months = (datetime.now().year - lastDate.year) * 12 + (datetime.now().month - lastDate.month)
                if num_months > 0.07:
                    accept = False
            except:
                continue

        if accept:
            username = user.username if user.username else ""
            first_name = user.first_name if user.first_name else ""
            last_name = user.last_name if user.last_name else ""
            name = (first_name + ' ' + last_name).strip()
            writer.writerow([username, user.id, user.access_hash, name, target_group.title, target_group.id])

print('[+] Members scraped successfully.')