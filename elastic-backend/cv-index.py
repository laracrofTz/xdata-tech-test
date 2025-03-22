from elasticsearch import Elasticsearch, helpers
import csv

INDEX = "cv-transcriptions"
CSV_FILEPATH = "./cv-valid-dev.csv"

es = Elasticsearch(hosts=['http://localhost:9200'])

with open(CSV_FILEPATH) as csvf:
    reader = csv.DictReader(csvf)
    helpers.bulk(es, reader, index=INDEX)