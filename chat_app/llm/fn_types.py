from typing import TypedDict, Union


class ExtractSupercategoryInput(TypedDict):
    convo_history: list[list[str]]
    current_categories: list[str]
    current_eligibilities: list[str]
    latest_msg: str
    all_supercategories: list[str]
    all_eligibilities: list[str]
    all_categories: list[str]
    task: str
    latest_question: str


class GetResponseInput(TypedDict):
    convo_history: list[list[str]]
    current_categories: list[str]
    current_eligibilities: list[str]
    latest_msg: str
    task: str
    all_supercategories: Union[list[str], None]
    query_subcategories: Union[list[str], None]
    query_eligibilities: Union[list[str], None]
    current_recommendations: str
