from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from app.core.config import settings

agent = create_agent(
    model=ChatOpenAI(
        api_key=settings.dashscope_api_key,
        base_url=settings.dashscope_base_url,
        model=settings.dashscope_model,
    ),
    tools=[],
    system_prompt="你是一个聊天助手，可以回答用户问题"
)


res = agent.invoke({
    "messages":[
        {"role":"user", "content":"明天合肥的天气如何?"},
    ]
})

print(res)