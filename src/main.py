from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage, ToolMessage
from langgraph.prebuilt import ToolNode
from langchain_google_genai import ChatGoogleGenerativeAI
from google.api_core.exceptions import TooManyRequests
import json

from src.db.persistence import load_state_from_mongodb, save_state_to_mongodb
from src.persona import persona_text
from src.state import AgentState
from src.tools import (
    shell_command_executor_raw,
    read_image,
    read_audio,
    read_video,
    fetch_url,
    current_time,
    calculate,
)
from dotenv import load_dotenv

load_dotenv()

tools = [
    shell_command_executor_raw,
    read_image,
    read_audio,
    read_video,
    fetch_url,
    current_time,
    calculate,
]

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash").bind_tools(
    tools
)  # Using 1.5-flash as it's generally better


def convert_tool_message_if_multimodal(message: ToolMessage) -> ToolMessage:
    """Convert ToolMessage content if it contains multimodal data."""
    try:
        if isinstance(message.content, str):
            content_data = json.loads(message.content)
        elif isinstance(message.content, dict):
            content_data = message.content
        else:
            return message

        if content_data.get("type") == "multimodal":
            return ToolMessage(
                content=content_data["content"], tool_call_id=message.tool_call_id
            )
        elif content_data.get("type") == "error":
            return ToolMessage(
                content=content_data["content"], tool_call_id=message.tool_call_id
            )
        else:
            return message

    except (json.JSONDecodeError, TypeError, KeyError):
        return message


def should_save_multimodal_to_history(message) -> bool:
    """
    Decide if a message with multimodal content should be saved to persistent history.
    We'll save a text-only version to avoid bloating the database.
    """
    return False


def create_text_only_version(message: ToolMessage) -> ToolMessage:
    """
    Create a text-only version of a multimodal ToolMessage for storage.
    """
    try:
        if isinstance(message.content, list):
            text_parts = [
                part.get("text", "")
                for part in message.content
                if part.get("type") == "text"
            ]
            text_content = (
                " ".join(text_parts) if text_parts else "Multimodal content processed"
            )

            return ToolMessage(content=text_content, tool_call_id=message.tool_call_id)
    except:
        pass

    return message


def prepare_messages_for_storage(messages: list) -> list:
    """
    Prepare messages for storage by converting multimodal content to text-only versions.
    """
    storage_messages = []

    for message in messages:
        if isinstance(message, ToolMessage) and isinstance(message.content, list):
            storage_messages.append(create_text_only_version(message))
        else:
            storage_messages.append(message)

    return storage_messages


def llm_call(state: AgentState) -> AgentState:
    """
    Optimized LLM call that handles multimodal content efficiently.
    """
    try:
        system_prompt = SystemMessage(content=persona_text)
        mongo_state = load_state_from_mongodb()

        current_processed = []
        for message in state["messages"]:
            if isinstance(message, ToolMessage):
                converted = convert_tool_message_if_multimodal(message)
                current_processed.append(converted)
            else:
                current_processed.append(message)

        all_messages = [system_prompt] + mongo_state["messages"] + current_processed

        response: AIMessage = llm.invoke(all_messages)

        messages_for_storage = prepare_messages_for_storage(state["messages"])
        new_state = {
            "messages": mongo_state["messages"] + messages_for_storage + [response]
        }
        save_state_to_mongodb(new_state)

        return {"messages": state["messages"] + [response]}

    except TooManyRequests:
        mongo_state = load_state_from_mongodb()
        fallback_response = AIMessage(content="Rate limit hit. Please try again later.")
        messages_for_storage = prepare_messages_for_storage(state["messages"])
        new_state = {
            "messages": mongo_state["messages"]
            + messages_for_storage
            + [fallback_response]
        }
        save_state_to_mongodb(new_state)
        return {"messages": state["messages"] + [fallback_response]}

    except Exception as e:
        mongo_state = load_state_from_mongodb()
        fallback_response = AIMessage(content=f"Error occurred: {str(e)}")
        messages_for_storage = prepare_messages_for_storage(state["messages"])
        new_state = {
            "messages": mongo_state["messages"]
            + messages_for_storage
            + [fallback_response]
        }
        save_state_to_mongodb(new_state)
        return {"messages": state["messages"] + [fallback_response]}


def should_continue(state: AgentState):
    if not state["messages"][-1].tool_calls:
        return "end"
    else:
        return "continue"


# --- Graph setup ---
# This is the most important part of the file. It creates the `app` that cli.py uses.
graph = StateGraph(AgentState)
graph.add_node("llm_call", llm_call)
tool_node = ToolNode(tools=tools)
graph.add_node("tools", tool_node)
graph.set_entry_point("llm_call")
graph.add_conditional_edges(
    "llm_call", should_continue, {"continue": "tools", "end": END}
)
graph.add_edge("tools", "llm_call")
app = graph.compile()
