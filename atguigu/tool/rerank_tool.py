import dashscope
from http import HTTPStatus

from atguigu.config.config import RerankConfig
from atguigu.tool.json_format_tool import json_format
from atguigu.tool.logger import logger

# 以下为华北2（北京）地域的配置，调用时请将{WorkspaceId}替换为真实的业务空间ID，各地域的配置不同。
dashscope.base_http_api_url = RerankConfig.rerank_base_url
dashscope.api_key = RerankConfig.rerank_api_key

def text_rerank(query,texts,limit=20):
    resp = dashscope.TextReRank.call(
        model="qwen3.7-text-rerank",
        query=query,
        documents=texts,
        # return_documents=True,
        top_n=limit,
        instruct="Given a web search query, retrieve relevant passages that answer the query."
    )
    if resp.status_code == HTTPStatus.OK:
        print(resp.output.results)
        return [
            {
                "index":item.index,
                "score": item.relevance_score,
            }
            for item in resp.output.results
        ]
    else:
        logger.error(f"重排序请求失败{resp.status_code}")
        raise Exception(resp.status_code)

if __name__ == '__main__':
    result = text_rerank(query="我爱谁？",texts=["我爱杨幂", "我爱赵丽颖"])
    print(json_format(result))