from elasticsearch import Elasticsearch, helpers
import csv

INDEX = "cv-transcriptions"
CSV_FILEPATH = "./cv-valid-dev.csv"

es = Elasticsearch(hosts=['http://localhost:9200'])

mapping = {
    "mappings": {
        "properties": {
            "generated_text": {"type": "text"},
            "duration": {"type": "float"},
            "age": {"type": "keyword"},
            "gender": {"type": "keyword"},
            "accent": {"type": "keyword"},
            "filename": {"type": "keyword"},
            "text": {"type": "text"},
            "up_votes": {"type": "integer"},
            "down_votes": {"type": "integer"}
        }
    }
}

es.indices.create(index=INDEX, body=mapping)
print(f"created index {INDEX} with mapping.")

with open(CSV_FILEPATH, newline='', encoding='utf-8') as csvf:
    reader = csv.DictReader(csvf)
    actions = []

    for row in reader:
        if "duration" in row and row["duration"].strip():
            try:
                row["duration"] = float(row["duration"])
            except ValueError:
                row["duration"] = None

        for vote_field in ["up_votes", "down_votes"]:
            if vote_field in row and row[vote_field].isdigit():
                row[vote_field] = int(row[vote_field])
            else:
                row[vote_field] = 0

        actions.append({"_index": INDEX, "_source": row})

    if actions:
        helpers.bulk(es, actions)
        print("data is ingested into index")