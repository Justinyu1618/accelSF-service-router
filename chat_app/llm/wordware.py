

import json
import requests
import os
from chat_app.llm.fn_types import ExtractSupercategoryInput
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
                        print("\nFINAL OUTPUTS:")
                        print(json.dumps(value, indent=4))
                        return value
        return None

    def _process_data(self, data):
        new_data = data.copy()

        if "convo_history" in new_data:
            new_data["convo_history"] = fmt_history(data["convo_history"])

        for key, value in new_data.items():
            if type(value) is list:
                new_data[key] = ", ".join(value)

        for key, value in new_data.items():
            if value == '':
                new_data[key] = " "

        return new_data

    def extract_supercategory(self, data: ExtractSupercategoryInput):
        prompt_id = "3202cbc1-5772-426f-ad02-6a9483663634"
        processed_data = self._process_data(data)
        return self._make_request(prompt_id, processed_data)

    def query_subcategory(self, data):
        pass

    def extract_subcategory(self, data):
        pass

    def query_eligibility(self, data):
        pass

    def extract_eligibility(self, data):
        pass
