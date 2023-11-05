from typing import TypedDict


class ExtractSupercategoryInput(TypedDict):
    convo_history: list[list[str]]
    current_categories: list[str]
    current_eligibilities: list[str]
    latest_msg: str
    all_supercategories: list[str]
