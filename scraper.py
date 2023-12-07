from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
import os, sys
import configparser
import csv
import time
import json

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

try:
    api_id = cpass['cred']['id']
    api_hash = cpass['cred']['hash']
    phone = cpass['cred']['phone']
    client = TelegramClient(phone, api_id, api_hash)
except KeyError:
    
    # banner()
    print(re+"[!] run python3 setup.py first !!\n")
    sys.exit(1)

client.connect()
# if not client.is_user_authorized():
#     client.send_code_request(phone)
    
#     # banner()
#     client.sign_in(phone, input(gr+'[+] Enter the code: '+re))

if not client.is_user_authorized():
    
    client.send_code_request(phone)
    
    if len(sys.argv) > 2 and sys.argv[2] in ['-s', '--signin']:
            # print("Enter the code2")
            # banner()
            code = input()
            client.sign_in(phone, code)
    else:
        print("Enter the code")
        sys.exit(1)

 

 

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
i=0
# for g in groups:
#     print(gr+'['+cy+str(i)+gr+']'+cy+' - '+ g.title)
#     i+=1

# print("ok")

def test_groups():
    with open("groups.csv","w",encoding='UTF-8') as f:
        writer = csv.writer(f,delimiter=",",lineterminator="\n")
        writer.writerow(['title'])
        for g in groups:
            if g.title:
                title= g.title
            else:
                title= ""
            writer.writerow([title])
    
 

# if any ([sys.argv[1] == '--listing', sys.argv[1] == '-l']):
#     groups_data = []
#     for group in groups:
#             # Extract necessary attributes from each group
#             group_info = {
#                 'id': group.id,
#                 'title': getattr(group, 'title', None),
#                 'access_hash': getattr(group, 'access_hash', None)
#                 # You can add more attributes here if needed
#             }
#             groups_data.append(group_info)

#     print(json.dumps(groups_data))
#     sys.exit(1)

# Check if any command-line arguments are passed
if len(sys.argv) > 1 and sys.argv[1] in ['--listing', '-l']:
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

g_index = input()
target_group=groups[int(g_index)]


 
# print(gr+'[+] Fetching Members...')
time.sleep(1)
all_participants = []
all_participants = client.get_participants(target_group, aggressive=True)
 
# print(gr+'[+] Saving In file...')
time.sleep(1)




with open("members.csv","w",encoding='UTF-8') as f:
    writer = csv.writer(f,delimiter=",",lineterminator="\n")
    writer.writerow(['username','user id', 'access hash','name','group', 'group id'])
    for user in all_participants:
        if user.username:
            username= user.username
        else:
            username= ""
        if user.first_name:
            first_name= user.first_name
        else:
            first_name= ""
        if user.last_name:
            last_name= user.last_name
        else:
            last_name= ""
        name= (first_name + ' ' + last_name).strip()
        writer.writerow([username,user.id,user.access_hash,name,target_group.title, target_group.id])
print(gr+'[+] Members scraped successfully.')



