import psycopg2
import torch
import langid
from utils.config_utils import MODEL_MESSAGE
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import logging
logging.set_verbosity_error()

class TextMessagePredictor:
    def __init__(self, text):
        self.text = text
        self.tokenizer = AutoTokenizer.from_pretrained('rifkat/uztext-3Gb-BPE-Roberta')
        self.device = torch.device('cpu')

    def text_cleaner(self):
        # Define language
        lang, _ = langid.classify(self.text)
        if lang == 'ru':
            return None
        edited_text = re.sub(r'[а-яА-ЯёЁ]+', '', self.text)
        edited_text = re.sub(r'\d+', '', edited_text)
        edited_text = re.sub(r'[^\w\s]', '', edited_text)
        edited_text = re.sub(r'\s+', ' ', edited_text)
        return edited_text.lower()

    def model_loader(self):
        model = AutoModelForSequenceClassification.from_pretrained('rifkat/uztext-3Gb-BPE-Roberta', num_labels=2)
        model.load_state_dict(torch.load(MODEL_MESSAGE, map_location=torch.device('cpu')))
        return model.to(self.device)

    def predictor(self):
        text_cleaned = self.text_cleaner()
        if text_cleaned:
            inputs = self.tokenizer(text_cleaned, padding=True, truncation=True, return_tensors='pt', max_length=512).to(self.device)
            model = self.model_loader()
            outputs = model(**inputs)

            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            predicted_label = predictions.argmax().item()
            predicted_prob = predictions[0][predictions.argmax().item()].item()
            return predicted_label, predicted_prob
        return None

import re

class ExtractURL:
    def __init__(self, message, text):
        self.message = message
        self.text = text
        self.urls = set()

    def url_from_text(self, text):
        url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        urls = re.findall(url_pattern, text)
        return set(urls)

    def get_urls(self):
        str_message = str(self.message)
        urls_from_text = self.url_from_text(self.text)
        urls_from_message = self.url_from_text(str_message)
        return self.urls.union(urls_from_text, urls_from_message)

class SendMessageAllUser:
    def __init__(self, db_params, bot,  text):
        self.text = text
        self.bot = bot
        self.db_params = db_params

    async def get_user_agreement_date(self):
        conn = psycopg2.connect(**self.db_params)
        c = conn.cursor()
        c.execute(f"SELECT user_id FROM users")
        chats = c.fetchall()
        conn.close()
        return chats

    async def send_message(self):
        chats = await self.get_user_agreement_date()
        for chat in chats:
            await self.bot.send_message(chat_id=chat[0], text= self.text[11:])


