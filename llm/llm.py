from langchain_openai import ChatOpenAI

base_url = 'https://ark.cn-beijing.volces.com/api/v3'
model_name = 'kimi-k2-thinking-251104'
api_key = 'xxx'


base_llm = ChatOpenAI(
    model_name=model_name,
    temperature=0.1,
    base_url=base_url,
    api_key=api_key,
)
