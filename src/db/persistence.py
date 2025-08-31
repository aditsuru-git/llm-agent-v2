import os
from pymongo import MongoClient
from langchain_core.messages import message_to_dict, messages_from_dict
from src.state import AgentState

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("MONGO_DB_NAME", "langgraph_chat_db")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION", "conversations")
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
conversations_collection = db[COLLECTION_NAME]
MY_FIXED_SESSION_ID = os.getenv("SESSION_ID", "my_personal_chatbot_session")


def save_state_to_mongodb(current_state: AgentState):
    if "messages" not in current_state:
        raise ValueError("current_state must have a 'messages' key")

    state_dict = {"messages": [message_to_dict(m) for m in current_state["messages"]]}

    conversations_collection.update_one(
        {"_id": MY_FIXED_SESSION_ID},
        {"$set": state_dict},
        upsert=True,
    )


def load_state_from_mongodb() -> AgentState:
    record = conversations_collection.find_one({"_id": MY_FIXED_SESSION_ID})
    if record and "messages" in record:
        loaded_messages = messages_from_dict(record["messages"])
        return {"messages": loaded_messages}
    return {"messages": []}


def clear_history_from_mongodb() -> None:
    conversations_collection.delete_one({"_id": MY_FIXED_SESSION_ID})
