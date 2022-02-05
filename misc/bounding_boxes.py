import csv
import json

with open("data/bounding_boxes.csv", 'r') as f:
    bounding_boxes = csv.DictReader(f)

    bounding_boxes_dict = dict()

    for row in bounding_boxes:
        country_name = row['country']
        bounding_boxes_dict[country_name] = {
            "lat": [row['latmin'], row['latmax']],
            "long": [row['longmin'], row['longmax']]
        }
    
with open("data/bounding_boxes.json", 'w') as f:
    json.dump(bounding_boxes_dict, f, indent=4)