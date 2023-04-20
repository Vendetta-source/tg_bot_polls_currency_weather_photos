from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode
from aiogram.utils import executor, deep_linking

from services.weather import Weather
from services.currency import Currency
from services.photos import AnimalsPhotos
from utils.polls import Poll
from config import BOT_TOKEN, WEATHER_API_KEY, EXCHANGE_API_KEY, PHOTOS_API_KEY

# Инициализация бота
storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)

weather_instance = Weather(WEATHER_API_KEY)
currency_instance = Currency(EXCHANGE_API_KEY)
photos_instance = AnimalsPhotos(PHOTOS_API_KEY)

polls_database = {}  # здесь хранится информация об опросах
polls_owners = {}  # здесь хранятся пары "id опроса <—> id её создателя"


# Обработка команды /start
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    """
    Обработка команды /start. Приветствие пользователя и предложение выбрать
    действие.
    """
    if message.chat.type == types.ChatType.PRIVATE:
        keyboard_markup = types.ReplyKeyboardMarkup(row_width=2,
                                                    resize_keyboard=True)
        weather_button = types.KeyboardButton('/weather')
        currency_button = types.KeyboardButton('/currency')
        animal_button = types.KeyboardButton('/animal')
        poll_button = types.KeyboardButton(
            text="Создать опрос",
            request_poll=types.KeyboardButtonPollType(
                type=types.PollType.REGULAR
            )
        )
        keyboard_markup.add(
            weather_button,
            currency_button,
            animal_button,
            poll_button
        )
        await message.reply('Привет! Что вы хотите сделать?',
                            reply_markup=keyboard_markup)
    else:
        words = message.text.split()
        # Только команда /start без параметров. В этом случае отправляем в
        # личку с ботом.
        if len(words) == 1:
            # Получаем информацию о боте
            bot_info = await bot.get_me()
            # Создаём клавиатуру с URL-кнопкой для перехода в ЛС
            keyboard = types.InlineKeyboardMarkup()
            move_to_dm_button = types.InlineKeyboardButton(
                text='Перейти в ЛС',
                url=f't.me/{bot_info.username}?start=anything'
            )
            keyboard.add(move_to_dm_button)
            await message.reply(
                'Не выбран ни один опрос. Пожалуйста, перейдите в личные '
                'сообщения с ботом,'
                'чтобы создать новый.', reply_markup=keyboard)
        # Если у команды /start или /startgroup есть параметр, то это,
        # скорее всего, ID опроса. Проверяем и отправляем.
        else:
            poll_owner = polls_owners.get(words[1])
            if not poll_owner:
                await message.reply(
                    'Опрос удален, недействителен или уже запущен в другой '
                    'группе. Попробуйте создать новый.')
                return
            # Проходим по всем сохранённым опросам от конкретного user ID
            for saved_poll in polls_database[poll_owner]:
                # Нашли нужный опрос, отправляем его.
                if saved_poll.poll_id == words[1]:
                    msg = await bot.send_poll(chat_id=message.chat.id,
                                              question=saved_poll.question,
                                              is_anonymous=False,
                                              options=saved_poll.options)
                    # ID опроса при отправке уже другого, создаём запись.
                    polls_owners[msg.poll.id] = poll_owner
                    # Старую запись удаляем.
                    del polls_owners[words[1]]
                    # В "хранилище" опросов тоже меняем ID опроса на новый
                    saved_poll.poll_id = msg.poll.id
                    # ... а также сохраняем chat_id ...
                    saved_poll.chat_id = msg.chat.id
                    # ... и message_id для последующего закрытия викторины.
                    saved_poll.message_id = msg.message_id


# Обработчик любых инлайн-запросов
@dp.inline_handler()
async def inline_query(query: types.InlineQuery):
    results = []
    user_polls = polls_database.get(str(query.from_user.id))
    if user_polls:
        for poll in user_polls:
            keyboard = types.InlineKeyboardMarkup()
            start_poll_button = types.InlineKeyboardButton(
                text="Отправить в группу",
                url=await deep_linking.get_startgroup_link(poll.poll_id)
            )
            keyboard.add(start_poll_button)
            results.append(types.InlineQueryResultArticle(
                id=poll.poll_id,
                title=poll.question,
                input_message_content=types.InputTextMessageContent(
                    message_text='Нажмите кнопку ниже, чтобы отправить опрос '
                                 'в группу.'),
                reply_markup=keyboard
            ))
    await query.answer(switch_pm_text='Создать опрос', switch_pm_parameter="_",
                       results=results, cache_time=10, is_personal=True)


@dp.message_handler(content_types=['poll'])
async def msg_with_poll(message: types.Message):
    # Если юзер раньше не присылал запросы, выделяем под него запись
    if not polls_database.get(str(message.from_user.id)):
        polls_database[str(message.from_user.id)] = []

    # Если юзер решил вручную отправить не викторину, а опрос, откажем ему.
    if message.poll.type == 'quiz':
        await message.reply('Извините, я не принимаю викторины!')
        return

    # Сохраняем себе викторину в память
    polls_database[str(message.from_user.id)].append(Poll(
        poll_id=message.poll.id,
        question=message.poll.question,
        options=[o.text for o in message.poll.options],
        owner_id=message.from_user.id)
    )
    # Сохраняем информацию о её владельце для быстрого поиска в дальнейшем
    polls_owners[message.poll.id] = str(message.from_user.id)

    await message.reply(
        f'Опрос сохранен. Общее число сохранённых опросов: {len(polls_database[str(message.from_user.id)])}')


# Обработка команды /weather
@dp.message_handler(commands=['weather'])
async def process_weather_command(message: types.Message):
    """
    Обработка команды /weather. Запрос погоды в заданном городе.
    """
    try:
        city = message.text.split()[1]
        weather = await weather_instance.get_weather(city)
        await message.reply(weather, parse_mode=ParseMode.HTML)
    except IndexError:
        await message.reply('Введите команду в формате /weather <город>')


# Обработка команды /currency
@dp.message_handler(commands=['currency'])
async def process_currency_command(message: types.Message):
    """
    Обработка команды /currency. Конвертация валют.
    """
    try:
        args = message.text.split()[1:]
        if len(args) != 3:
            raise IndexError
        amount = float(args[0])
        from_currency = args[1].upper()
        to_currency = args[2].upper()
        result = await currency_instance.get_exchange_rate(amount,
                                                           from_currency,
                                                           to_currency)
        await message.reply(result)
    except (IndexError, ValueError):
        await message.reply(
            'Введите команду в формате /currency <сумма> <валюта источника> '
            '<валюта назначения>\nВалюту источника и назначения указывать в '
            'общепринятом формате (EUR, RUB USD и т.д.)')


# Обработка команды /animal
@dp.message_handler(commands=['animal'])
async def process_animal_command(message: types.Message):
    """
    Обработка команды /animal. Отправка случайной картинки с милыми животными.
    """
    try:
        image = await photos_instance.get_image()
        await message.reply_photo(image)
    except:
        await message.reply(f'Ошибка в получении изображения.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
