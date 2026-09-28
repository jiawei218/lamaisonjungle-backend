from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.core.config import settings


def main() -> None:
    model = ChatOpenAI(
        api_key=settings.dashscope_api_key,
        base_url=settings.dashscope_base_url,
        model=settings.dashscope_model,
    )

    messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content="你是谁？"),
    ]

    # stream() 会逐块返回模型生成的内容。因为是聊天模型，所以注意使用chunk.content
    for chunk in model.stream(messages):
        if chunk.content:
            print(chunk.content, end="", flush=True)

    print()


if __name__ == "__main__":
    main()
