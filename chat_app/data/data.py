
# parse json file
import json
import os

DEFAULT_DATA_PATH = "chat_app/data/TEMP_DATA.json"


def parse_json_file(file_path):
    with open(file_path) as json_file:
        data = json.load(json_file)
        return data


class DataSet:
    def __init__(self, dataPath):
        self.dataPath = dataPath
        self.data = parse_json_file(dataPath)

        self.id_to_service = {}
        self.category_to_services = {}

        self._transform_data()

    def _transform_data(self):
        try:
            self.categories = self.data["facets"]["categories"]
            self.eligibilities = self.data["facets"]["eligibilities"]
            self.supercategories = self.data["supercategories"]
        except KeyError:
            print(
                "Error: trouble getting categories, eligitibilites or subcategories from data")

        for service in self.data["hits"]:
            id = service["id"]
            self.id_to_service[id] = service

            categories = service["categories"]
            for category in categories:
                if (category not in self.category_to_services):
                    self.category_to_services[category] = []
                self.category_to_services[category].append(id)

    def get_all_services(self):
        return self.data["hits"] if "hits" in self.data else []

    def get_service_by_id(self, id):
        return self.id_to_service[id] if id in self.id_to_service else None

    def get_all_supercategories(self):
        return self.supercategories

    def get_all_categories(self):
        return self.categories

    def get_all_eligibilities(self):
        return self.eligibilities

    def get_categories_for_supercategory(self, supercategory):
        return self.supercategories[supercategory]["categories"]


if __name__ == '__main__':
    dataset = DataSet(DEFAULT_DATA_PATH)
    print(list(map(lambda item: [item[0], item[1]
          ["name"]], dataset.id_to_service.items())))
