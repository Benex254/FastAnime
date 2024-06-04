import os

import yaml


class YamlParser:
    """makes managing yaml files easier"""

    data = {}

    def __init__(self, file_path: str, default, data_type):
        self.file_path: str = file_path
        self.data: data_type
        if os.path.exists(file_path):
            try:
                with open(self.file_path, "r") as yaml_file:
                    self.data = yaml.safe_load(yaml_file)
            except Exception:
                self.data = default
                with open(file_path, "w") as yaml_file:
                    yaml.dump(default, yaml_file)
        else:
            self.data = default
            with open(file_path, "w") as yaml_file:
                yaml.dump(default, yaml_file)

    def read(self):
        with open(self.file_path, "r") as yaml_file:
            self.data = yaml.safe_load(yaml_file)
            return self.data

    def write(self, new_obj):
        with open(self.file_path, "w") as yaml_file:
            yaml.dump(new_obj, yaml_file)
