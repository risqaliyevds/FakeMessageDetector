from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from static.texts import OFERTA, OFERTA_AGREE

# Agreement Inline Markup
agreement_markup = InlineKeyboardMarkup()
button_agreement = InlineKeyboardButton('Roziman ✅', callback_data = 'agree')
agreement_markup.add(button_agreement)