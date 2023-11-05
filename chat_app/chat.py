from typing import TypedDict
from chat_app.data.data import DEFAULT_DATA_PATH, DataSet
from chat_app.llm.llm_functions import LMMFunctions
from chat_app.utils import log


class ChatState(TypedDict):
    history: list[list[str]]
    current_categories: dict[str, float]
    current_supercategories: dict[str, float]
    current_eligibilities: list[str]
    latest_msg: str
    latest_question: str
    latest_query_eligibilities: list[str]
    latest_query_subcategories: list[str]
    current_task: str
    num_elig_queries: int
    current_recommendations: str


SUPCAT_CONF_THRESHOLD = 80
CAT_CONF_THRESHOLD = 80
NUM_SUBCATS_TO_QUERY = 3
NUM_ELIG_TO_QUERY = 1

TARGET_ELIG_QUERIES = 2

DEFAULT_RESPONSE = "Please tell me more"

EXCLUDE_SUPERCATS = ["Others"]


class ChatMain:
    def __init__(self):
        self.data = DataSet(DEFAULT_DATA_PATH)
        self.lmm = LMMFunctions()
        self.state: ChatState = {
            "history": [],
            "current_categories": {},
            "current_eligibilities": [],
            "current_supercategories": {},
            "latest_msg": "",
            "latest_question": "",
            "latest_query_eligibilities": [],
            "latest_query_subcategories": [],
            "current_task": "",
            "num_elig_queries": 0,
            "current_recommendations": ""
        }

    def run_output(self, output: str):
        print(f"> {output}\n")
        resp = input("> ")

        # Only sending response for now
        self.state['history'].append(["", resp])
        self.state['latest_question'] = output
        self.state['latest_msg'] = resp

    def run(self):
        msg = self.run_output("Hello, what can I help you with?")
        while True:
            self.lmm_extract_information(msg)

            task = self.set_current_task()
            next_resp = self.lmm_get_response(task, msg)

            self.print_state()
            msg = self.run_output(next_resp)

    def set_current_task(self):
        task = "conversation"

        # If any supercategory is above the confidence threshold, we should query subcategories
        sup_cat = self.state['current_supercategories']
        if (any(val >= SUPCAT_CONF_THRESHOLD for val in sup_cat.values())):
            task = "query_subcategory"
        cats = self.state['current_categories']
        if (any(val >= CAT_CONF_THRESHOLD for val in cats.values())):
            task = "query_eligibility"

        elig_services, cand_services = self.data.get_candidate_services(
            self.state['current_categories'], self.state['current_eligibilities'])
        if (self.state['num_elig_queries'] >= TARGET_ELIG_QUERIES):
            task = "recommend"
        if (self.state["current_recommendations"]):
            task = "qa"

        self.state['current_task'] = task
        return task

    def lmm_get_response(self, task, msg=None):
        query_subcategories = None
        all_supercategories = None
        query_eligibilities = None

        if (task == "query_subcategory"):
            query_subcategories = self.get_top_subcategories()
            self.state['latest_query_subcategories'] = query_subcategories
            log(f"QUERY_SUB: {query_subcategories}")
            all_supercategories = self.data.get_all_supercategories()

        if (task == "query_eligibility"):
            query_eligibilities = self.get_top_eligibilities()
            self.state['latest_query_eligibilities'] = query_eligibilities
            self.state['num_elig_queries'] += 1
            log(f"QUERY_ELIG: {query_eligibilities}", )

        if (task == "recommend"):
            elig_services = self.data.get_candidate_services(
                self.state['current_categories'], self.state['current_eligibilities'])[0]

            rec_str = self.data.get_service_string(elig_services[:10])
            self.state['current_recommendations'] = rec_str
            # log("REC: ", rec_str)

        msg = msg or self.state['latest_msg']
        get_response_resp = self.lmm.get_response({
            "convo_history": self.state['history'],
            "current_categories": list(self.state['current_categories'].keys()),
            "current_eligibilities": self.state['current_eligibilities'],
            "latest_msg": msg,
            "all_supercategories": all_supercategories,
            "task": task,
            "query_subcategories": query_subcategories,
            "query_eligibilities": query_eligibilities,
            "current_recommendations": self.state['current_recommendations']
        })

        # log("RESP: ", get_response_resp)
        if (get_response_resp):
            return get_response_resp["response"]
        return DEFAULT_RESPONSE

    def lmm_extract_information(self, msg=None):

        if (self.state['current_task'] == "recommend" or self.state['current_task'] == "qa"):
            return

        msg = msg or self.state['latest_msg']
        all_eligibilites = self.data.get_all_eligibilities_for_categories(
            self.state["current_categories"])
        all_categories = self.data.get_all_categories_for_supercategories(
            self.state['current_supercategories'])

        extract_supercategory_resp = self.lmm.extract_supercategory({
            "convo_history": self.state['history'],
            "current_categories": list(self.state['current_categories'].keys()),
            "current_eligibilities": list(self.state['current_eligibilities']),
            "latest_msg": msg,
            "latest_question": self.state['latest_question'],
            "all_supercategories": self.data.get_all_supercategories(),
            "all_eligibilities": all_eligibilites,
            "all_categories": all_categories,
            "task": self.state['current_task']
        })

        if extract_supercategory_resp:
            log(f"RETURNED EXTRACTED INFO: {extract_supercategory_resp}", )
            supercategories = extract_supercategory_resp['new_supercategories']
            log(f"extracted supercategories: {supercategories} ", )
            for sup, perc in supercategories.items():
                if (not self.data.is_valid_supercategory(sup)):
                    continue
                # This is not actually a running average, potentially better to bias towards new responses?
                new_perc = (self.state['current_supercategories'][sup] + perc) / \
                    2 if sup in self.state['current_supercategories'] else perc
                self.state['current_supercategories'][sup] = new_perc

                if (perc >= SUPCAT_CONF_THRESHOLD):
                    categories = self.data.get_categories_for_supercategory(
                        sup)
                    for cat in categories:
                        cat_perc = perc * 0.75
                        new_perc = (self.state['current_categories'][cat] + cat_perc) / \
                            2 if cat in self.state['current_categories'] else cat_perc
                        self.state['current_categories'][cat] = new_perc

            eligibilities = extract_supercategory_resp['new_eligibilities']
            log(f"extracted eligibilities: {eligibilities}", )
            # for elig, perc in eligibilities.items():
            #     if (not self.data.is_valid_eligibity(elig)):
            #         log("NOT VALID ELIGIBILITY")
            #         continue
            #     # This is not actually a running average, potentially better to bias towards new responses?
            #     new_perc = (self.state['current_eligibilities'][elig] + perc) / \
            #         2 if elig in self.state['current_eligibilities'] else perc
            #     self.state['current_eligibilities'][elig] = new_perc
            for elig in eligibilities:
                if (not self.data.is_valid_eligibity(elig)):
                    log("NOT VALID ELIGIBILITY")
                    continue
                # This is not actually a running average, potentially better to bias towards new responses?
                self.state['current_eligibilities'].append(elig)

            categories = extract_supercategory_resp['new_categories']
            log(f"extracted categories: {categories} ", )
            for cat, perc in categories.items():
                if (not self.data.is_valid_category(cat)):
                    continue
                # This is not actually a running average, potentially better to bias towards new responses?
                new_perc = (self.state['current_categories'][cat] + perc) / \
                    2 if cat in self.state['current_categories'] else perc
                self.state['current_categories'][cat] = new_perc

            if (self.state['current_task'] == 'query_subcategory'):
                affirmative = extract_supercategory_resp[
                    'category_affirmative'] if 'category_affirmative' in extract_supercategory_resp else None
                if (affirmative != None):
                    new_categories = {cat: 120 if
                                      affirmative else 0 for cat in self.state['latest_query_subcategories']}
                    log(
                        f"affirmative: {affirmative} updates: {new_categories}")
                    self.apply_perc_update(
                        new_categories, self.state['current_categories'])

            if (self.state['current_task'] == 'query_eligibility'):
                affirmative = extract_supercategory_resp[
                    'eligibility_affirmative'] if 'eligibility_affirmative' in extract_supercategory_resp else None
                if (affirmative):
                    for elig in self.state['latest_query_eligibilities']:
                        self.state['current_eligibilities'].append(elig)
                    log(
                        f"affirmative: {affirmative} updates: {self.state['latest_query_eligibilities']}")

    def apply_perc_update(self, update, current):
        for key, perc in update.items():
            # This is not actually a running average, potentially better to bias towards new responses?
            new_perc = (current[key] + perc) / \
                2 if key in current else perc
            current[key] = new_perc
        return current

    def get_top_subcategories(self):
        cats = self.state['current_categories']
        ordered_list = self.data.get_ordered_list_of_categories(cats.keys())
        return ordered_list[:NUM_SUBCATS_TO_QUERY]

    def get_top_eligibilities(self):
        cats = self.state['current_categories']
        ordered_list = self.data.get_ordered_list_of_eligibilities(cats)
        return list(filter(lambda elig: elig not in self.state['current_eligibilities'], ordered_list))[:NUM_ELIG_TO_QUERY]

    def print_state(self):
        log(f"""\n=========\nState: \n super categories: {self.state['current_supercategories']}\n categories:
              {self.state['current_categories']}\n eligibilities: {self.state['current_eligibilities']}\n current_task: {self.state['current_task']}\n==========\n""") 