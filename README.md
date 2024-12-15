# AI_NEWS_EDITOR
### Your News Editor Powered by RAG and gemini

### Set your API Key for gemini

1. Go to Google AI Studio
2. Create An API KEY for your usage 
3. Put your API KEY in the `ASK_LLM_websocket_server.py` and `vector_dump_websocket_server.py` script
4. Create conda environment using `requirements.txt`
5. Activate conda environment

#### Open three different terminal
#### RUN 
`python3 ASK_LLM_websocket_server.py`
#### RUN
`python3 vector_dump_websocket_server.py`
#### Finally RUN
`streamlit run streamlit_chatbox.py`

#### If there exit data in Chroma DB then just go to the chatbox and start asking questions

### FOR SCAPING AND DUMPING NEW DATA INTO Chroma DB

Select a date from the calender in the sidebar
Now Click on button named `Dump into VectorDB`
You will see message upcomimg stating the current process going on

#### if you cannot find relevant answer for very recent inserted documents then Re-RUN. 
`python3 vector_dump_websocket_server.py`

#### Otherwise it would not be necessary.
### NOW ASK YOUR QUESSION IN THE CHATBOX