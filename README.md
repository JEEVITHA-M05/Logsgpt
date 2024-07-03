# Logsgpt
Logsgpt is an advanced data streaming project that leverages Windows logs for data ingestion.
Utilizing Winlogbeat and Logstash, the project efficiently ingests data and stores it in Elasticsearch.
For data visualization, Kibana is used, providing comprehensive insights into the logs.
The project incorporates Hugging Face's BGE Large embedding modelto embed logs, which are then
stored in Elasticsearch as indexes. Retrieval-Augmented Generation (RAG) is employed to process
and provide log information to a Large Language Model (LLM). The frontend is built using the ChainLit
framework, enabling users to interact and query log data seamlessly. Python is used as the primary
programming language for this project. Additionally, project tracing is facilitated by Langsmith from
Langchain
