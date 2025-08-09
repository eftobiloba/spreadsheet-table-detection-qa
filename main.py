# from bot.routes import bot
from modules.sheetprocessor import detect_tables
from modules.csvqa import CSVPromptQA

if __name__ == "__main__":

    # This tests table detection
    file_path = "files/report2.xlsx"
    num_tables, image_path = detect_tables(file_path, visualize=True)
    print(f"✅ Detected {num_tables} table(s).")

    # This runs the bot
    # print("🤖 Bot is running...")
    # bot.infinity_polling()