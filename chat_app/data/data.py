
# parse json file
import json
import os
from string import Template

# from .llmstring_data import data_to_string

DEFAULT_DATA_PATH = "chat_app/data/COMBINED_DATA.json"
DEFAULT_CATEGORIES_PATH = "chat_app/data/categories_edited.json"


def parse_json_file(file_path):
    with open(file_path) as json_file:
        data = json.load(json_file)
        return data


class Default(dict):
    def __missing__(self, key):
        return 'N/A'


def data_to_string(hit, addresses_string, schedule_string, phone_string):
    # loop through addresses list for a list of addresses associated with service
    for address in hit["addresses"]:
        address_template = Template(
            '$address1, $city, $state, $country, $postal_code\n')
        addresses_string += address_template.substitute(address1=address["address_1"], city=address["city"],
                                                        state=address["state_province"], country=address["country"], postal_code=address["postal_code"])

    # loop through schedule info to get schedule list
    if ("resource_schedule" in hit):
        for time in hit["resource_schedule"]:
            schedule_template = Template(
                '$day: Open from $opens_at to $closes_at\n')
            schedule_string += schedule_template.substitute(day=time["day"], opens_at=(str(time["opens_at"])[:-2]+':'+str(
                time["opens_at"])[-2:]), closes_at=(str(time["closes_at"])[:-2]+':'+str(time["closes_at"])[-2:]))
    else:
        for time in hit["schedule"]:
            schedule_template = Template(
                '$day: Open from $opens_at to $closes_at\n')
            schedule_string += schedule_template.substitute(day=time["day"], opens_at=(str(time["opens_at"])[:-2]+':'+str(
                time["opens_at"])[-2:]), closes_at=(str(time["closes_at"])[:-2]+':'+str(time["closes_at"])[-2:]))

    # loop through phone #s if they exist
    if ("phones" in hit):
        for number in hit["phones"]:
            phone_template = Template('$number - $service_type')
            phone_string += phone_template.substitute(**number)

    template_string = "The service name is {name}.\nHere is a description of the service it offers:\n{long_description}\nThe following are the required documents to receive the service:\n{required_documents}\nThe fee is {fee}.\nHere is the information for the application process:\n{application_process}\nThis is an email to contact them: {email}\nThe service provides the following interpretation services:\n{interpretation_services}\nHere is the website: {url}\nIs there a wait time: {wait_time}\nIt may also be known as its alternate name, {alternate_name}.\nHere are the addresses associated with the service:\n{address_string}\nThe service provides services under the following categories: \n{categories}\nIt has the following eligibility category requirements: {eligibility}\nHere are the service's phone numbers: {phone}\nHere are instructions associated with the service: {instructions}.\nHere are the hours for the service:\n{schedule_string}\n------------------------------------------------------------\n"

    return template_string.format_map(Default(**hit, address_string=addresses_string, schedule_string=schedule_string, phone=phone_string))


