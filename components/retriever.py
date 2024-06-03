from langchain.vectorstores.elasticsearch import ElasticsearchStore
from components.embedding_model import EmbeddingModel
from dotenv import load_dotenv
from utilities.config import DataConstants
from logger import logger
import os
 

class Retriever:
    @staticmethod
    def get_retriever():
        try:
            data_constants=DataConstants()
            embeddings = EmbeddingModel.initialize_model()
            db = ElasticsearchStore(
                es_url=data_constants.es_url,
                index_name=data_constants.embeddings_index,
                embedding=embeddings,
                es_user=data_constants.es_user,
                es_password=data_constants.es_password,
                strategy=ElasticsearchStore.ApproxRetrievalStrategy(),
            )
            retriever=db.as_retriever(search_type="similarity", search_kwargs={"k": 20})
            return retriever 
        except Exception as e:
            logger.error(f"Error initializing retriever: {e}")
            return None
            