# from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.output_parsers import StrOutputParser

# TavilySearchResultsを使う場合（APIキーが必要）
# export TAVILY_API_KEY="hogehogehoge"
# tool = TavilySearchResults(max_results=2)
tool = DuckDuckGoSearchRun()
tools = [tool]

# res = tool.invoke("Where is the capital in Japan?")
# print(StrOutputParser().invoke(res))

from typing import Annotated

from langchain_google_genai import ChatGoogleGenerativeAI
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)

# langgraph.prebuild.ToolNodeでやることを自前で定義するとこんな感じらしい
#
# import json
# from langchain_core.messages import ToolMessage
#
# class BasicToolNode:
#     """A node that runs the tools requested in the last AIMessage."""
#     def __init__(self, tools: list) -> None:
#         self.tools_by_name = {tool.name: tool for tool in tools}
#
#     def __call__(self, inputs: dict):
#         if messages := inputs.get("messages", []):
#             message = messages[-1]
#         else:
#             raise ValueError("No message found in input")
#         outputs = []
#         for tool_call in message.tool_calls:
#             tool_result = self.tools_by_name[tool_call["name"]].invoke(
#                 tool_call["args"]
#             )
#             outputs.append(
#                 ToolMessage(
#                     content=json.dumps(tool_result),
#                     name=tool_call["name"],
#                     tool_call_id=tool_call["id"]
#                 )
#             )
#         return {"messages": outputs}
#
# tool_node = BasicToolNode(tools=tools)
# graph_builder.add_node("tools", tool_node)
from langgraph.prebuilt import ToolNode

tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

# langgraph.prebuild.tools_conditionを自前で定義するとこんな感じらしい
#
# from typing import Literal
#
# def route_tools(state: State):
#     """
#     Use in the conditional_edge to route to the ToolNode if the last message
#     has tool calls. Otherwise, route to the end
#     """
#     if isinstance(state, list):
#         ai_message = state[-1]
#     elif messages := state.get("messages", []):
#         ai_message = messages[-1]
#     else:
#         raise ValueErro(f"No messages found in input state to tool_edge: {state}")
#     if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
#         return "tools"
#     return END
#
# graph_builder.add_conditional_edges(
#     "chatbot",
#     route_tools,
#     # route_toolsの戻り値がどのノードを示すかを指定しているっぽい
#     {"tools": "tools", END: END}
# )
from langgraph.prebuilt import tools_condition
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition
)

graph_builder.add_edge("tools", "chatbot")
# add_conditional_edgeでENDに移動する条件を指定しいるのでchatbotとENDの間のエッジの定義は不要
# graph_builder.add_edge(START, "chatbot")
graph_builder.set_entry_point("chatbot")  # このメソッドでも、START - chatbot間のエッジを指定できるっぽい
graph = graph_builder.compile()


# チャット用関数
def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [("user", user_input)]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)
# チャット開始
while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        stream_graph_updates(user_input)
    except:
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break