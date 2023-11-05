from chat_app.chat import ChatMain
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    chat = ChatMain()
    chat.run()
