

import json
import requests
import os
import re
from chat_app.llm.fn_types import ExtractSupercategoryInput, GetResponseInput
from chat_app.llm.utils import fmt_history

ENDPOINT_URL = "https://app.wordware.ai/api/prompt/%s/run"


class WordWare:
    def __init__(self):
        self.api_key = os.getenv('WORDWARE_API_KEY')
        pass

    def _make_request(self, prompt_id, inputs):
        # Execute the prompt)
        r = requests.post(ENDPOINT_URL % prompt_id,
                          json={
                              "inputs": inputs
                          },
                          headers={
                              "Authorization": f"Bearer {self.api_key}"},
                          stream=True
                          )

        # Ensure the request was successful
        if r.status_code != 200:
            print("Request failed with status code", r.status_code)
            print(json.dumps(r.json(), indent=4))
        else:
            for line in r.iter_lines():
                if line:
                    content = json.loads(line.decode('utf-8'))
                    print("CONTENT: ", content)
                    value = content['value']
                    # # We can print values as they're generated
                    # if value['type'] == 'generation':
                    #     if value['state'] == "start":
                    #         print("\nNEW GENERATION -", value['label'])
                    #     else:
                    #         print("\nEND GENERATION -", value['label'])
                    # elif value['type'] == "chunk":
                    #     print(value['value'], end="")
                    if value['type'] == "outputs":
                        # Or we can read from the outputs at the end
                        # Currently we include everything by ID and by label - this will likely change in future in a breaking
                        # change but with ample warning

                        # print("\nFINAL OUTPUTS:")
                        # print(json.dumps(value, indent=4))
                        return value
                    elif 'state' in value and value['state'] == "error":
                        print("ERROR: ", value)
                        # print(inputs["current_eligibility"])

    def _preprocess_data(self, data):
        new_data = data.copy()

        if "convo_history" in new_data:
            new_data["convo_history"] = fmt_history(data["convo_history"])

        for key, value in new_data.items():
            if type(value) is list:
                new_data[key] = ", ".join(value)

        for key, value in new_data.items():
            if value == '' or value == None:
                new_data[key] = " "

        return new_data

    def _parse_response_value(self, values):
        SUPCATEGORY_PROMPT_NAME = "accelSF/Classify Category"
        ELIG_PROMPT_NAME = "accelSF/Classify Eligibility"
        CATEGORY_PROMPT_NAME = "accelSF/Classify SubCategory"
        QUERY_ELIG_PROMPT_NAME = "accelSF/Query Eligibility"

        # print("RAW VALUES: ", values)
        values["new_supercategories"] = self._parse_categories_resp(
            values[SUPCATEGORY_PROMPT_NAME]["new_supercategories"]) if SUPCATEGORY_PROMPT_NAME in values else {}
        values["new_categories"] = self._parse_categories_resp(
            values[CATEGORY_PROMPT_NAME]["new_categories"]) if CATEGORY_PROMPT_NAME in values else {}
        values["category_affirmative"] = bool(
            values[CATEGORY_PROMPT_NAME]["affirmative"]) if CATEGORY_PROMPT_NAME in values else None
        values["new_eligibilities"] = self._parse_eligibilities_resp(
            values[ELIG_PROMPT_NAME]["new_eligibilities"]) if ELIG_PROMPT_NAME in values else []
        values["eligibility_affirmative"] = bool(
            values[QUERY_ELIG_PROMPT_NAME]["affirmative"]) if QUERY_ELIG_PROMPT_NAME in values else None

        return values

    def _parse_categories_resp(self, resp):
        matches = re.findall(r'([a-zA-Z ]*?), (\d{1,2}|100)%', resp)

        result = {category: int(perc) for category, perc in matches}
        return result

    def _parse_eligibilities_resp(self, resp):
        # matches = re.findall(r'([a-zA-Z ]*?)', resp)
        matches = resp.split(",")
        print("MATCHES", matches)
        result = [elig.strip() for elig in matches]
        return result

    def extract_supercategory(self, data: ExtractSupercategoryInput):
        print("extracting data")
        prompt_id = "ba587aa9-64d9-442c-9a27-9b34652efc95"
        processed_data = self._preprocess_data(data)
        resp = self._make_request(prompt_id, processed_data)
        print("RESP: ", resp)
        if resp:
            values = self._parse_response_value(resp["values"])
            print("VALUES: ", values)
            return values
        return None

    def get_response(self, data: GetResponseInput):
        prompt_id = "c477762e-b8dd-4e6e-a331-0696e3a70ecb"
        processed_data = self._preprocess_data(data)
        resp = self._make_request(prompt_id, processed_data)

        if resp:
            values = resp["values"]
            return values

    def query_subcategory(self, data):
        pass

    def extract_subcategory(self, data):
        pass

    def query_eligibility(self, data):
        pass

    def extract_eligibility(self, data):
        pass
