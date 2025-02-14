from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()

from typing import Annotated
from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

# TavilySearchResultsを使う場合（APIキーが必要）
# export TAVILY_API_KEY="hogehogehoge"
# tool = TavilySearchResults(max_results=2)
tool = DuckDuckGoSearchResults(backend="lite")
tools = [tool]
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")

graph = graph_builder.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "1"}}
user_input = "Hi there! My name is Will."
events = graph.stream(
    {"messages": [("user", user_input)]},
    config,
    stream_mode="values"
)
for event in events:
    event["messages"][-1].pretty_print()

user_input = "Remember my name?"
events = graph.stream(
    {"messages": [("user", user_input)]},
    # 同じthread_idを指定すると、過去の会話履歴もLLMに渡してくれるらしい
    config,
    stream_mode="values"
)
for event in events:
    event["messages"][-1].pretty_print()

# get_stateメソッドで渡したconfigに関連したstateを取得できる
# snapshot = graph.get_state(config)