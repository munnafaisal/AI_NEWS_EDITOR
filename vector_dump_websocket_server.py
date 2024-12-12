from pydantic import BaseModel
import uvicorn
import asyncio
from news_scraper.scraper_fn import scrap_data
import json
from websockets.asyncio.server import serve
import threading
import traceback


from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.vectorstores import Chroma
import os
import gc
import chromadb
import streamlit as st
import random
import time

persistent_client = chromadb.PersistentClient()

from langchain_community.document_loaders import WebBaseLoader

if "GOOGLE_API_KEY" not in os.environ:
    # os.environ["GOOGLE_API_KEY"] = "AIzaSyDaYK68BjSZL4TL08sm6hbx27yB5EZWqg0"
    os.environ["GOOGLE_API_KEY"] = "AIzaSyC0Bse9MriADspLnHVVwnfKfSUwnojvDJI"
    #os.environ["GOOGLE_API_KEY"] = "AIzaSyADADIp1CBs8Nv44dIgP39ik2mS5QqZCYo"

# Initialize embeddings
embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")


def get_docs(file_path):
    """# CSV Loading"""

    from langchain_community.document_loaders.csv_loader import CSVLoader

    loader = CSVLoader(file_path=file_path, encoding='utf-8')

    data = loader.load()

    return data


def get_doc_spliter(chnk_sz, chnk_olp):
    # Split
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chnk_sz,
        chunk_overlap=chnk_olp
    )
    return text_splitter


# Persist directory for FAISS
persist_directory = 'News_Assistant/chroma/'
os.makedirs(persist_directory, exist_ok=True)

gc.collect()  # Force garbage collection to free memory


class my_croma():

    def __init__(self):
        self.a = 1
        pass

    def init_DB(self, collection_name):
        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=embedding,
            persist_directory=persist_directory,  # Where to save data locally, remove if not necessary
        )
        return vector_store

        # persistent_client = chromadb.PersistentClient()
        # collection = persistent_client.get_or_create_collection("collection_name")
        # return collection

    def insert_DB(self, splited_docs, collection_name):
        vectordb = Chroma.from_documents(
            collection_name=collection_name,
            documents=splited_docs,
            embedding=embedding,
            persist_directory=persist_directory
        )
        vectordb.persist()
        return vectordb


async def send_dump_status(websocket, DB):

    while True:

        time.sleep(2)
        print("dump status :: ", dump_st)
        try:
            if dump_st == "COMP":
                count = DB._collection.count()
                await websocket.send("Current Total number of chunk ::" + str(count))
                await websocket.send("close")
                break
            else:
                if dump_st == "ST":
                    count = DB._collection.count()
                    print("vector dump loop running ....")
                    await websocket.send("Current Total number of chunk ::" + str(count))
        except:
            print(traceback.print_exc())

async def dump_into_vector_DB(news_archive_date,websocket):

    global dump_st
    dump_st = "ST"

    csv_path = 'data/' + str(news_archive_date) + '/' + str(news_archive_date) + '_articles.csv'
    splits = get_doc_spliter(chnk_sz=200, chnk_olp=50).split_documents(get_docs(file_path=csv_path))

    bb_my_vector_db = my_croma()
    init_db = bb_my_vector_db.init_DB(collection_name="test")

    # Define a function to split a list into chunks of a specified size
    def split_list(lst, chunk_size):
        # Use a list comprehension to create chunks
        # For each index 'i' in the range from 0 to the length of the list with step 'chunk_size'
        # Slice the list from index 'i' to 'i + chunk_size'
        return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

    # Define a list of integers from 1 to 15
    # Split the list into chunks of size 3 using the split_list function



    tt1 = threading.Thread(target=run_sync_in_async_dump_fn, args=(websocket, init_db,), name="scrapper thread",
                           daemon=True)
    tt1.daemon = True
    tt1.start()

    print("...............Number of splitted docs ", len(splits))

    new_my_vector_db = my_croma()

    chunk_splits = split_list(splits, 200)

    for chnk in chunk_splits:
        new_my_vector_db.insert_DB(splited_docs=chnk, collection_name="test")

    dump_st = "COMP"

    return "Data dump cpmpleted"

async def send_status(websocket,my_scraper):

    while True:

        time.sleep(1)
        print("loop running ....")
        try:
            if my_scraper.fetch_status == "FT_COMP":
                await websocket.send("scraping completed")
                break
            else:
                await websocket.send(my_scraper.fetch_status)
        except:
            pass

def run_sync_in_async_scraper_fn(websocket, my_scraper):
    asyncio.run(send_status(websocket,my_scraper))

def run_sync_in_async_dump_fn(websocket, DB):
    asyncio.run(send_dump_status(websocket, DB))

async def echo(websocket):

    print("echo was called ....")
    async for message in websocket:

        #message = json.loads(message)['action']
        data = json.loads(message)
        print(data)
        news_archive_date = data['date']

        my_scraper = scrap_data()
        my_scraper.get_date(date=news_archive_date, concurrency=20, output='csv')

        tt1 = threading.Thread(target= run_sync_in_async_scraper_fn, args=(websocket, my_scraper,), name="scrapper thread", daemon=True)
        tt1.daemon = True
        tt1.start()

        await my_scraper.main(1)
        await dump_into_vector_DB(news_archive_date=news_archive_date, websocket=websocket)



async def main():
    async with serve(echo, "localhost", 6605,ping_interval=None) as server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())