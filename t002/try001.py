from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(
    temperature=0,
    model="gemini-1.5-flash"
)

# LLMは記憶を持たないので、２つ目の問いに答えられない
#
# res = model.invoke([HumanMessage("Hi! I'm Bob")])
# print(StrOutputParser().invoke(res))
# res = model.invoke([HumanMessage("What's my name?")])
# print(StrOutputParser().invoke(res))
# => As an AI, I do not have access to personal information like your name.  To know your name, you'll need to tell me!

res = model.invoke([
    HumanMessage(content="Hi! I'm Bob."),
    AIMessage(content="Hello Bob! How can I assist you today?"),
    HumanMessage(content="What's my name?"),
])
print(StrOutputParser().invoke(res))
# => You told me your name is Bob!