# atguigu/query_process/nodes/node_web_search_mcp.py
import asyncio
import json

from agents.mcp import MCPServerStreamableHttp

from atguigu.query_process.base import NodeBase
from atguigu.query_process.state import QueryGraphState
from atguigu.tool.logger import logger
from config.config import McpConfig
from tool.json_format_tool import json_format


class NodeWebSearchMcp(NodeBase):
    """
    节点功能，调用外部搜索引擎补充信息
    """

    # 覆盖基类的 name 属性，标识节点名称
    name: str = "node_web_search_mcp"

    def process(self, state: QueryGraphState):
        rewritten_query = state.get("rewritten_query")
        if not rewritten_query:
            logger.error("改写后的问题不存在，无法进行web检索")
            raise ValueError("改写后的问题不存在，无法进行web检索")

        result = asyncio.run(self.run_mcp(rewritten_query))
        data = json.loads(result.content[0].text).get("pages")
        return {
            "web_search_docs": [
                {
                    "content": item.get("snippet"),
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "source": "web"
                }
                for item in data
            ]
        }

    async def run_mcp(self,query,limit=10) -> None:
        token = McpConfig.mcp_api_key
        async with MCPServerStreamableHttp(
                name="网络搜索服务",
                params={
                    "url": McpConfig.mcp_base_url,
                    "headers": {"Authorization": f"Bearer {token}"},
                    "timeout": 10,
                },
                cache_tools_list=True,
                max_retry_attempts=3,
                client_session_timeout_seconds=30 #从服务器开始连接一直到请求超时的总时间
        ) as server:
            result = await server.call_tool(tool_name="bailian_web_search",arguments={
                "query": query,
                "count": limit
            })
            return result

if __name__ == "__main__":

    init_state = {
        "rewritten_query": "关于HAK180烫金机如何使用"
    }

    # 执行节点的业务调用
    node_web_search_mcp = NodeWebSearchMcp()
    result = node_web_search_mcp(init_state)
    logger.info(json_format(result))