class DataSet:
    def __init__(self, dataPath):
        self.dataPath = dataPath
        self.data = parse_json_file(dataPath)
        self.categories_map = parse_json_file(DEFAULT_CATEGORIES_PATH)

        self.id_to_service = {}
        self.category_to_services = {}
        self.eligibilities_to_services = {}

        self._transform_data()

    def _transform_data(self):
        try:
            self.categories = []
            self.categories_to_querycat = {}
            self.querycat_to_category = {}
            for cats in self.categories_map.values():
                self.categories.extend(cats.keys())

                for cat, querycats in cats.items():
                    if cat not in self.categories_to_querycat:
                        self.categories_to_querycat[cat] = []
                    querycats = [cat] if querycats == [] else querycats
                    self.categories_to_querycat[cat].extend(querycats)
                    self.querycat_to_category.update(
                        {qcat: cat for qcat in querycats})
                    # initialized herexws
                    self.category_to_services[cat] = []

            self.eligibilities = self.data["facets"]["eligibilities"]
            self.supercategories = list(self.categories_map.keys())

        except KeyError:
            print(
                "Error: trouble getting categories, eligitibilites or subcategories from data")

        for service in self.data["hits"]:
            id = service["id"]
            self.id_to_service[id] = service

            query_cats = service["categories"]
            for qcat in query_cats:
                if (qcat not in self.querycat_to_category):
                    # TODO: we ignore anything that's in categories.json that's not in the dataset. we should make it consistent
                    continue

                category = self.querycat_to_category[qcat]
                if (category not in self.category_to_services):
                    self.category_to_services[category] = []
                self.category_to_services[category].append(id)

            eligibilities = service["eligibilities"] if "eligibilities" in service else [
            ]
            for elig in eligibilities:
                if elig not in self.eligibilities_to_services:
                    self.eligibilities_to_services[elig] = []
                self.eligibilities_to_services[elig].append(id)

    def get_all_services(self):
        return self.data["hits"] if "hits" in self.data else []

    def get_service_by_id(self, id):
        return self.id_to_service[id] if id in self.id_to_service else None

        # add string template for each service id
    def get_service_string(self, ids):
        # define a class for Default values if key does not exist
        class Default(dict):
            def __missing__(self, key):
                return 'N/A'

        addresses_string = ""
        schedule_string = ""
        phone_string = ""

        string_template = ""

        for id in ids:
            service = self.id_to_service[id]
            string_template += data_to_string(service,
                                              addresses_string, schedule_string, phone_string)

        return string_template

    def get_all_supercategories(self):
        return self.supercategories

    def get_all_categories(self):
        return self.categories

    def get_all_eligibilities(self):
        return self.eligibilities

    def get_eligibilities_for_service(self, service_id):
        service = self.get_service_by_id(service_id)
        return service["eligibilities"] if service and "eligibilities" in service else []

    def get_services_for_category(self, category):
        return self.category_to_services[category] if category in self.category_to_services else []

    def get_all_eligibilities_for_categories(self, categories):
        eligibilities = []
        for category in categories:
            services = self.get_services_for_category(category)
            for service_id in services:
                eligibilities.extend(
                    self.get_eligibilities_for_service(service_id))
        return list(set(eligibilities))

    def get_all_categories_for_supercategories(self, supercategories):
        categories = []
        for sup in supercategories:
            categories.extend(
                list(self.categories_map[sup].keys()) if sup in self.categories_map else [])
        return list(set(categories))

    def get_categories_for_supercategory(self, supercategory):
        return self.categories_map[supercategory].keys() if self.is_valid_supercategory(supercategory) else []

    def get_ordered_list_of_categories(self, categories):
        return sorted(categories, key=lambda cat: len(self.category_to_services[cat]), reverse=True)

    def get_ordered_list_of_eligibilities(self, categories):
        potential_elig = self.get_all_eligibilities_for_categories(categories)
        return sorted(potential_elig, key=lambda elig: len(self.eligibilities_to_services[elig]), reverse=True)

    def get_candidate_services(self, categories, eligibilities):
        cand_services = []
        for cat in categories:
            cand_services.extend(self.category_to_services[cat])

        eligible_services = []
        for cand_id in cand_services:
            serv = self.get_service_by_id(cand_id)
            if serv:
                required_elig = self.get_eligibilities_for_service(cand_id)
                if any(e in required_elig for e in eligibilities):
                    eligible_services.append(cand_id)

        return eligible_services, cand_services

    def is_valid_supercategory(self, supercategory):
        return supercategory in self.supercategories

    def is_valid_category(self, category):
        return category in self.categories

    def is_valid_eligibity(self, eligibility):
        return eligibility in self.eligibilities


if __name__ == '__main__':
    dataset = DataSet(DEFAULT_DATA_PATH)
    print(list(map(lambda item: [item[0], item[1]
          ["name"]], dataset.id_to_service.items())))
