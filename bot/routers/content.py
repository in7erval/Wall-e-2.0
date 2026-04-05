"""
Роутер для контента: анекдоты, цитаты, гороскоп, факты
"""
import hashlib
import random
from datetime import date

import aiohttp
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

router = Router()

# ==================== Шар-предсказатель ====================

MAGIC_8BALL_ANSWERS = [
    # Положительные
    "Бесспорно", "Предрешено", "Никаких сомнений", "Определённо да",
    "Можешь быть уверен", "Мне кажется — да", "Вероятнее всего",
    "Хорошие перспективы", "Знаки говорят — да", "Да",
    # Нейтральные
    "Пока не ясно, попробуй снова", "Спроси позже",
    "Лучше не рассказывать", "Сейчас нельзя предсказать",
    "Сконцентрируйся и спроси опять",
    # Отрицательные
    "Даже не думай", "Мой ответ — нет", "По моим данным — нет",
    "Перспективы не очень", "Весьма сомнительно",
]


@router.message(F.text.casefold().startswith("бот шар"))
async def magic_8ball(message: Message) -> None:
    """Шар-предсказатель (Magic 8-ball)"""
    question = message.text.split("бот шар", 1)[-1].strip() if message.text else ""
    if not question:
        await message.reply("🎱 Задай вопрос! Например: бот шар я сдам экзамен?")
        return
    answer = random.choice(MAGIC_8BALL_ANSWERS)
    await message.reply(f"🎱 {answer}")


# ==================== Рейтинг ====================

RATING_COMMENTS = {
    0: "💀 Ужас...",
    1: "😰 Очень плохо",
    2: "😕 Плохо",
    3: "😐 Ниже среднего",
    4: "🤔 Так себе",
    5: "😑 Средненько",
    6: "🙂 Неплохо",
    7: "😊 Хорошо",
    8: "😃 Очень хорошо!",
    9: "🤩 Отлично!",
    10: "🏆 Идеально!",
}


@router.message(F.text.casefold().startswith("бот оцени"))
async def rate(message: Message) -> None:
    """Бот, оцени [что-то]"""
    thing = message.text.split("бот оцени", 1)[-1].strip() if message.text else ""
    if not thing:
        await message.reply("Что оценить? Например: бот оцени мой код")
        return
    score = random.randint(0, 10)
    comment = RATING_COMMENTS[score]
    bar = "▓" * score + "░" * (10 - score)
    await message.reply(f"Оценка: {bar} <b>{score}/10</b>\n{comment}")


# ==================== Анекдоты ====================

JOKES = [
    "— Алло, это прачечная?\n— Какая, к чёрту, прачечная?! Это министерство обороны!\n— А почему так грязно?",
    "Программист ставит себе на тумбочку перед сном два стакана. Один с водой — если захочет пить. Второй пустой — если не захочет.",
    "— Что будет, если скрестить ежа и ужа?\n— Полтора метра колючей проволоки.",
    "Заходит улитка в бар. Бармен её выкидывает. Через неделю улитка заходит снова:\n— И за что вы меня в прошлый раз выкинули?",
    "Штирлиц стрелял вслепую. Слепая падала, поднималась и снова шла.",
    "— Доктор, меня все игнорируют.\n— Следующий!",
    "Оптимист изучает английский. Пессимист — китайский. Реалист — автомат Калашникова.",
    "Программист: У меня в коде 99 багов. Исправил один — стало 117.",
    "— Сири, почему я одинок?\n— *открывает фронтальную камеру*",
    "Жена программисту: Сходи в магазин, купи батон хлеба. Если будут яйца — возьми десяток.\nПрограммист принёс 10 батонов хлеба.\n— Яйца были.",
    "В России только две проблемы — дураки и дороги. И обе не решаются.",
    "— Официант, у вас есть рыба без костей?\n— Есть, но она тоже уже не плавает.",
    "Вчера был на свидании вслепую. Зря я ей глаза завязал.",
    "Колобок повесился.",
    "У чукчи спрашивают: «Ты в интернете сидишь?» — «Нет, однако, стою. Стулья у вас дорогие.»",
    "Мама, я замуж хочу! — А посуду мыть не хочешь? — Ну, если только за это...",
    "— Какой язык программирования самый быстрый?\n— JavaScript. Не успеешь оглянуться — уже новый фреймворк.",
    "Совещание — это место, где минуты записывают, а часы теряют.",
    "— Почему программисты путают Хэллоуин и Рождество?\n— Потому что OCT 31 == DEC 25.",
    "Идёт медведь по лесу. Видит — машина горит. Сел в неё и сгорел.",
]


@router.message(Command("joke"))
@router.message(F.text.casefold().in_({"анекдот", "бот анекдот", "расскажи анекдот", "бот расскажи анекдот"}))
async def cmd_joke(message: Message) -> None:
    """Случайный анекдот"""
    joke = random.choice(JOKES)
    await message.reply(joke)


