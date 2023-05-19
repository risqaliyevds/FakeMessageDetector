from aiogram import Bot, Dispatcher, types, executor
from keyboards import agreement_markup
from aiogram.types import ContentTypes
from config.config import BOT_TOKEN, DB_PARAMS, ADMIN
from static.texts import *
from utils.func_database import *
from utils.func_text_message import *

bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'], content_types=['text'])
async def start_message(message: types.Message):
    if DataBaseUserSaver(DB_PARAMS, message).user_exists():
        date = DataBaseUserSaver(DB_PARAMS, message).get_user_agreement_date()
        date_str = date[0].strftime("%Y-%m-%d")
        await bot.send_message(message.from_user.id,
                               text= OFERTA_AGREE_EXIST + f'<b>{date_str} </b>✅.',
                               parse_mode='HTML',
                               disable_web_page_preview = True)
        await bot.send_message(message.from_user.id, ACCESS)
        await bot.send_message(message.from_user.id, USE_MESSAGE)

    else:
        await bot.send_message(message.from_user.id,
                               text=OFERTA,
                               reply_markup=agreement_markup,
                               parse_mode='HTML',
                               disable_web_page_preview = True)

@dp.callback_query_handler()
async def agreement_callback(callback: types.CallbackQuery):
    await callback.message.edit_text(OFERTA_AGREE, parse_mode= 'HTML',
                                     disable_web_page_preview = True)
    await bot.send_message(callback.from_user.id, ACCESS)
    await bot.send_message(callback.from_user.id, USE_MESSAGE)
    DataBaseUserSaver(DB_PARAMS, callback).insert_user()

@dp.message_handler(commands=['adminmryu'], content_types=['text'])
async def send_message_all(message: types.Message):
    if message.from_user.id == ADMIN:
        await SendMessageAllUser(DB_PARAMS, bot, message.text).send_message()
    else:
        await bot.send_message(message.from_user.id, 'Siz admin emassiz!')

@dp.message_handler(content_types= ContentTypes.all())
async def get_user_message(message):
    if not DataBaseUserSaver(DB_PARAMS, message).user_exists():
        await bot.send_message(message.from_user.id, REJECT_BEFORE_AGREEMENT)
    if message.caption or message.text:
        text = message.caption if message.caption else message.text
        urls = ExtractURL(message, text).get_urls()
        response = TextMessagePredictor(text).predictor()
        if response:
            predicted_label, predicted_prob = response
            if predicted_label:
                await bot.send_message(message.from_user.id, SUSPICIOUS_TEXT + WARNING, parse_mode='HTML')
            else:
                await bot.send_message(message.from_user.id, NORMAL_TEXT + WARNING, parse_mode='HTML')
            await DataBaseTextSaver(DB_PARAMS, message, text, predicted_label).save_from_users()
            await DatabaseUrl(DB_PARAMS, urls).insert_urls()

        else:
            await bot.send_message(message.from_user.id, XABAR_MATNI_XATO)
    else:
        await bot.send_message(message.from_user.id, XABAR_MATNI_XATO)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)