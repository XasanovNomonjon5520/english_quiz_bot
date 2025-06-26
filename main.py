import telebot
import random
import json
import os
from dotenv import load_dotenv
import os

load_dotenv()  # Bu juda muhim

load_dotenv()
BOT_TOKEN = ("7645795503:AAGk-9CfNcBcEGNWsdO5H0SL72OdSz1HmIo")
bot = telebot.TeleBot(BOT_TOKEN)


def load_questions():
    with open("data/daily_lessons.json", "r", encoding="utf-8") as f:
        return json.load(f)

questions = load_questions()
user_states = {}

def get_shuffled_options(question_data):
    options = list(question_data["options"])
    answer = question_data["answer"]
    if answer not in options:
        options.append(answer)
    random.shuffle(options)
    formatted_options = [f"{chr(65 + i)}) {opt}" for i, opt in enumerate(options)]
    return formatted_options, options.index(answer)

def send_next_question(message, user_id):
    state = user_states[user_id]
    if state['current_question_index'] >= len(state['shuffled_questions']):
        bot.send_message(
            message.chat.id,
            f"✅ Test tugadi! Siz {len(state['shuffled_questions'])} ta savoldan {state['score']} tasiga to‘g‘ri javob berdingiz."
        )
        del user_states[user_id]
        return

    if state['total_questions_answered'] > 0 and state['total_questions_answered'] % 10 == 0:
        remaining = len(state['shuffled_questions']) - state['current_question_index']
        bot.send_message(message.chat.id, f"ℹ️ Siz {state['total_questions_answered']} ta javob berdingiz. Qolgan savollar: {remaining}")

    q = state['shuffled_questions'][state['current_question_index']]
    opts, correct_idx = get_shuffled_options(q)
    q['correct_char'] = chr(65 + correct_idx)

    options_text = "\n".join(opts)
    bot.send_message(message.chat.id, f"{q['question']}\n\n{options_text}")
    bot.send_message(message.chat.id, "Javobingizni harf bilan yuboring. (Masalan: A)")

@bot.message_handler(commands=['start', 'hello'])
def start_msg(message):
    bot.send_message(message.chat.id, "Assalomu alaykum! 👋 /test buyrug‘i orqali testni boshlang.")

@bot.message_handler(commands=['test'])
def start_test(message):
    user_id = message.from_user.id
    shuffled = list(questions)
    random.shuffle(shuffled)
    user_states[user_id] = {
        'current_question_index': 0,
        'shuffled_questions': shuffled,
        'score': 0,
        'total_questions_answered': 0
    }
    bot.send_message(message.chat.id, "🎯 Test boshlandi!")
    send_next_question(message, user_id)

@bot.message_handler(func=lambda msg: True)
def check_answer(message):
    user_id = message.from_user.id
    if user_id not in user_states:
        bot.send_message(message.chat.id, "Avval /test buyrug‘ini yuboring.")
        return

    state = user_states[user_id]
    q = state['shuffled_questions'][state['current_question_index']]
    correct_char = q['correct_char']
    user_char = message.text.upper().strip()

    if user_char == correct_char:
        bot.send_message(message.chat.id, "✅ To‘g‘ri javob! 🎉")
        state['score'] += 1
    else:
        bot.send_message(
            message.chat.id,
            f"❌ Noto‘g‘ri. To‘g‘ri javob: {correct_char}) {q['answer']}"
        )

    state['total_questions_answered'] += 1
    state['current_question_index'] += 1
    send_next_question(message, user_id)

print("🤖 Bot ishga tushdi...")
bot.polling()