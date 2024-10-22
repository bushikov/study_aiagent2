from langserve import RemoteRunnable
from langchain_core.output_parsers import StrOutputParser

remote_chain = RemoteRunnable("http://localhost:8000/chain/")
result = remote_chain.invoke({"language": "italian", "text": "hi"})
print(StrOutputParser().invoke(result))