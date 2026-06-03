import requests
from config.telegram_settings import TOKEN, CHAT_ID, URL
from notification.notifier_interface import INotifier

class TelegramNotifier(INotifier):
    def __init__(self):
        self.token = TOKEN
        self.chat_id = CHAT_ID
        self.url = URL

    def notify(self, message: str):
        data = {
            "chat_id": self.chat_id,
            "text": message
        }
        response = requests.post(self.url, data=data)
        if response.status_code == 200:
            print("Message sent successfully")
        else:
            print("Error:", response.text)