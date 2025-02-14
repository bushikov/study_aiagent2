# LangGraphのチュートリアルやってみた
- [LangGraph公式チュートリアル](https://langchain-ai.github.io/langgraph/tutorials/introduction/)

ライブラリのインストール
```shell
pip install langgraph langchain-google-genai
```

実行
```shell
export GOOGLE_API_KEY="hogehogehoge"
python ~.py
```

## ファイル
- try001.py：基礎的なチャットボット
    - [Part 1: Build a Basic Chatbot](https://langchain-ai.github.io/langgraph/tutorials/introduction/#part-1-build-a-basic-chatbot)
- try002.py：ツールを使用できるようにしたチャットボット
    - 追加ライブラリのインストール
        ```shell
        pip install duckduckgo-search langchain_community
        ```
    - [Part 2: Enhancing the Chatbot with Tools](https://langchain-ai.github.io/langgraph/tutorials/introduction/#part-2-enhancing-the-chatbot-with-tools)
    - [LangChainでのDuckDuckGoの使い方](https://python.langchain.com/docs/integrations/tools/ddg/)
    - __キーワード__
        - bind_tools()
        - ToolNode
        - tools_condition
- try003.py：会話履歴を記憶できるチャットボット
    - [Part 3: Adding Memory to the Chatbot](https://langchain-ai.github.io/langgraph/tutorials/introduction/#part-3-adding-memory-to-the-chatbot)
    - 記憶方法として、インメモリセーバーだけでなく、SqliteセーバーやPostgreセーバーなどもある
    - __キーワード__
        - MemorySaver
        - checkpointer in StateGraph().compile
- try004.py：Human-in-the-loop
    - 指定のノード実行前や実行後に処理を止め、人がそれまでの処理結果などを確認できる
    - [Part 4: Human-in-the-loop](https://langchain-ai.github.io/langgraph/tutorials/introduction/#part-4-human-in-the-loop)
    - __キーワード__
        - interrupt_before in StateGraph().compile
        - interrupt_after in StateGraph().compile
- try005.py：処理途中で状態を更新する（メッセージの追加）
    - [Part 5: Manually Updating the State](https://langchain-ai.github.io/langgraph/tutorials/introduction/#part-5-manually-updating-the-state)
    - __キーワード__
        - interrupt_before in StateGraph().compile
        - interrupt_after in StateGraph().compile
        - update_state
- try005b.py：処理途中で状態を更新する（既存メッセージの更新）
    - [What if you want to overwrite existing messages?](https://langchain-ai.github.io/langgraph/tutorials/introduction/#what-if-you-want-to-overwrite-existing-messages)
    - __キーワード__
        - interrupt_before in StateGraph().compile
        - interrupt_after in StateGraph().compile
        - update_state
- try006.py：状態のカスタマイズ
    - [Part 6: Customizing State](https://langchain-ai.github.io/langgraph/tutorials/introduction/#part-6-customizing-state)
- try007.py：
    - [Part 7: Time Travel](https://langchain-ai.github.io/langgraph/tutorials/introduction/#part-7-time-travel)
    - __キーワード__
        - get_state_history