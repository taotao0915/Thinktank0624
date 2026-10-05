# atguigu/query_process/nodes/node_search_embedding.py
import json

from atguigu.query_process.base import NodeBase
from atguigu.query_process.state import QueryGraphState
from atguigu.tool.logger import logger
from config.config import MilvusConfig
from tool.bge_m3_tool import get_bge_m3_embeddings
from tool.json_format_tool import json_format
from tool.milvus_client_tool import create_search_request, hybrid_search


class NodeSearchEmbedding(NodeBase):
     """
    节点功能：基于已确认主体名+改写后的用户问题，执行Milvus向量数据库混合检索
    """

     # 覆盖基类的 name 属性，标识节点名称
     name: str = "node_search_embedding"

     def process(self, state: QueryGraphState):
         # 获取重写后的用户问题以及商品名称
         item_names, rewritten_query = self.get_rewritten_query(state)
         # 向量化问题，混合检索
         chunks = self.get_embedding_chunks(item_names, rewritten_query)

         return {
             "embedding_chunks": chunks
         }


     def get_embedding_chunks(self, item_names, rewritten_query):
         # 向量化问题
         embeddings = get_bge_m3_embeddings([rewritten_query])
         dense = embeddings.get("dense")[0]
         sparse = embeddings.get("sparse")[0]
         # 混合检索
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
             ranker=(0.8, 0.2),
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
        "rewritten_query": "关于BrotherHAK180烫金机如何使用",
        "item_names": ["HAK180烫金机"]
    }
    node_search_embedding = NodeSearchEmbedding()
    result = node_search_embedding(init_state)
    logger.info(json_format(result))