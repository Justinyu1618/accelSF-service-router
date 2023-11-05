

from typing import Literal, TypeAlias, TypedDict
from chat_app.llm.fn_types import ExtractSupercategoryInput
from chat_app.llm.wordware import WordWare


LMMBackends: TypeAlias = 'Literal["wordware"]'


class LMMFunctions:
    def __init__(self, backend: LMMBackends = "wordware"):
        if (backend == "wordware"):
            self.backend = WordWare()
        pass

    def extract_supercategory(self, data: ExtractSupercategoryInput):
        return self.backend.extract_supercategory(data)

    def query_subcategory(self, data):
        pass

    def extract_subcategory(self, data):
        pass

    def query_eligibility(self, data):
        pass

    def extract_eligibility(self, data):
        pass
