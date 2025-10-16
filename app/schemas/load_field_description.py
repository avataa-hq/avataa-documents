from os import path
import json

parent_dir = path.dirname(path.abspath(__file__))
with open(path.join(parent_dir, "field_description.json"), "r") as file:
    field_description = json.load(file)