# ==================== Цитаты ====================

FALLBACK_QUOTES = [
    ("Единственный способ делать великие дела — любить то, что делаешь.", "Стив Джобс"),
    ("Жизнь — это то, что с тобой происходит, пока ты строишь другие планы.", "Джон Леннон"),
    ("Будь собой; прочие роли уже заняты.", "Оскар Уайльд"),
    ("Не ошибается тот, кто ничего не делает.", "Теодор Рузвельт"),
    ("Будущее принадлежит тем, кто верит в красоту своей мечты.", "Элеонора Рузвельт"),
    ("Лучше быть хорошим человеком, ругающимся матом, чем тихой воспитанной тварью.", "Фаина Раневская"),
    ("Сложнее всего начать действовать, всё остальное зависит только от упорства.", "Амелия Эрхарт"),
    ("Учитесь так, словно будете жить вечно; живите так, словно умрёте завтра.", "Махатма Ганди"),
    ("Самый тёмный час — перед рассветом.", "Томас Фуллер"),
    ("Код — это поэзия.", "Линус Торвальдс"),
]


@router.message(Command("quote"))
@router.message(F.text.casefold().in_({"цитата", "бот цитата"}))
async def cmd_quote(message: Message) -> None:
    """Случайная цитата"""
    # Пробуем API forismatic
    try:
        async with aiohttp.ClientSession() as session, session.get(
            "http://api.forismatic.com/api/1.0/",
            params={"method": "getQuote", "format": "json", "lang": "ru"},
            timeout=aiohttp.ClientTimeout(total=3)
        ) as resp:
            if resp.status == 200:
                data = await resp.json(content_type=None)
                text = data.get("quoteText", "").strip()
                author = data.get("quoteAuthor", "").strip() or "Неизвестный"
                if text:
                    await message.reply(f"💬 <i>{text}</i>\n\n— <b>{author}</b>")
                    return
    except Exception:
        pass

    # Фолбэк на локальные цитаты
    text, author = random.choice(FALLBACK_QUOTES)
    await message.reply(f"💬 <i>{text}</i>\n\n— <b>{author}</b>")


# ==================== Гороскоп ====================

ZODIAC_SIGNS = {
    "овен": "♈", "телец": "♉", "близнецы": "♊", "рак": "♋",
    "лев": "♌", "дева": "♍", "весы": "♎", "скорпион": "♏",
    "стрелец": "♐", "козерог": "♑", "водолей": "♒", "рыбы": "♓",
}

HOROSCOPE_TEMPLATES = [
    "Сегодня звёзды говорят: {action}. {advice}.",
    "{advice}. Звёзды намекают, что {action}.",
    "День будет {mood}. {action}. {advice}.",
    "Планеты сошлись так, что {action}. {advice}.",
]

HOROSCOPE_ACTIONS = [
    "удача будет на вашей стороне",
    "вас ждёт приятный сюрприз",
    "кто-то из близких порадует вас",
    "стоит быть осторожнее с финансами",
    "новые знакомства принесут пользу",
    "вы найдёте ответ на давний вопрос",
    "стоит уделить время отдыху",
    "рабочие дела пойдут в гору",
    "вам улыбнётся фортуна",
    "стоит довериться интуиции",
    "появится шанс изменить привычный порядок вещей",
    "творческая энергия будет зашкаливать",
    "важный человек обратит на вас внимание",
    "вселенная отправит вам знак — не пропустите",
]

HOROSCOPE_ADVICE = [
    "Не забудьте выпить воды",
    "Позвоните близким — они скучают",
    "Сегодня лучше избегать споров",
    "Хороший день для начала нового проекта",
    "Прогулка на свежем воздухе не помешает",
    "Доверяйте своим чувствам",
    "Не откладывайте важные дела",
    "Побалуйте себя чем-нибудь вкусным",
    "Медитация поможет собраться с мыслями",
    "Сегодня ваш счастливый день — дерзайте",
]

HOROSCOPE_MOODS = [
    "энергичным", "спокойным", "продуктивным", "романтичным",
    "непредсказуемым", "вдохновляющим", "расслабленным", "насыщенным",
]


