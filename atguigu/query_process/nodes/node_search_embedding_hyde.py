# atguigu/query_process/nodes/node_search_embedding_hyde.py
import json

from langchain.chat_models import init_chat_model

from atguigu.query_process.base import NodeBase
from atguigu.query_process.state import QueryGraphState
from atguigu.tool.logger import logger
from config.config import LLMConfig, MilvusConfig
from config.prompt import HYDE_PROMPT
from tool.bge_m3_tool import get_bge_m3_embeddings
from tool.json_format_tool import json_format
from tool.milvus_client_tool import create_search_request, hybrid_search


class NodeSearchEmbeddingHyde(NodeBase):
    """
    节点功能：HyDE (Hypothetical Document Embedding)
    先让 LLM 生成假设性答案，再对答案进行向量检索，提高召回率。
    """

    # 覆盖基类的 name 属性，标识节点名称
    name: str = "node_search_embedding_hyde"

    def process(self, state: QueryGraphState):
        item_names, rewritten_query = self.get_rewritten_query(state)
        hyde_answer = self.generate_hyde_answer(rewritten_query)

        chunks = self.hyde_hybird_search(hyde_answer, item_names, rewritten_query)

        return {
            "hyde_embedding_chunks": chunks
        }

    def hyde_hybird_search(self, hyde_answer, item_names, rewritten_query):
        # 把问题和生成的假设性答案拼接起来，作为新的查询问题进行向量化（语义更丰富）
        merged_query = rewritten_query + ":" + hyde_answer
        embeddings = get_bge_m3_embeddings([merged_query])
        dense = embeddings.get("dense")[0]
        sparse = embeddings.get("sparse")[0]
        # 过滤条件
        item_names = [
            item_name.replace("\\", "\\\\").replace("'", "\'").replace('"', '\"')
            for item_name in item_names
        ]
        expr = f"item_name in {json.dumps(item_names)}"
        reqs = create_search_request(
            dense,
            sparse,
            dense_anns_field="dense_vector",
            sparse_anns_field="sparse_vector",
            expr=expr
        )
        res = hybrid_search(
            collection_name=MilvusConfig.chunks_collection,
            reqs=reqs,
            ranker=(0.6, 0.4),
            output_fields=["id", "title", "file_title", "content", "item_name"]
        )
        chunks = [
            {
                **item.get("entity"),
                "score": item.get("distance"),
                "source": "local"
            }
            for item in res[0]
        ]
        return chunks

    def generate_hyde_answer(self, rewritten_query):
        llm = init_chat_model(
            model=LLMConfig.item_model,
            model_provider="openai",
            api_key=LLMConfig.openai_api_key,
            base_url=LLMConfig.openai_api_base,
            temperature=float(LLMConfig.llm_default_temperature),
        )
        messages = [
            {"role": "user", "content": HYDE_PROMPT.format(rewritten_query=rewritten_query)}
        ]
        res = llm.invoke(input=messages)
        hyde_answer = res.content
        return hyde_answer

    def get_rewritten_query(self, state):
        rewritten_query = state.get("rewritten_query")
        item_names = state.get("item_names")
        if not rewritten_query:
            logger.error("rewritten_query不能为空")
            raise ValueError("rewritten_query不能为空")
        if not item_names:
            logger.error("item_names不能为空")
            raise ValueError("item_names不能为空")
        return item_names, rewritten_query

if __name__ == "__main__":
    init_state = {
        "rewritten_query": "关于HAK180烫金机如何使用",
        "item_names": ["HAK180烫金机"]
    }
    node_search_embedding_hyde = NodeSearchEmbeddingHyde()
    result = node_search_embedding_hyde(init_state)
    logger.info(json_format(result))