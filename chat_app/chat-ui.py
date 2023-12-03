import json
import os
from typing import Dict, Generator

import streamlit as st

import requests
from dotenv import load_dotenv

load_dotenv()

wordware_prompt_id = "062e5016-a8b9-4749-ae3f-f95a69274f3a"


def run_prompt(prompt_id: str, inputs: Dict[str, str]) -> Generator[str, None, str]:
   # Execute the prompt
   r = requests.post(f"https://app.wordware.ai/api/prompt/{prompt_id}/run",
                     json={
                         "inputs": inputs
                     },
                     headers={"Authorization": f"Bearer {os.environ['WORDWARE_API_KEY']}"},
                     stream=True
                     )

   # Ensure the request was successful
   if r.status_code != 200:
       print("Request failed with status code", r.status_code)
       print(json.dumps(r.json(), indent=4))
   else:
       current_generation = None
       for line in r.iter_lines():
           if line:
               content = json.loads(line.decode('utf-8'))
               value = content['value']
               # We can print values as they're generated
               if value['type'] == 'generation':
                   if value['state'] == "start":
                       # print("\nNEW GENERATION -", value['label'])
                       current_generation = value['label']
                   else:
                       current_generation = None
                       # print("\nEND GENERATION -", value['label'])
               elif value['type'] == "chunk":
                   # print(value['value'], end="")
                   if current_generation == "reply":
                       yield value['value']
               # el
               if value['type'] == "outputs":
                   # Or we can read from the outputs at the end
                   # Currently we include everything by ID and by label - this will likely change in future in a breaking
                   # change but with ample warning
                   # print("\nFINAL OUTPUTS:")
                   # print(json.dumps(value, indent=4))
                   return value['values']['reply']



def main():
   st.title("AccelerateSF")
   if "messages" not in st.session_state:
       st.session_state.messages = []

   for message in st.session_state.messages:
       with st.chat_message(message["role"]):
           st.markdown(message["content"])

   if prompt := st.chat_input("How can we help?"):
       st.session_state.messages.append({"role": "user", "content": prompt})
       with st.chat_message("user"):
           st.markdown(prompt)

       with st.chat_message("assistant"):
           message_placeholder = st.empty()
           message_history = "\n".join(list([m['role'] + ": " + m['content'] for m in st.session_state.messages]))
           response = run_prompt(wordware_prompt_id, {"message_history": message_history})

           full_response = ""

           for chunk in response:
               full_response += chunk
               message_placeholder.markdown(full_response + "▌")
           message_placeholder.markdown(full_response)
       st.session_state.messages.append({"role": "assistant", "content": full_response})