@router.message(Command("horoscope"))
@router.message(F.text.casefold().startswith("бот гороскоп"))
@router.message(F.text.casefold() == "гороскоп")
async def cmd_horoscope(message: Message) -> None:
    """Шуточный гороскоп"""
    text = message.text or ""
    # Ищем знак зодиака
    sign_name = None
    for sign in ZODIAC_SIGNS:
        if sign in text.lower():
            sign_name = sign
            break

    if not sign_name:
        # Показываем кнопки выбора знака
        rows = []
        signs = list(ZODIAC_SIGNS.items())
        for i in range(0, len(signs), 3):
            row = []
            for name, emoji in signs[i:i + 3]:
                row.append(InlineKeyboardButton(
                    text=f"{emoji} {name.capitalize()}",
                    callback_data=f"horo_{name}"
                ))
            rows.append(row)
        await message.answer(
            "🔮 Выберите знак зодиака:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=rows)
        )
        return

    await message.reply(_generate_horoscope(sign_name))


@router.callback_query(F.data.startswith("horo_"))
async def horoscope_callback(call: CallbackQuery) -> None:
    sign_name = call.data.replace("horo_", "")
    if sign_name not in ZODIAC_SIGNS:
        return
    await call.message.edit_text(_generate_horoscope(sign_name))


def _generate_horoscope(sign_name: str) -> str:
    emoji = ZODIAC_SIGNS.get(sign_name, "⭐")
    # Детерминированный рандом по знаку + дата (чтобы не менялся в течение дня)
    seed = hashlib.md5(f"{sign_name}{date.today()}".encode()).hexdigest()
    rng = random.Random(seed)

    template = rng.choice(HOROSCOPE_TEMPLATES)
    horoscope = template.format(
        action=rng.choice(HOROSCOPE_ACTIONS),
        advice=rng.choice(HOROSCOPE_ADVICE),
        mood=rng.choice(HOROSCOPE_MOODS),
    )
    lucky_number = rng.randint(1, 99)

    return (
        f"{emoji} <b>Гороскоп для {sign_name.capitalize()}</b>\n"
        f"📅 {date.today().strftime('%d.%m.%Y')}\n\n"
        f"{horoscope}\n\n"
        f"🔢 Счастливое число: <b>{lucky_number}</b>"
    )


# ==================== Факт дня ====================

FACTS = [
    "Осьминоги имеют три сердца и голубую кровь.",
    "Мёд — единственный продукт, который не портится тысячелетиями.",
    "На Юпитере и Сатурне идут дожди из алмазов.",
    "Бананы — это ягоды, а клубника — нет.",
    "У улитки около 25 000 зубов.",
    "Группа фламинго называется «фламбоянс».",
    "Свет Солнца достигает Земли за 8 минут 20 секунд.",
    "В среднем человек проводит 6 месяцев жизни в ожидании зелёного сигнала светофора.",
    "Сердце синего кита настолько большое, что ребёнок может проползти по его артериям.",
    "Клеопатра жила ближе к запуску iPhone, чем к строительству пирамид.",
    "На Венере день длится дольше, чем год.",
    "В одном литре морской воды содержится около 13 миллиардов атомов золота.",
    "Муравьи не спят.",
    "Первый программист в истории — женщина: Ада Лавлейс.",
    "Кошки не чувствуют сладкого вкуса.",
    "Человеческий мозг потребляет около 20% всей энергии тела.",
    "В космосе нет звука — звуковые волны не распространяются в вакууме.",
    "ДНК человека на 60% совпадает с ДНК банана.",
    "Эйфелева башня летом вырастает на 15 см из-за расширения металла.",
    "Среднестатистический человек за жизнь проходит расстояние, равное 5 кругосветным путешествиям.",
    "У Земли есть ещё один «квази-спутник» — астероид Круитни.",
    "Слоны — единственные животные, которые не умеют прыгать.",
    "Каждый день наш мозг генерирует около 70 000 мыслей.",
    "Длина всех кровеносных сосудов человека — около 100 000 км.",
    "Горилла может заболеть простудой от человека.",
]


@router.message(Command("fact"))
@router.message(F.text.casefold().in_({"факт", "бот факт", "факт дня", "бот факт дня"}))
async def cmd_fact(message: Message) -> None:
    """Случайный интересный факт"""
    fact = random.choice(FACTS)
    await message.reply(f"💡 <b>Интересный факт:</b>\n\n{fact}")


# ==================== Кто сегодня ====================

@router.message(Command("who"))
@router.message(F.text.casefold().startswith("бот кто сегодня"))
async def cmd_who_is_today(message: Message) -> None:
    """Кто сегодня [роль]? — выбирает случайного участника"""
    getattr(message, '_repos', None) or {}

    text = message.text or ""
    # Извлекаем роль
    if text.startswith("/who"):
        role = text.split(maxsplit=1)[1].strip() if " " in text else "избранный"
    else:
        role = text.lower().split("бот кто сегодня", 1)[-1].strip() or "избранный"

    # Получаем уникальных пользователей из сообщений этого чата
    from sqlalchemy import select

    from database import async_session_maker
    from database.models import Message as MessageModel

    try:
        async with async_session_maker() as session:
            result = await session.execute(
                select(MessageModel.person_id, MessageModel.name)
                .where(MessageModel.chat_id == message.chat.id)
                .distinct(MessageModel.person_id)
            )
            users = result.all()
    except Exception:
        users = []

    if not users:
        await message.reply("🤷 Не знаю участников этого чата. Напишите побольше сообщений!")
        return

    # Детерминированный выбор по роли + дата
    seed = hashlib.md5(f"{message.chat.id}{role}{date.today()}".encode()).hexdigest()
    rng = random.Random(seed)
    person_id, name = rng.choice(users)

    await message.reply(
        f"🎯 Сегодня <b>{role}</b> — <a href='tg://user?id={person_id}'>{name}</a>!"
    )


