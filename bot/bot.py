import logging
import os
import random
from urllib.parse import urljoin

import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import DICE_SLOT_MACHINE
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

BASE_API_URL = os.getenv('API_BASE_URL')


def start(update: Update, context: CallbackContext) -> None:
    update.effective_message.reply_text('''
Привет! Здесь ты можешь поискать фильм на свой вкус 🎥
Для поиска введи /search + запрос
    ''')
    if animation_id := os.getenv('START_ANIMATION_ID'):
        update.effective_message.reply_animation(animation_id)


def search(update: Update, context: CallbackContext) -> None:
    query = update.effective_message.text.replace('/search', '').strip()
    if not query:
        update.effective_message.reply_text('Пожалуйста, введи поисковый запрос')
        return

    url = urljoin(BASE_API_URL, 'movies')
    response = requests.get(
        url,
        params={'search': query, 'limit': 4, 'page': 1},
        headers={'Content-Type': 'application/json'}
    )
    if not response.ok:
        logger.log(level=logging.ERROR, msg=f'{url} - {query} - {response.status_code} - {response.text}')
        update.effective_message.reply_text('Хьюстон, у нас проблемы! Пожалуйста, попробуй еще раз')
        return

    movies = response.json()
    if not movies:
        update.effective_message.reply_text('К сожалению, ничего не нашлось :( Попробуй поискать еще что-нибудь')
        return

    buttons = [
        [
            InlineKeyboardButton(
                text=f'{movie["title"]} IMDB: {movie["imdb_rating"]}',
                callback_data=f'show_movie_{movie["id"]}'
            )
        ] for movie in movies
    ]
    if len(buttons) > 1:
        buttons.append(
            [
                InlineKeyboardButton(text='Воля случая!', callback_data=f'random_{query}')
            ]
        )
    update.effective_message.reply_text(text='Вот что удалось найти 👇', reply_markup=InlineKeyboardMarkup(buttons))


def show_movie(update: Update, context: CallbackContext) -> None:
    movie_id = update.callback_query.data.replace('show_movie_', '')

    url = urljoin(urljoin(BASE_API_URL, 'movies/'), movie_id)
    response = requests.get(
        url,
        headers={'Content-Type': 'application/json'}
    )
    if not response.ok:
        logger.log(level=logging.ERROR, msg=f'{url} - {response.status_code} - {response.text}')
        update.effective_message.reply_text('Хьюстон, у нас проблемы! Пожалуйста, попробуй еще раз')
        return
    movie = response.json()
    message = '''
Название: {title} \n
Описание: {description} \n
IMDB rating: {imdb_rating} \n
Актеры: {actors} \n
Жанры: {genre} \n
Сценаристы: {writers} \n
Режисер: {director} \n
    '''.format(
        **movie
    )
    update.effective_message.reply_text(message)


def random_dice(update: Update, context: CallbackContext) -> None:
    update.effective_message.reply_dice(emoji=DICE_SLOT_MACHINE)
    # Последняя кнопка - Воля случая
    movies = update.effective_message.reply_markup.inline_keyboard[:-1]
    chosen_movie = random.choice(movies)
    update.effective_message.reply_text(
        'Я предлагаю посмотреть  👇',
        reply_markup=InlineKeyboardMarkup([chosen_movie]))


def oops(update: Update, context: CallbackContext) -> None:
    update.effective_message.reply_text('''
    Я не умею отвечать без команды :( Пожалуйста, используй /search запрос.
    ''')


def main():
    updater = Updater(os.getenv('TELEGRAM_API_TOKEN'))

    dispatcher = updater.dispatcher

    # регистрируем команды
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', start))
    dispatcher.add_handler(CommandHandler('search', search))

    # callbacks
    dispatcher.add_handler(CallbackQueryHandler(show_movie, pattern=r'^show_movie_\w+$'))
    dispatcher.add_handler(CallbackQueryHandler(random_dice, pattern=r'^random_\w+$'))

    # обработка простых текстовых сообщений
    dispatcher.add_handler(MessageHandler(Filters.all & ~Filters.command, oops))

    # Стартуем поллинг, еще метод - вебхук
    updater.start_polling()

    # Ждем до сигнала прерывания
    updater.idle()


if __name__ == '__main__':
    main()
