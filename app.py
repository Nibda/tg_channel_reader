import pytz
import configparser
from datetime import datetime, timedelta
from telethon.sync import TelegramClient

# Reading Configs
config = configparser.ConfigParser()
config.read("config.ini", encoding='utf-8')

# Setting configuration values
telegram = config['Telegram']
api_id = telegram['api_id']
api_hash = telegram['api_hash']
phone = telegram['phone']
username = telegram['username']
send_to = telegram['send_to']

creds = config['Credentials']
keywords = creds['keywords'].split(' ')
channels = creds['channels'].split(' ')
timestamp_format = '%Y-%m-%d %H:%M:%S.%f'

# Завантаження або встановлення значень дати за замовчуванням для message_timestamp і comment_timestamp
default_time = datetime.now(pytz.timezone('Europe/Kyiv')).strftime(timestamp_format)
timestamp_str = creds.get('message_timestamp', default_time)
comment_timestamp_str = creds.get('comment_timestamp', default_time)

# Конвертація строк в datetime з часовим поясом
last_timestamp_obj = datetime.strptime(timestamp_str, timestamp_format).replace(tzinfo=pytz.timezone('Europe/Kyiv'))
last_comment_timestamp_obj = datetime.strptime(comment_timestamp_str, timestamp_format).replace(tzinfo=pytz.timezone('Europe/Kyiv'))

# Створення клієнта Telegram
client = TelegramClient(username, api_id, api_hash)
client.start()

def main(channel):
    global last_timestamp_obj, last_comment_timestamp_obj
    new_last_message_time = last_timestamp_obj
    new_last_comment_time = last_comment_timestamp_obj

    # Ітерація по повідомленням
    for message in client.iter_messages(channel, limit=5, reverse=True, offset_date=last_timestamp_obj):
        
        message_datetime = message.date.astimezone(pytz.timezone('Europe/Kyiv'))

        # Оновлення останнього часу повідомлення, якщо воно пізніше попереднього
        if message_datetime > new_last_message_time:
            new_last_message_time = message_datetime

        if message.text and message.text[0].isalnum():
            message_text = message.text.replace('\n', ' ')
            print(f"{message_datetime} {message.id} {message_text}")
            for word in keywords:
                if word in message.text.lower():
                    client.send_message(send_to, message.text)

            # Читання коментарів
            for comment in client.iter_messages(channel, reply_to=message.id, reverse=True, offset_date=last_comment_timestamp_obj):
                comment_datetime = comment.date.astimezone(pytz.timezone('Europe/Kyiv'))

                # Пропустити коментар, якщо його дата менша за last_comment_timestamp_obj
                if comment_datetime <= last_comment_timestamp_obj:
                    continue

                # Оновлення останнього часу коментаря, якщо він новіший
                if comment_datetime > new_last_comment_time:
                    new_last_comment_time = comment_datetime

                print(f"{comment_datetime} {comment.id} {comment.text}")
                for word in keywords:
                    if word in comment.text.lower():
                        client.send_message(send_to, 
                            f"{comment_datetime} {comment.text} {channel}/{message.id}?comment={comment.id}")

    # Повернення нових значень часу для збереження
    return new_last_message_time, new_last_comment_time

# Функція для збереження конфігурації
def update_config(timestamp, comment_timestamp):
    creds['message_timestamp'] = timestamp.strftime(timestamp_format)
    creds['comment_timestamp'] = comment_timestamp.strftime(timestamp_format)
    with open('config.ini', 'w') as config_file:
        config.write(config_file)

# Головний процес
for channel in channels:
    new_last_message_time, new_last_comment_time = main(channel)

# Оновлення timestamp після обробки всіх каналів
update_config(new_last_message_time, new_last_comment_time)

# Закриття клієнта
client.disconnect()
