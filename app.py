import pytz
import configparser
from datetime import datetime
from telethon import TelegramClient

# Reading Configs
config = configparser.ConfigParser()
config.read("config.ini", encoding='utf-8')

# Setting configuration values
telegram    = config['Telegram']
api_id      = telegram['api_id']
api_hash    = telegram['api_hash']
phone       = telegram['phone']
username    = telegram['username']
send_to     = telegram['send_to']

creds = config['Credentials']
keywords = creds['keywords'].split(' ')
channels = creds['channels'].split(' ')
timestamp_str = creds['timestamp']
timestamp_format = '%Y-%m-%d %H:%M:%S.%f'
last_timestamp_obj = datetime.strptime(timestamp_str, timestamp_format)

# Create the client and connect
client = TelegramClient(username, api_id, api_hash)
async def main(channel):
    async for message in client.iter_messages(channel):
        message_datetime = message.date.astimezone(pytz.timezone('Europe/Kyiv'))
        if  message.text and message_datetime.timestamp() > last_timestamp_obj.timestamp() \
            and message.text[0].isalnum():
            message_text = message.text.replace('\n', ' ') # set message in single string
            print(f"{message_datetime} {message.id} {message_text}")
            for word in keywords:
                if word in message.text.lower():
                    await client.send_message(send_to, message.text)
            # read comments
            try:
                async for comment in client.iter_messages(channel, reply_to=message.id):
                    print(f"{comment.date.astimezone(pytz.timezone('Europe/Kyiv'))}{comment.id} {comment.text}")
                    for word in keywords:
                        if word in comment.text.lower():
                            await client.send_message(send_to, 
                                f"{comment.date.astimezone(pytz.timezone('Europe/Kyiv'))} \
                                {comment.text} {channel}/{message.id}?comment={comment.id}")
            # catching exceptions that arise when the administrator deleted a comment in the group 
            except telethon.errors.rpcerrorlist.MsgIdInvalidError:
                print("Comment deleted by the administrator. Passed")

with client:
    for channel in channels:
        client.loop.run_until_complete(main(channel))

creds['timestamp'] = str(datetime.now())
with open('config.ini', 'w') as config_file:
    config.write(config_file)
