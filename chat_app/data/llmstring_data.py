import json
from string import Template

# set string template for LLM to process
# t = Template("The service name is $name.\nHere is a description of the service it offers:\n$long_description\nThe following are the required documents to receive the service:\n$required_documents\nThe fee is $fee.\nHere is the information for the application process:\n$application_process\nThis is an email to contact them: $email\nThe service provides the following interpretation services:\n$interpretation_services\nHere is the website: $url\nIs there a wait time: $wait_time\nIt may also be known as its alternate name, $alternate_name.\nHere are the addresses associated with the service:\n$address_string\nThe service provides services under the following categories: \n$categories\nIt has the following eligibility category requirements: $eligibility\nHere is the service's phone number: \nHere are instructions associated with the service: $instructions.\nHere are the hours for the service:\n$schedule_string\n------------------------------------------------------------\n") 

# read in JSON file
with open('/Users/jessica.li/Desktop/accelSF-service-router/json_files/combined_pgs.json', 'r') as f: 
    data = json.load(f)

# define a class for Default values if key does not exist
class Default(dict):
    def __missing__(self, key):
        return 'N/A'
    
addresses_string = ""
schedule_string = ""
phone_string = ""

    
def data_to_string(hit, addresses_string, schedule_string, phone_string):
    # loop through addresses list for a list of addresses associated with service
    for address in hit["addresses"]:
        address_template = Template('$address1, $city, $state, $country, $postal_code\n')
        addresses_string += address_template.substitute(address1=address["address_1"], city=address["city"], state=address["state_province"], country=address["country"], postal_code=address["postal_code"])

    # loop through schedule info to get schedule list
    if ("resource_schedule" in hit):
        for time in hit["resource_schedule"]:
            schedule_template = Template('$day: Open from $opens_at to $closes_at\n')
            schedule_string += schedule_template.substitute(day=time["day"], opens_at=(str(time["opens_at"])[:-2]+':'+str(time["opens_at"])[-2:]), closes_at=(str(time["closes_at"])[:-2]+':'+str(time["closes_at"])[-2:]))        
    else:
        for time in hit["schedule"]:
            schedule_template = Template('$day: Open from $opens_at to $closes_at\n')
            schedule_string += schedule_template.substitute(day=time["day"], opens_at=(str(time["opens_at"])[:-2]+':'+str(time["opens_at"])[-2:]), closes_at=(str(time["closes_at"])[:-2]+':'+str(time["closes_at"])[-2:]))

    # loop through phone #s if they exist
    if ("phones" in hit):
        for number in hit["phones"]:
            phone_template = Template('$number - $service_type')
            phone_string += phone_template.substitute(**number)
        
    template_string = "The service name is {name}.\nHere is a description of the service it offers:\n{long_description}\nThe following are the required documents to receive the service:\n{required_documents}\nThe fee is {fee}.\nHere is the information for the application process:\n{application_process}\nThis is an email to contact them: {email}\nThe service provides the following interpretation services:\n{interpretation_services}\nHere is the website: {url}\nIs there a wait time: {wait_time}\nIt may also be known as its alternate name, {alternate_name}.\nHere are the addresses associated with the service:\n{address_string}\nThe service provides services under the following categories: \n{categories}\nIt has the following eligibility category requirements: {eligibility}\nHere are the service's phone numbers: {phone}\nHere are instructions associated with the service: {instructions}.\nHere are the hours for the service:\n{schedule_string}\n------------------------------------------------------------\n"

    return template_string.format_map(Default(**hit, address_string=addresses_string, schedule_string=schedule_string, phone=phone_string))

# create text file to write text data to
with open('llmtext_data.txt', 'w') as f:
    for hit in data["hits"]:
        f.write(data_to_string(hit, addresses_string, schedule_string, phone_string).format_map(Default(**hit, address_string=addresses_string, schedule_string=schedule_string, phone=phone_string)))

f.close()