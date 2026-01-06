import json

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from llm import base_llm
from tools import search_tool, sum_tool
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langgraph.graph import StateGraph, START, END

# 定义状态结构
class State(TypedDict):
    messages: Annotated[list, add_messages]


tools = [search_tool, sum_tool]
llm_with_tools = base_llm.bind_tools(tools)


# 定义LLM处理节点
def llm_node(state: State) -> State:
    response_chunks = []

    print("\n[llm节点流式输出] >>>>>>>>>>>>>>>>>")
    for chunk in llm_with_tools.stream(state["messages"]):
        # 流式输出过程信息
        if hasattr(chunk, 'content') and chunk.content:
            print(f"{chunk.content}", end="", flush=True)
        response_chunks.append(chunk)
    print("\n<<<<<<<<<<<<<<<<< [llm节点流式输出结束]")

    # 合并所有响应块
    if response_chunks:
        full_response = response_chunks[0]
        for chunk in response_chunks[1:]:
            full_response = full_response + chunk
    else:
        from langchain_core.messages import AIMessage
        full_response = AIMessage(content="")
    return {"messages": [full_response]}


# 定义工具执行节点
def tool_executor_node(state: State) -> State:
    last_message = state["messages"][-1]
    tool_calls = last_message.tool_calls

    results = []
    for call in tool_calls:
        tool_name = call["name"]
        tool_args = call["args"]

        if tool_name == "search_tool":
            tool_instance = search_tool
        elif tool_name == "sum_tool":
            tool_instance = sum_tool
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

        result = tool_instance.invoke(tool_args)
        results.append({
            "tool_call_id": call["id"],
            "content": str(result)
        })

    return {"messages": [ToolMessage(content=result["content"], tool_call_id=result["tool_call_id"]) for result in results]}


# 工具执行条件
def tools_condition(state: State) -> str:
    last_message = state["messages"][-1]
    if not last_message.tool_calls:
        return "__end__"
    return "tools"


# 自定义消息编码器
class MessageEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'dict'):
            return obj.dict()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        return super().default(obj)


def run(user_input: str):
    # 构建状态图
    workflow = StateGraph(State)

    # 添加节点
    workflow.add_node("llm", llm_node)
    workflow.add_node("tools", tool_executor_node)

    # 添加普通边，以及条件边
    workflow.add_edge(START, "llm")
    workflow.add_conditional_edges(
        "llm",
        tools_condition,
        {
            "tools": "tools",
            "__end__": END
        }
    )
    workflow.add_edge("tools", "llm")

    # 编译图
    app = workflow.compile()

    # 执行
    invoke_messages = {
        "messages": [
            # SystemMessage(content="your system prompt"),
            HumanMessage(content=user_input)
        ]
    }

    for state_update in app.stream(invoke_messages):
        state_update_json = json.dumps(state_update, cls=MessageEncoder, ensure_ascii=False)
        print(f"Graph状态更新:\n {state_update_json}")
