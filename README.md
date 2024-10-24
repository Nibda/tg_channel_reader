**ОПИС**

Парсить телеграм канал (включаючи обговорення у чатах) на наявність повідомлень по ключовим словам. Коли повідмлення містить ключове слово, таке повідомлення надсилається на вказаний контакт. 

**ВСТАНОВЛЕННЯ**

Для роботи потрітно встановити модуль Telethon.
Це можна зробити командою
`pip install telethon` або `pip install -r requirements.txt`

**CREDENTIALS**

Для роботи необхідно заповнити файл `config.ini`, а саме:

```
[Telegram]
api_id = get it here https://my.telegram.org/auth?to=apps
api_hash = get it here https://my.telegram.org/auth?to=apps
phone = +380
username = TgUsername
send_to = +380

[Credentials]
keywords = список ключових слів через пробіл
channels = https://t.me/any_channel (можна включити декілька каналів через пробіл)
timestamp = 
```

**CRON**

Для того щоб програма запускалася пероідично і автоматично можна налаштувати задачу в cron через команду 

`crontab -e`

Наприклад, для того щоб скрипт запускався кожних 15 хв. пишемо 

`*/15 * * * *`



