from chat_app.chat import ChatMain
from dotenv import load_dotenv

from chat_app.utils import clear_log

load_dotenv()

if __name__ == "__main__":
    clear_log()
    chat = ChatMain()
    chat.run()
