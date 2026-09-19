# atguigu/import_process/nodes/node_import_milvus.py
import json

from pymilvus import DataType

from atguigu.config.config import MilvusConfig
from atguigu.import_process.base import NodeBase
from atguigu.import_process.state import ImportGraphState
from atguigu.tool.logger import logger
from atguigu.tool.milvus_client_tool import get_milvus_client
from tool.json_format_tool import json_format


class NodeImportMilvus(NodeBase):
    """
    导入向量库节点：数据持久化
    """

    name = "node_import_milvus"

    def process(self, state: ImportGraphState):
        chunks = state.get("chunks")
        if not chunks:
            logger.error("chunks不存在")
            raise Exception("chunks不存在")

        file_title = chunks[0].get("file_title")
        milvus_client = get_milvus_client()
        collection_name = MilvusConfig.chunks_collection
        if not milvus_client.has_collection(collection_name):
            schema = milvus_client.create_schema(
                auto_id=True
            )
            schema.add_field(
                field_name="id",
                datatype=DataType.INT64,
                is_primary=True
            ).add_field(
                field_name="title",
                datatype=DataType.VARCHAR,
                max_length=100
            ).add_field(
                field_name="file_title",
                datatype=DataType.VARCHAR,
                max_length=100
            ).add_field(
                field_name="content",
                datatype=DataType.VARCHAR,
                max_length=5000
            ).add_field(
                field_name="part",
                datatype=DataType.INT64,
            ).add_field(
                field_name="item_name",
                datatype=DataType.VARCHAR,
                max_length=100
            ).add_field(
                field_name="dense_vector",
                datatype=DataType.FLOAT_VECTOR,
                dim=1024
            ).add_field(
                field_name="sparse_vector",
                datatype=DataType.SPARSE_FLOAT_VECTOR,
            )


            index_params = milvus_client.prepare_index_params()
            index_params.add_index(
                field_name="dense_vector",
                index_name="dense_vector_index",
                index_type="IVF_FLAT",
                metric_type="COSINE",
                params={"nlist": 128,"nprobe": 10},
            )

            index_params.add_index(
                field_name="sparse_vector",
                index_name="sparse_vector_index",
                index_type="SPARSE_INVERTED_INDEX",
                metric_type="IP",
                params={
                    "inverted_index_algo": "DAAT_MAXSCORE"
                }
            )


            milvus_client.create_collection(
                collection_name=collection_name,
                schema=schema,
                index_params=index_params
            )

        #插入数据前要幂等性删除
        milvus_client.load_collection(collection_name=collection_name)
        file_title = file_title.replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"')
        filter = f"file_title == '{file_title}'"
        milvus_client.delete(
            collection_name=collection_name,
            filter=filter
        )


        #插入chunks到milvus 不需要向量化了，因为上个节点已经做过了
        res = milvus_client.insert(
            collection_name=collection_name,
            data=chunks
        )
        ids = res.get("ids")
        for idx,chunk in enumerate(chunks):
            # chunk["id"] = ids.pop(0)
            chunk["id"] = ids[idx]


        return {
            "chunks": chunks,
        }


if __name__ == '__main__':
    node = NodeImportMilvus()
    with open(r"D:\output0624\hak180产品安全手册\chunks_embedding.json","r",encoding="utf-8") as f:
        chunks = json.load(f)
    init_state = {
        "chunks":chunks
    }
    result = node(init_state)
    logger.info(json_format(result))
