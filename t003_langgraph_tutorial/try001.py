from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_google_genai import ChatGoogleGenerativeAI

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

llm = ChatGoogleGenerativeAI(temperature=0, model="gemini-1.5-flash")

# ノードを関数で定義
def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

graph_builder.add_node("chatbot", chatbot)

# エントリーポイントとエンドポイントを指定
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

# 実行
graph = graph_builder.compile()

# グラフのビジュアライズ
#   たぶんJupyter notebookとかで実行する必要がありそう
# from IPython.display import Image, display
#
# try:
#     display(Image(graph.get_graph().draw_mermaid_png()))
# except Exception:
#     pass

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
        # fallback if input() is not available
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break