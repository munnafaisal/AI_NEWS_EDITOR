import streamlit as st
import datetime
import asyncio
from websockets.asyncio.client import connect
import json
import random
import time
import requests


url = 'http://localhost:8000/test_api/'
insert_vc_url = 'http://localhost:8000/write_to_vector_DB/'

event = {'action': "scrap", "name": "new age", "date": "test", "QS": "who are you?"}

# Streamed response emulator
def response_generator():
    response = random.choice(
        [
            "Hello there! How can I assist you today?",
            "Hi, human! Is there anything I can help you with?",
            "Do you need help?",
        ]
    )
    for word in response.split():
        yield word + " "
        time.sleep(0.05)

reply = " hello....??  "
async def hello(my_event):
    global reply
    async with connect("ws://localhost:8765") as websocket:
        await websocket.send(json.dumps(my_event))
        while True:
            message = await websocket.recv()
            print(message)
            reply = reply + message
            if message == "close":
                #print(message)
                websocket.close()
                break

st.title("Simple chat")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    myobj = {"name": "7BcYJsSF57t6GDYo5", "QS":prompt}
    # Display assistant response in chat message container
    with st.chat_message("assistant"):

##################  FASTAPI ######################################

        # #response = st.write_stream(response_generator())
        # ans = requests.post(url, json=myobj)
        # print(ans.text)
        # st.write(ans.text)
        # st.session_state.messages.append({"role": "assistant", "content": ans.text})

##################### WEBSOCKETS ########################

        async def hello():
            global reply
            async with connect("ws://localhost:8765", ping_interval=None) as websocket:
                event["QS"] = prompt
                await websocket.send(json.dumps(event))
                while True:
                    message = await websocket.recv()
                    print(message)
                    if message != "close":

                        response = st.write(message)
                        st.session_state.messages.append({"role": "assistant", "content": message})
                    if message == "close":
                        # print(message)
                        await websocket.close()
                        break


        print("Async IO called ....")
        asyncio.run(hello())


##############################################################


with st.sidebar:

    d = st.date_input("Insert Datetime of NEW AGE Archive", value=None)
    # picked_date = d.strftime("%Y-%m-%d")
    # st.write("You have selected the following date :", d)
    if d is not None:

        picked_date = d.strftime("%Y-%m-%d")
        st.write("You have selected the following date :", d)
        payload = {"date":picked_date}
        if st.button("Dump into VectorDB"):

            # ans = requests.post(insert_vc_url, json=payload)
            # response = st.write(ans.text)

            event = {'action': "scrap", "name": "new age", "date": picked_date}


            async def hello():
                async with connect("ws://localhost:6605",ping_interval=None) as websocket:
                    #await websocket.ping(data="hi")
                    await websocket.send(json.dumps(event))

                    while True:

                        message = await websocket.recv()
                        print(message)
                        st.write(message)
                        if message == "close":
                            st.write("Vector dump completed....")
                            websocket.close()
                            break
                        else:
                            st.write(message)

            asyncio.run(hello())

        else:
            pass



