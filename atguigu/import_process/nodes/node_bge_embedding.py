# atguigu/import_process/nodes/node_bge_embedding.py
import json

from atguigu.import_process.base import NodeBase
from atguigu.import_process.state import ImportGraphState
from tool.bge_m3_tool import get_bge_m3_embeddings
from tool.json_format_tool import json_format
from tool.logger import logger


class NodeBGEEmbedding(NodeBase):
    """
    混合向量化节点：使用 BGE-M3 模型将文本转换为向量
    """

    name = "node_bge_embedding"

    def process(self, state: ImportGraphState):
        # 对chunks进行向量化，并且把每个chunk字典里面回填自己的稠密和稀疏向量
        # 手动对chunks进行批处理 做向量化
        chunks = state.get("chunks")
        if not chunks:
            logger.error("chunks不存在")
            raise ValueError("chunks不存在")

        for i in range(0, len(chunks), 3):
            # 每次取3个chunk 做向量化
            chunk_k_list = chunks[i:i + 3]
            chunk_content_list = [f"{item.get("item_name")}-{item.get("content")}" for item in chunk_k_list]
            embeddings = get_bge_m3_embeddings(chunk_content_list)
            # 回填向量到chunk里面去
            for idx, chunk in enumerate(chunk_k_list):
                chunk["dense_vector"] = embeddings.get("dense")[idx]
                chunk["sparse_vector"] = embeddings.get("sparse")[idx]

        with open(f"D:\output0624\hak180产品安全手册\chunks_embedding.json", "w", encoding="utf-8") as f:
            f.write(json_format(chunks))

        logger.info("向量化完成")

        return {
            "chunks": chunks,
        }

if __name__ == '__main__':
    node = NodeBGEEmbedding()
    with open(r"D:\output0624\hak180产品安全手册\item_name_chunks.json", "r", encoding="utf-8") as f:
        chunks = json.load(f)

    init_state = {
        "chunks":chunks,
    }
    result = node(init_state)
    logger.info(json_format(result))

