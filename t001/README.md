# LangServeを使ってみた
- https://python.langchain.com/docs/tutorials/llm_chain/#serving-with-langserve

ライブラリのインストール
```shell
pip install fastapi
pip install langchain
pip install langchain-google-genai
pip install "langserve[all]"
```

実行
```shell
python serve.py
```

確認１
- ブラウザで`http://localhost:8000/chain/playground/`にアクセスする
    - 簡単なUIでアプリの確認ができる

確認２
- `python client.py`を実行する