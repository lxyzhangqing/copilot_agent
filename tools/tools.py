from langchain_core.tools import tool
from typing import Dict, Any, List
from pydantic import BaseModel, Field


# 搜索工具的协议定义
class SearchToolInput(BaseModel):
    date: str = Field(
        ...,
        description="查询的日期，格式为YYYY-MM-DD，例如'2024-01-15'，如果没有指定时间，默认'2026-01-05'"
    )
    city: str = Field(
        ...,
        description="查询的城市名称，支持中文城市名，例如'北京'、'上海'、'广州'等"
    )


@tool("search_tool", args_schema=SearchToolInput)
def search_tool(date: str, city: str) -> Dict[str, Any]:
    """搜索工具，用于查询相关信息"""
    # 模拟搜索逻辑
    results = {
        "query": f"时间：{date}, 城市：{city}",
        "result": f"明天{city}天气晴朗，气温24摄氏度，东北风3级",
        "count": 1
    }
    return results


# 求和工具的协议定义
class SumToolInput(BaseModel):
    """对数字列表进行求和计算"""
    numbers: List[int] = Field(
        ...,
        description="要相加的数字列表, 例如: [1,2,3,4]",
        items={
            "description": "待求和的整型数字"
        }
    )


@tool("sum_tool", args_schema=SumToolInput)
def sum_tool(numbers: List[int]):
    result = 0
    for i in numbers:
        result += i
    return result
