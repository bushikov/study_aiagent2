from typing import Annotated

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchResults
from typing_extensions import TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

class State(TypedDict):
    messages: Annotated[list, add_messages]
    ask_human: bool

# 人を介在させるためのツールの定義
from pydantic import BaseModel

class RequestAssistance(BaseModel):
    """
    Escalate the conversation to an expert.
    Use this if you are unable to assist directly or if the user requires support beyonnd your permissions.
    To use this function, relay the user's 'request' so the expert can provide the right guidance.
    """
    request: str

tool = DuckDuckGoSearchResults(backend="lite")
tools = [tool]
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
# Function Callingで呼び出せるように登録
llm_with_tools = llm.bind_tools(tools + [RequestAssistance])

# 人を介在させるためのツールノードを呼ぶためのフラグ（ask_human）管理を定義
def chatbot(state: State):
    response = llm_with_tools.invoke(state["messages"])
    ask_human = False
    if (
        response.tool_calls
        and response.tool_calls[0]["name"] == RequestAssistance.__name__
    ):
        ask_human = True
    return {"messages": [response], "ask_human": ask_human}

graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", ToolNode(tools=tools))

# 人が介在するノードの追加
from langchain_core.messages import AIMessage, ToolMessage

def create_response(response: str, ai_message: AIMessage):
    return ToolMessage(
        content=response,
        tool_call_id=ai_message.tool_calls[0]["id"]
    )

# 実際に実行されるノードになる関数を定義
# __call__メソッドとかをRequestAssistanceクラスに追加することもできそう？
def human_node(state: State):
    new_messages = []
    if not isinstance(state["messages"][-1], ToolMessage):
        # Typically, the user will have updated the state during the interrupt.
        # If they choose not to, we will include a placeholder ToolMessage to
        # let the LLM continue
        new_messages.append(
            create_response(
                "No response from human",
                state["messages"][-1]
            )
        )
    return {
        "messages": new_messages,
        "ask_human": False
    }

graph_builder.add_node("human", human_node)

# ノードとツールの定義を別々（ツールはクラス定義、ノードは関数定義）にしたので、
# 条件分岐を独自定義している？
def select_next_node(state: State):
    if state["ask_human"]:
        return "human"
    return tools_condition(state)

graph_builder.add_conditional_edges(
    "chatbot",
    select_next_node,
    {"human": "human", "tools": "tools", END: END}
)

graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge("human", "chatbot")
graph_builder.add_edge(START, "chatbot")

memory = MemorySaver()

graph = graph_builder.compile(
    checkpointer=memory,
    interrupt_before=["human"]
)


# 実行
user_input = "I need some expert guidance for building this AI agent. Could you request assistance for me?"
config = {"configurable": {"thread_id": "1"}}
events = graph.stream(
    {"messages": [("user", user_input)]},
    config,
    stream_mode="values"
)
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()

snapshot = graph.get_state(config)
print(snapshot.next)

# エキスパートとしての回答を入力
ai_message = snapshot.values["messages"][-1]
human_response = (
    "We, the experts are here to help! We'd recommend you check out LangGraph to build your agent.",
    "It's much more reliable and extensible than simple autonomous agents."
)
tool_messages = create_response(human_response, ai_message)
graph.update_state(config, {"messages": [tool_messages]})

print(graph.get_state(config).values["messages"])

# 続きを実行
events = graph.stream(None, config, stream_mode="values")
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()