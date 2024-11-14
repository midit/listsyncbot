import logging
import random
import string
import re
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from telegram.ext.dispatcher import run_async

product_lists = {}
sessions = {}
user_languages = {}

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def set_user_language(user_id, language_code):
    user_languages[user_id] = language_code


def get_user_language(user_id):
    return user_languages.get(user_id, 'ua')


def send_message_in_preferred_language(update, text_ua, text_en):
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    if language == 'ua':
        update.message.reply_text(text_ua)
    else:
        update.message.reply_text(text_en)


def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    set_user_language(user_id, 'ua')  # Set default language to Ukrainian
    send_message_in_preferred_language(
        update,
        "Вітаю! Використовуйте команду /create_session або /cs, щоб створити нову сесію, "
        "або /join_session або /js <код_сесії>, щоб приєднатися до сесії.",
        "Welcome! Use the /create_session or /cs command to create a new session, "
        "or /join_session or /js <session_code> to join a session."
    )

def change_language(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    args = context.args
    if len(args) == 1:
        language_code = args[0].lower()
        if language_code in ['en', 'ua']:
            set_user_language(user_id, language_code)
            if language_code == 'ua':
                update.message.reply_text("Мова змінена на українську.")
            else:
                update.message.reply_text("Language changed to English.")
        else:
            update.message.reply_text("Invalid language code. Use /en for English or /ua for Ukrainian.")
    else:
        update.message.reply_text("Invalid command format. Use /change_language <language_code>.")

def get_user_session(user_id):
    for session_code, participants in sessions.items():
        if user_id in participants:
            return session_code
    return None


def join_session(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    args = context.args
    if len(args) == 1:
        session_code = args[0]
        if session_code in sessions:
            sessions[session_code].append(user_id)
            update.message.reply_text(
                "Ви успішно приєдналися до сесії. "
                "Тепер ви можете обмінюватись повідомленнями з іншими учасниками сесії.")
        else:
            update.message.reply_text("Невірний код сесії. Спробуйте ще раз.")
    else:
        update.message.reply_text("Невірний формат команди. "
                                  "Використовуйте команду /join_session або /js <код_сесії>.")


def create_session(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    session_code = generate_session_code()
    sessions[session_code] = [user_id]
    update.message.reply_text(
        f"Код вашої сесії: {session_code}\nПодайте цей код іншому користувачу, щоб приєднатися до сесії.")


def generate_session_code() -> str:
    while True:
        session_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        if session_code not in sessions:
            return session_code


def handle_message(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    message_text = update.message.text
    lines = message_text.split('\n')

    session_code = get_user_session(user_id)
    session_users = sessions.get(session_code, [])

    if re.match(r'^-\d+(?:,\s?-\d+)*$', message_text):
        product_indices = [int(index) for index in message_text.replace('-', '').split(',')]

        if session_code and session_code in product_lists:
            products = product_lists[session_code]
            removed_products = []

            for product_index in product_indices:
                adjusted_index = product_index - 1
                if 0 <= adjusted_index < len(products):
                    removed_products.append(products.pop(adjusted_index))
                else:
                    update.message.reply_text(f"Неправильний номер продукту: {product_index}")

            if removed_products:
                for uid in session_users:
                    for removed_product in removed_products:
                        context.bot.send_message(uid, f"Продукт {removed_product} було видалено.")
                if products:
                    products_text = "\n".join(
                        [f"{index + 1}. {product} {quantity}" for index, (product, quantity) in enumerate(products)])
                    for uid in session_users:
                        context.bot.send_message(uid, f"Оновлений список продуктів:\n{products_text}")
                else:
                    for uid in session_users:
                        context.bot.send_message(uid, "Список продуктів порожній.")
            else:
                update.message.reply_text("Не вдалося знайти продукти для видалення.")
        else:
            update.message.reply_text("Ви не знаходитесь у жодній сесії або у сесії немає продуктів.")
    else:
        product_list = []
        for line in lines:
            match = re.match(r'^(.+?)(?: (\d+) ?)?$', line)
            if match:
                product_name, quantity_str = match.groups()
                quantity = int(quantity_str) if quantity_str else 1
                product_list.append((product_name, quantity))

        if product_list:
            session_code = get_user_session(user_id)
            if session_code:
                product_lists.setdefault(session_code, []).extend(product_list)
                for uid in session_users:
                    context.bot.send_message(uid, "До списку продуктів були додані нові позиції.")
                    products = product_lists[session_code]
                    products_text = "\n".join(
                        [f"{index + 1}. {product} {quantity}" for index, (product, quantity) in enumerate(products)])
                    context.bot.send_message(uid, f"Список продуктів:\n{products_text}")
            else:
                update.message.reply_text("Ви не знаходитесь у жодній сесії.")
        else:
            update.message.reply_text("Повідомлення не містить коректного списку продуктів.")


def show_product_list(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    session_code = get_user_session(user_id)

    if session_code in product_lists:
        products = product_lists[session_code]
        if products:
            products_text = "\n".join(
                [f"{index + 1}. {product} {quantity}" for index, (product, quantity) in enumerate(products)])
            update.message.reply_text(f"Список продуктів:\n{products_text}")
        else:
            update.message.reply_text("Список продуктів порожній.")
    else:
        update.message.reply_text("Ви не знаходитесь у жодній сесії або ви ще не створили список продуктів.")


def close_session(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    session_code = get_user_session(user_id)

    if session_code and session_code in sessions:
        participants = sessions[session_code]
        if len(participants) == 1:
            sessions.pop(session_code)
            product_lists.pop(session_code, None)
            update.message.reply_text("Сесію закрито.")
        else:
            participants.remove(user_id)
            update.message.reply_text("Ви вийшли з сесії.")
    else:
        update.message.reply_text("Ви не знаходитесь у жодній сесії.")


def main() -> None:
    token = 'YOUR_TOKEN'
    updater = Updater(token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('create_session', create_session))
    dispatcher.add_handler(CommandHandler('cs', create_session))
    dispatcher.add_handler(CommandHandler('join_session', join_session))
    dispatcher.add_handler(CommandHandler('js', join_session))
    dispatcher.add_handler(CommandHandler('close_session', close_session))
    dispatcher.add_handler(CommandHandler('end', close_session))
    dispatcher.add_handler(CommandHandler('list', show_product_list))
    dispatcher.add_handler(CommandHandler('lang', change_language))
    dispatcher.add_handler(MessageHandler(Filters.regex(re.compile(r'\bсписок\b', re.IGNORECASE)), show_product_list))
    dispatcher.add_handler(MessageHandler(Filters.regex(re.compile(r'\bс\b', re.IGNORECASE)), show_product_list))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
