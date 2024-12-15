#!/usr/bin/env python

"""Echo server using the asyncio API."""
import datetime

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from sqlalchemy.orm.collections import collection
import os

if "GOOGLE_API_KEY" not in os.environ:
    #os.environ["GOOGLE_API_KEY"] = "AIzaSyDaYK68BjSZL4TL08sm6hbx27yB5EZWqg0"
    os.environ["GOOGLE_API_KEY"] = "AIzaSyC0Bse9MriADspLnHVVwnfKfSUwnojvDJI"

#llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest")
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-002")

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import os
import logging
import gc
import chromadb
import asyncio
import time
import json
from websockets.asyncio.server import serve

persist_directory = 'News_Assistant/chroma/'
os.makedirs(persist_directory, exist_ok=True)
embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")


template = """

I am your news presenter. I give you the news you are searching for and mostly focused on Bangladesh.
Here's a detailed guide for your interactions:
Accurate Historical Information: When users ask about any person's identity, statement,current status, any report on any organization, bussiness group or any entity, activity of any subject, ensure your answers are factually accurate and based on the provided timeline and background information.
Your Perspective: Answer questions as a news presenter, using the first person ("I"). Convey his thoughts, understanding.
Respect and Sensitivity: Always maintain a respectful tone, act like telling a story.
Engaging Storytelling: Use vivid language and descriptive details based on information provided.
Few-shot Learning Examples:
Question 1: What is the capital of India?
Answer: New Delhi is the capital of India.
Question 2: Who is the president of India?
Answer: Narendra Modi is the president of India.
Question 3: What is the capital of China?
Answer: Beijing is the capital of China.
{context}
Question: {question}

Helpful Answer:"""




date = datetime.date.today()
log_dir = f"LLM_OUT_LOG/{date}"
os.makedirs(log_dir, exist_ok=True)

# Set paths for log and output files with timestamp
log_filename = f"{log_dir}/{date}_logs.log"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class my_croma():

    def __init__(self):
        self.a = 1
        pass

    def init_DB(self,collection_name):

        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=embedding,
            persist_directory=persist_directory,  # Where to save data locally, remove if not necessary
        )
        return vector_store

        # persistent_client = chromadb.PersistentClient()
        # collection = persistent_client.get_or_create_collection("collection_name")
        # return collection

    def insert_DB(self,splited_docs,collection_name):

        vectordb = Chroma.from_documents(
            collection_name= collection_name,
            documents=splited_docs,
            embedding=embedding,
            persist_directory=persist_directory
        )

        return vectordb

QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

def GET_QA_CHAIN (collection_name):

    # Step 4: Create the QA chain
    my_vector_db = my_croma().init_DB(collection_name=collection_name)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=my_vector_db.as_retriever(k=20),
        return_source_documents=True,
        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
    )

    return qa_chain

def init_QA_CHAIN (collection_name):

    global qa_chain

    qa_chain = GET_QA_CHAIN(collection_name)

    #return qa_chain

def ASK_LLM (question):

    #qa_chain = GET_QA_CHAIN()
    #print("QS :: ", question)
    logging.info(msg=question)
    result = qa_chain({"query": question})

    #print("LLM RES \n ",result["result"])
    logging.info(msg=result["result"])
    return result["result"]


#init_QA_CHAIN(collection_name='test')
async def echo(websocket):
    async for message in websocket:

        message = json.loads(message)
        action = message['action']
        collection_name = message['date']
        init_QA_CHAIN(collection_name=collection_name)
        llm_answer = ASK_LLM(question=message['QS'])

        if action == "close":
            break

        await websocket.send(llm_answer)
        # await websocket.send("END ......")
        # await websocket.send("END ......")
        # await websocket.send("END ......")
        await websocket.send("close")


async def main():
    async with serve(echo, "localhost", 8765,ping_interval=None) as server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())