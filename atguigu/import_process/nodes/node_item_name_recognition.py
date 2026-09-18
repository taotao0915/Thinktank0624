# atguigu/import_process/nodes/node_item_name_recognition.py
import json

from langchain.chat_models import init_chat_model
from pymilvus import MilvusClient, DataType

from atguigu.config.config import LLMConfig, MilvusConfig
from atguigu.config.prompt import ITEM_NAME_SYSTEM_PROMPT, ITEM_NAME_USER_PROMPT_TEMPLATE
from atguigu.import_process.base import NodeBase
from atguigu.import_process.state import ImportGraphState
from atguigu.tool.logger import logger
from atguigu.tool.milvus_client_tool import get_milvus_client
from tool.bge_m3_tool import get_bge_m3_embeddings
from tool.json_format_tool import json_format


class NodeItemNameRecognition(NodeBase):
    """
    主体识别节点：主体识别与标签提取
    """

    name = "node_item_name_recognition"

    def process(self, state: ImportGraphState):
        # 1、获取chunks
        chunks, file_title = self.get_chunks(state)
        # 2、通过chunks截取前面20个拼接成字符串
        content_str = self.get_chunks_str(chunks)
        # 3、通过LLM和上一步的字符串及文件名大模型识别获取item_name
        item_name = self.get_llm_item_name(content_str, file_title)
        # 4、对item_name进行向量化，并且创建item_name对应的milvus表
        collection_name, dense_vector, milvus_client, sparse_vector = self.create_milvus_collection(item_name)
        # 5、将item_name和向量存储到milvus，先要进行幂等性删除同文件识别的item_name
        self.insert_data(collection_name, dense_vector, file_title, item_name, milvus_client, sparse_vector)

        # 6、回填item_name到每个chunk
        for chunk in chunks:
            chunk["item_name"] = item_name


        return {
            "item_name":item_name,
            "chunks":chunks
        }

    def insert_data(self, collection_name, dense_vector, file_title, item_name, milvus_client, sparse_vector):
        # 5、将item_name和向量存储到milvus
        # 把item_name整理成一个milvus需要的字典格式
        # 在存入数据之前应该要对表里面的数据做幂等性删除
        # 要做删除数据，把milvus表必须进行加载才能操作
        milvus_client.load_collection(collection_name=collection_name)
        file_title = file_title.replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"')
        filter = f"file_title == '{file_title}'"
        milvus_client.delete(
            collection_name=collection_name,
            filter=filter
        )
        data = {
            "item_name": item_name,
            "file_title": file_title,
            "dense_vector": dense_vector,
            "sparse_vector": sparse_vector
        }
        milvus_client.insert(collection_name=collection_name, data=data)

    def create_milvus_collection(self, item_name):
        # 3、对item_name进行向量化
        embeddings = get_bge_m3_embeddings([item_name])
        dense_vector = embeddings.get("dense")[0]
        sparse_vector = embeddings.get("sparse")[0]
        # 4、创建表
        # milvus创建表的三大步：1、创建结构  2、创建索引 3、创建表
        milvus_client = get_milvus_client()
        collection_name = MilvusConfig.item_name_collection  # 获取配置的表名
        if not milvus_client.has_collection(collection_name):
            # 创建表的三大步
            schema = milvus_client.create_schema(
                auto_id=True,
            )
            schema.add_field(
                field_name="id",
                datatype=DataType.INT64,
                is_primary=True,
                # is_unique=True,
            ).add_field(
                field_name="item_name",
                datatype=DataType.VARCHAR,
                max_length=100
            ).add_field(
                field_name="file_title",
                datatype=DataType.VARCHAR,
                max_length=100
            ).add_field(
                field_name="dense_vector",
                datatype=DataType.FLOAT_VECTOR,
                dim=1024  # 稠密向量必须传维度，稀疏向量不能传维度，否则就炸
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
                params={
                    "nlist": 128,  # 一共分成128个簇（桶）
                    "nprobe": 10  # 查询时，拿最有可能的10个簇来找
                }
            )

            index_params.add_index(
                field_name="sparse_vector",
                index_name="sparse_vector_index",
                index_type="SPARSE_INVERTED_INDEX",
                metric_type="IP",
                params={
                    "inverted_index_algo": "DAAT_MAXSCORE",
                    # 高效的稀疏检索算法
                    "normalize": True,
                    # ↑ L2 归一化，让内积 (IP) 等价于余弦相似度
                    "quantization": "none"
                    # ↑ 关闭量化，保持原始精度：模型生成的向量已经压缩的一半的精度了（BGE_FP16=1），这里就不再压缩了
                    # "quantization": "none" → 存储原始向量，不压缩
                    # "quantization": "sq8" → 存储压缩后的向量（8-bit 量化
                }
            )

            milvus_client.create_collection(
                collection_name=collection_name,
                schema=schema,
                index_params=index_params
            )
        return collection_name, dense_vector, milvus_client, sparse_vector

    def get_llm_item_name(self, content_str, file_title):
        # 2、调用LLM进行主体识别
        llm = init_chat_model(
            model=LLMConfig.llm_default_model,
            model_provider="openai",
            api_key=LLMConfig.openai_api_key,
            base_url=LLMConfig.openai_api_base,
            temperature=LLMConfig.llm_default_temperature
        )
        messages = [
            {
                "role": "system",
                "content": ITEM_NAME_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": ITEM_NAME_USER_PROMPT_TEMPLATE.format(file_title=file_title, context=content_str)
            }
        ]
        res = llm.invoke(input=messages)
        item_name = res.content
        item_name = item_name.replace(" ", "").replace("\n", "").replace("\t", "")
        if not item_name:
            item_name = file_title
        return item_name

    def get_chunks_str(self, chunks):
        # 开始进行主体识别
        # 1、根据部分的chunk拼接chunk的内容变成一个大的字符串
        chunk_k_list = chunks[:20]
        content_str = ""
        for idx, chunk in enumerate(chunk_k_list, start=1):
            title = chunk.get("title")
            content = chunk.get("content")
            chunk_content = f"[切片{idx}]\n[标题:]{title}\n[内容:]{content}\n\n"
            content_str += chunk_content
            if len(content_str) >= 12000:
                break
        content_str = content_str[:12000]
        # print(content_str)
        return content_str

    def get_chunks(self, state):
        chunks = state.get("chunks")
        file_title = state.get("file_title")
        if not chunks:
            logger.error(f"文件 {file_title} 没有切片，无法进行主体识别")
            raise ValueError(f"文件 {file_title} 没有切片，无法进行主体识别")
        if not file_title:
            logger.error(f"文件标题未定义，无法进行主体识别")
            raise ValueError("文件标题未定义，无法进行主体识别")
        return chunks, file_title


if __name__ == '__main__':
    node = NodeItemNameRecognition()
    with open(r"D:\output0624\hak180产品安全手册\split_chunks.json", "r", encoding="utf-8") as f:
        chunks = f.read()


    init_state = {
        "chunks": json.loads(chunks),
        "file_title": "hak180产品安全手册"
    }

    result = node(init_state)
    logger.info(json_format(result))

