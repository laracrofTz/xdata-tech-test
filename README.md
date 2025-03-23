# xData test documentation

## Task 2

### Task 2C
Install ffmpeg into the system.

**Windows**: Download from official ffmpeg website (https://www.ffmpeg.org/), Add ffmpeg into system path \
**Ubuntu/Linux**: ``` sudo apt install ffmpeg ``` \
**MacOS**: ``` brew install ffmpeg ```

To start server, run
```
python3 asr_api.py
```

Test command:
```shell
curl -F 'file=@/home/advaitaa/cv-valid-dev/sample-000000.mp3' http://localhost:8001/asr
```

### Task 2D
Based on the requirement, I assumed that the asr api only accepts a single file input param. Hence, I did not implement batch inference. (But if I were to implement batch inference, I would change the api to accept multiple files). Due to this, the processing of the files were slow, even though I used multi-threading to parallelise the api calls.

To run the flask server in a multi threaded way, I used gunicorn since Flask by defult can only serve 1 request at a time and for 4000+ files that is not ideal. gunicorn can be used in Linux/Mac but for Windows it needs WSL and cannot run directly on Windows.

I have 8 CPU cores, and to not max out the cores, I decided to start it with 3 worker processes that can handle 2 threads in parallel so it is 6 total requests. --preload loads the model before forking the workers. --timeout gives enough time for slow or large audio files.

1. To start the server, run
```
gunicorn -w 3 --threads 2 -b 0.0.0.0:8001 asr_api:app --preload --timeout 180
```
2. Then run
```
python3 cv-decode.py
```

### Task 2E
1. Run the following in asr directory to build the container.
```
docker-compose up --build -d
```
2. Once container successfully runs, you can run the curl command or the python script to transcribe files.

## Task 3
Details of the architecture are explained in the pdf document.

## Task 4
1. Created a dockerfile to run the python script to create the index (if it doesnt exist) and ingest the data from csv to elastic-search container.
2. Run to start 2 node cluster elasticsearch services.
```
docker-compose up -d
```

#### Micellaneous (used to test via postman):
- To verify if cv-transcriptions index is created, run
```
http://localhost:9200/_cat/indices
```
- To verify if the documents exist in the index, run
```
http://localhost:9200/cv-transcriptions/_search
```
- To verify mapping of the index, run
```
http://localhost:9200/cv-transcriptions/_mapping?pretty
```

## Task 5
### How I did the setup before containerisation (just FYI):
1. Download search-ui starter app:
```
curl https://codeload.github.com/elastic/app-search-reference-ui-react/tar.gz/master | tar -xz
 ```
2. Run ``` npm i ``` to install dependencies
3. Modify App.js according to my requirements. Used elastic search connector since the documentation has mentioned that App Search is deprecated.
4. Removed config folder as it is more relevant for App Search.

### After containerisation:
I used port 3001 instead of 3000 because there was some process running on it that I could not kill no matter what I tried.
1. Run to build the docker and docker compose files.
```
docker-compose up --build
```
2. Access the frontend site at ``` http://localhost:3000 ``` (**Only for local dev!!**)
3. Used nginx to serve the static frontend assets.
4. The user can search for any word/text in the main search bar and once they click search, they can see the results. Else, if they want to filter and search, they can select the facets at the left hand side of the screen to filter through factors like age, gender, accent and duration.
5. Here is a screenshot of what it looks like in local development: ![alt text](search-ui/search-ui-ss.png)

## Task 6
There were a few changes made to my docker-compose files when I was deploying.

**Errors**
1. Initially the JVM memory was set to 512MB when I was testing locally. However, for deployment, the aws t2.micro instance has only 1 GB of memory. So I changed the initial heap size to 128MB.
2. But then I kept getting the ``` java.lang.OutOfMemoryError: Java Heap Space ``` error. This was because Elasticsearch was trying to grab larger heap memory than what was available.
3. Hence, I had to add this ```"ES_JAVA_OPTS=-Xms128m -Xmx128m -XX:MaxDirectMemorySize=64m"``` which told Elasticsearch to only use 128MiB for heap and 64MiB for direct memory, which allowed the container to stay within the available memory limits.

**HTTPS**
1. Use Nginx as a reverse proxy to listen for HTTPs connections on port 443.
2. I ran the following command in the ec2 instance to generate a self signed ssl cert (but did not push the certs to git repo).
```
mkdir -p nginx/certs
openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout nginx/certs/selfsigned.key \
  -out nginx/certs/selfsigned.crt \
  -subj "/C=US/ST=NA/L=NA/O=Dev/OU=Dev/CN=localhost"
```

## Task 7
**Deployment URL**:  https://3.27.69.234

## Task 8
Refer to essay.pdf.
## References
1. ffmpeg audio file conversion and resampling: https://stackoverflow.com/questions/67880409/ffmpeg-how-to-resample-audio-file
2. Soundfile python library: https://python-soundfile.readthedocs.io/en/0.13.1/#
3. Gunicorn: https://flask.palletsprojects.com/en/stable/deploying/gunicorn/
4. Thread Pool Executor Python: https://docs.python.org/3/library/concurrent.futures.html
5. Index, documents, fields Elasticsearch: https://www.elastic.co/guide/en/elasticsearch/reference/current/documents-indices.html
5. Data ingestion into Elastic Search Backend: https://betterstack.com/community/questions/import-csv-into-elasticsearch/, https://theaidigest.in/load-csv-into-elasticsearch-using-python/
6. Python icon: https://www.flaticon.com/free-icons/python
7. Search-UI: https://www.elastic.co/guide/en/search-ui/current/overview.html
8. Elasticsearch Guide: https://medium.com/data-science/mastering-elasticsearch-a-beginners-guide-to-powerful-searches-and-precision-part-1-87686fec9808
9. Elasticsearch Mapping: https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html
10. Max virtual memory error: https://stackoverflow.com/questions/51445846/elasticsearch-max-virtual-memory-areas-vm-max-map-count-65530-is-too-low-inc/51447991#51447991
11. Nginx: https://medium.com/@sstarr1879/serving-the-default-nginx-homepage-using-a-reverse-proxy-in-a-docker-container-ubuntu-2bc0a822f662
12. Deploying multi container applications on aws: https://medium.com/@mudasirhaji/how-to-deploy-multiple-application-containers-using-docker-compose-on-amazon-ec2-367e39437fbd
14. Javalang out of memory: https://sarasagunawardhana.medium.com/java-lang-outofmemoryerror-java-heap-space-on-elasticsearch-in-aws-911d81abd71e, https://stackoverflow.com/questions/27359885/elasticsearch-outofmemoryerror-java-heap-space
