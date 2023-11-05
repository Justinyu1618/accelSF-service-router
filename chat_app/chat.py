from typing import TypedDict
from chat_app.data.data import DEFAULT_DATA_PATH, DataSet
from chat_app.llm.llm_functions import LMMFunctions


class ChatState(TypedDict):
    history: list[list[str]]
    current_categories: list[str]
    current_eligibilities: list[str]
    latest_msg: str


class ChatMain:
    def __init__(self):
        self.data = DataSet(DEFAULT_DATA_PATH)
        self.lmm = LMMFunctions()
        self.state: ChatState = {
            "history": [],
            "current_categories": [],
            "current_eligibilities": [],
            "latest_msg": ""
        }

    def run_output(self, output: str):
        print(f"> {output}\n")
        resp = input("> ")

        self.state['history'].append([output, resp])
        self.state['latest_msg'] = resp

    def run(self):
        resp = self.run_output("Hello, what can I help you with?")
        self.extract_supercategory()
        pass

    def extract_supercategory(self, msg):
        msg = msg or self.state['latest_msg']
        extract_supercategory_resp = self.lmm.extract_supercategory({
            "convo_history": self.state['history'],
            "current_categories": self.state['current_categories'],
            "current_eligibilities": self.state['current_eligibilities'],
            "latest_msg": msg,
            "all_supercategories": self.data.get_all_supercategories()
        })
        print(extract_supercategory_resp)
