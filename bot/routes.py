import os
from config.config import bot
from modules.sheetprocessor import detect_tables
from modules.jsonqa import JsonQuestionAnswering
from modules.csvqa import CSVPromptQA
from modules.geminis import generate
from telebot import asyncio_helper


user_files = {}  # { user_id: [file_path1, file_path2, ...] }
user_sessions = {}  # {user_id: {'sheet_name': ..., 'question': ...}}
qa_instances = {}  # { sheet_name: JsonQuestionAnswering }

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message,
        "👋 Welcome to SheetQA Bot!\n\n"
        "Available commands:\n"
        "/upload_sheet - Upload an Excel file (.xlsx)\n"
        "/detect_tables sheet_name - Detect tables in the sheet\n"
        "/ask_questions 'sheet_name.xlsx' 'your question' - Ask a question"
    )

@bot.message_handler(commands=['upload_sheet'])
def prompt_upload(message):
    bot.reply_to(message, "📄 Please upload your Excel file (.xlsx) as a document.")

@bot.message_handler(content_types=['document'])
def handle_upload(message):
    user_id = message.from_user.id
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    os.makedirs("files", exist_ok=True)
    file_path = os.path.join("files", message.document.file_name)
    with open(file_path, 'wb') as f:
        f.write(downloaded_file)

    # Save uploaded file per user
    if user_id not in user_files:
        user_files[user_id] = []
    user_files[user_id].append(file_path)

    bot.reply_to(message,
        f"✅ File '{message.document.file_name}' uploaded successfully.\n\n"
        f"Now you can:\n"
        f"/detect_tables '{message.document.file_name}'\n"
        f"/ask_questions '{message.document.file_name}' 'your question'"
    )

@bot.message_handler(commands=['detect_tables'])
def handle_detect_tables(message):
    try:
        args = message.text.split(" ")
        if len(args) != 2:
            bot.reply_to(message, "⚠️ Usage: /detect_tables 'sheet name'")
            return

        sheet_name = args[1]
        file_path = f"files/{sheet_name}.xlsx"

        if not os.path.exists(file_path):
            bot.reply_to(message, f"❌ File '{sheet_name}.xlsx' not found.")
            return
        
        # Send loading GIF animation
        loading_gif_path = "files/assets/loading2.gif"
        if os.path.exists(loading_gif_path):
            with open(loading_gif_path, 'rb') as gif:
                loading_msg = bot.send_animation(
                    message.chat.id,
                    gif,
                    caption="_Detecting tables, takes 5 seconds or less..._",
                    parse_mode="Markdown"
                )
        else:
            bot.reply_to(message, "⚠️ Loading animation not found, proceeding with detection...")

        num_tables, image_path = detect_tables(file_path, visualize=True)

        reply_msg = f"✅ Detected {num_tables} table(s) in '{sheet_name}.xlsx'."
        bot.reply_to(message, reply_msg)

        # Send image
        if image_path and os.path.exists(image_path):
            with open(image_path, 'rb') as img:
                bot.send_photo(message.chat.id, img)

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

@bot.message_handler(commands=['ask_questions'])
def handle_question(message):
    try:
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            return bot.reply_to(message, "⚠️ Format: /ask_questions 'sheet_name.xlsx' 'your question'")

        sheet_name = parts[1].strip("'\"")
        question = parts[2].strip("'\"")
        file_path = os.path.join("files", sheet_name)

        if not os.path.exists(file_path):
            return bot.reply_to(message, f"❌ File '{sheet_name}' not found.")

        # Send italicized waiting message
        bot.send_chat_action(message.chat.id, 'typing')
        # Send loading gif animation
        loading_gif_path = "files/assets/loading2.gif"
        with open(loading_gif_path, 'rb') as gif:
            loading_msg = bot.send_animation(message.chat.id, gif, caption="_Generating your answer, might take up to 1 minute..._", parse_mode="Markdown")

        # Save user session
        user_sessions[message.from_user.id] = {
            'sheet_name': sheet_name,
            'question': question
        }

        answer = generate(question=question)

        # Delete loading gif
        bot.delete_message(message.chat.id, loading_msg.message_id)

        # Send answer
        bot.send_message(message.chat.id, f"💡 Answer:\n{answer}")

    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {e}")