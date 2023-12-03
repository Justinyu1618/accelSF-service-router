from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

form_url = "https://crmproxy.sfgov.org/form/auto/hsh_shelter_reservation"
form_url2 = "https://housing.sfgov.org/listings/a0W4U00000NlRyAUAV/apply-welcome/intro"

chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options, service=Service(ChromeDriverManager().install()))
driver.get(form_url)

driver.implicitly_wait(2)

# json: value to value
# dict from form id to value
ex_json = {'dform_widget_txt_FirstName': 'Jessica', 'applicant_middle_name': None, 'dform_widget_txt_LastName': 'Smith', 'dform_widget_sel_BirthMonth': 'January', 'dform_widget_sel_BirthDay': '1', 'dform_widget_txt_BirthYear': '2000', 'dform_widget_txt_Email': 'example.email@gmail.com', 'dform_widget_txt_PhoneNumber': '408-120-1930', 'dform_widget_sel_PhoneOwner': 'Self', 'dform_widget_sel_PhoneOwner': None, 'dform_widget_txt_AltEmail': 'alt.email@gmail.com', 'dform_widget_txt_AltPhone': None, 'dform_widget_sel_AltPhoneOwner': None, 'sex': 'female', 'MSC-South': 'yes', 'Nextdoor': 'yes', 'Sanctuary': 'no', 'dform_widget_Request_description': 'I need housing asap please!!! Im disabled and need help getting to the door'}

for key in ex_json: 
    if (ex_json.get(key) != None): 
        # check gender
        if (key == 'sex'):
            if (ex_json.get(key) == 'female'):
                element = driver.find_element(By.ID, 'dform_widget_rad_BedPreference2')
                element.click()
            elif (ex_json.get(key) == 'male'):
                element = driver.find_element(By.ID, 'dform_widget_rad_BedPreference1')
        elif (key == 'MSC-South'):
            if (ex_json.get(key) == 'yes'):
                element = driver.find_element(By.ID, 'dform_widget_mchk_SheltersPreference1')
                element.click()
        elif (key == 'Nextdoor'):
            if (ex_json.get(key) == 'yes'):
                element = driver.find_element(By.ID, 'dform_widget_mchk_SheltersPreference2')
                element.click()
        elif (key == 'Sanctuary'):
            if (ex_json.get(key) == 'yes'):
                element = driver.find_element(By.ID, 'dform_widget_mchk_SheltersPreference2')
                element.click()
        else: 
            element = driver.find_element(By.ID, key)
            print(element.tag_name)
            if (element.get_attribute("type") == "text") or (element.get_attribute("type") == "email") or (element.get_attribute("type") == "textarea"):
                element.send_keys(ex_json.get(key))
            elif (element.get_attribute("type") == "select-one"):
                drop=Select(element)
                drop.select_by_visible_text(ex_json.get(key))

# submit form here! 

# def dahliapt1():
#     ex_json2 = {'language': 'en', 'applicant_first_name': 'Jessica', 'applicant_middle_name': None, 'applicant_last_name': 'Li', 'date_of_birth_month': '01', 'date_of_birth_day': '01', 'date_of_birth_year': '2000', 'applicant_email': None}
#     # apply_btn = driver2.find_element(By.XPATH, "//button[contains(text(), 'Apply Online')]")
#     # apply_btn.click()
#     # driver2.implicitly_wait(2)
#     begin_btn = driver2.find_element(By.ID, f"submit-{ex_json2.get('language')}")
#     begin_btn.click()
#     driver2.implicitly_wait(2)
#     next_btn = driver2.find_element(By.ID, "submit")
#     next_btn.click()
#     driver2.implicitly_wait(2)
#     for key in ex_json2: 
#         if (key != 'language') and (ex_json2.get(key) != None):
#             if (key == 'applicant_email') and (ex_json2.get(key) == None):
#                 element = driver2.find_element(By.ID, 'applicant_no_email')
#                 element.click()
#             else: 
#                 element = driver2.find_element(By.ID, key)
#                 element.send_keys(ex_json2.get(key))

# driver2 = webdriver.Chrome(options=chrome_options, service=Service(ChromeDriverManager().install()))
# driver2.get(form_url2)
# driver2.implicitly_wait(5)
# dahliapt1()

# # Find all "See Details" buttons and click each one
# see_details_btns = driver2.find_elements(By.XPATH, "//button[contains(text(),'See Details')]")
# print(see_details_btns)

# for button in see_details_btns:
#     # Scroll into view to ensure the button is clickable
#     driver2.execute_script("arguments[0].scrollIntoView();", button)
    
#     # Click the "See Details" button
#     button.click()

#     # Handle the details page as needed (e.g., print the title)
#     driver2.implicitly_wait(3)
#     dahlia()

#     driver2.implicitly_wait(3)
#     # Navigate back to the listings page
#     # driver2.back()