# ==================== Совместимость ====================

@router.message(Command("match"))
@router.message(F.text.casefold().startswith("бот совместимость"))
async def cmd_match(message: Message) -> None:
    """Совместимость двух пользователей"""
    user1_id = message.from_user.id
    user1_name = message.from_user.full_name

    # Если ответ на чьё-то сообщение
    if message.reply_to_message and message.reply_to_message.from_user:
        user2_id = message.reply_to_message.from_user.id
        user2_name = message.reply_to_message.from_user.full_name
    else:
        await message.reply(
            "💕 Ответьте на сообщение пользователя, с которым хотите проверить совместимость!\n"
            "Или: /match (в ответ на сообщение)"
        )
        return

    if user1_id == user2_id:
        await message.reply("💕 Самовлюблённость — 100%! 😏")
        return

    # Детерминированный % по паре + дата
    pair = tuple(sorted([user1_id, user2_id]))
    seed = hashlib.md5(f"{pair}{date.today()}".encode()).hexdigest()
    percent = random.Random(seed).randint(0, 100)

    if percent >= 90:
        comment = "🔥 Идеальная пара!"
    elif percent >= 70:
        comment = "💕 Отличная совместимость!"
    elif percent >= 50:
        comment = "💛 Неплохо, есть потенциал"
    elif percent >= 30:
        comment = "🤔 Сложно, но возможно"
    else:
        comment = "💔 Звёзды не на вашей стороне..."

    bar = "❤️" * (percent // 10) + "🖤" * (10 - percent // 10)
    await message.reply(
        f"💕 <b>Совместимость</b>\n\n"
        f"👤 {user1_name}\n"
        f"👤 {user2_name}\n\n"
        f"{bar} <b>{percent}%</b>\n"
        f"{comment}"
    )


# ==================== Стикер из текста (Big Text) ====================

EMOJI_FONT = {
    'а': '🅰', 'б': '🅱', 'в': '🔷', 'г': '🟦', 'д': '🔶',
    'е': '📧', 'ё': '📧', 'ж': '❇️', 'з': '3️⃣', 'и': '🔵',
    'й': '🔵', 'к': '🟧', 'л': '🟩', 'м': 'Ⓜ️', 'н': '🟥',
    'о': '⭕', 'п': '🟪', 'р': '🅿', 'с': '🌀', 'т': '✝️',
    'у': '🔘', 'ф': '🎱', 'х': '❌', 'ц': '🟡', 'ч': '☑️',
    'ш': '🔲', 'щ': '🔳', 'ъ': '▪️', 'ы': '🔸', 'ь': '▫️',
    'э': '🔹', 'ю': '🔮', 'я': '🏮',
    'a': '🅰', 'b': '🅱', 'c': '🌀', 'd': '🔶', 'e': '📧',
    'f': '🎏', 'g': '🟩', 'h': '🟥', 'i': 'ℹ️', 'j': '🎷',
    'k': '🟧', 'l': '🟦', 'm': 'Ⓜ️', 'n': '🟪', 'o': '⭕',
    'p': '🅿', 'q': '🔵', 'r': '🔴', 's': '💲', 't': '✝️',
    'u': '🔘', 'v': '🔻', 'w': '🔷', 'x': '❌', 'y': '🔸',
    'z': '💤',
    '0': '0️⃣', '1': '1️⃣', '2': '2️⃣', '3': '3️⃣', '4': '4️⃣',
    '5': '5️⃣', '6': '6️⃣', '7': '7️⃣', '8': '8️⃣', '9': '9️⃣',
    ' ': '  ', '!': '❗', '?': '❓', '.': '🔹', ',': '▪️',
}


@router.message(Command("bigtext"))
async def cmd_bigtext(message: Message) -> None:
    """Превратить текст в эмодзи"""
    text = (message.text or "").split(maxsplit=1)
    if len(text) < 2:
        await message.reply("Использование: /bigtext [текст]")
        return

    input_text = text[1][:50]  # Ограничение
    result = " ".join(EMOJI_FONT.get(ch.lower(), ch) for ch in input_text)
    await message.reply(result)
