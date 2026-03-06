import json
import yaml

#open .ndjson file and save as json and yaml

with open("tracking_log.ndjson", "r") as f:
    lines = f.readlines()
    json_data = [json.loads(line) for line in lines]
with open("tracking_log.json", "w") as f:
    json.dump(json_data, f, indent=2, ensure_ascii=False)
with open("tracking_log.yaml", "w") as f:
    yaml.dump(json_data, f, allow_unicode=True)