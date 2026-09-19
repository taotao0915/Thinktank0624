from pymilvus import MilvusClient, AnnSearchRequest, WeightedRanker, RRFRanker

from atguigu.config.config import MilvusConfig

milvus_client = None
def get_milvus_client():
    global milvus_client
    if not milvus_client:
        milvus_client = MilvusClient(
            uri=MilvusConfig.milvus_url
        )
    return milvus_client


# 封装混合检索的工具函数
# 1、制造混合检索的稠密向量和稀疏向量检索请求对象，组成列表
# 2、执行混合检索
# 混合检索请求函数的参数要看AnnSearchRequest需要什么参数
def create_search_request(
        dense_data,
        sparse_data,
        dense_anns_field,
        sparse_anns_field,
        dense_param=None,
        sparse_param=None,
        limit=10,
        expr=None):
    if not dense_param:
        dense_param = {
            "metric_type": "COSINE",
        }
    if not sparse_param:
        sparse_param = {
            "metric_type": "IP",
        }

    #给稠密向量创建请求
    dense_req = AnnSearchRequest(
        data=[dense_data],
        anns_field=dense_anns_field,
        param=dense_param,
        limit=limit,
        expr=expr,
    )

    #给稀疏向量创建请求
    sparse_req = AnnSearchRequest(
        data=[sparse_data],
        anns_field=sparse_anns_field,
        param=sparse_param,
        limit=limit,
        expr=expr,
    )
    #返回请求组成的列表

    return [dense_req, sparse_req]


def hybrid_search(collection_name,reqs,ranker=(0.5,0.5),limit=10,output_fields=None):
    milvus_client = get_milvus_client()

    weighted_ranker = WeightedRanker(*ranker)
    res = milvus_client.hybrid_search(
        collection_name=collection_name,
        reqs=reqs,
        ranker=weighted_ranker, #加权排序 0.5*dense_score + 0.5*sparse_score，一句话最终分数偏向谁
        limit=limit,
        output_fields=output_fields
    )

    return res

