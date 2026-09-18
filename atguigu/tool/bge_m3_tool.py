# 获取模型
from pymilvus.model.hybrid import BGEM3EmbeddingFunction

from atguigu.config.config import BgeM3Config
from atguigu.tool.json_format_tool import json_format

bge_m3_model = None
def get_bge_m3_model():
    """
    获取BGEM3模型对象
    :return: bge_m3_model模型的对象，可以使用很多方式去实例化
    """
    global bge_m3_model
    if bge_m3_model is None:
        bge_m3_model = BGEM3EmbeddingFunction(
            model_name=BgeM3Config.bge_m3_path,
            device=BgeM3Config.bge_device,
            use_fp16=BgeM3Config.bge_fp16
        )
    return bge_m3_model


# 获取模型对数据的向量化结果
def get_bge_m3_embeddings(text_list):
    """
    获取BGEM3模型对数据的向量化结果
    :param text_list: 文本列表，可以是文档也可以是查询
    :return: 向量化的结果
    """
    bge_m3_model = get_bge_m3_model()
    result = bge_m3_model.encode_documents(text_list)


    sparse = result.get("sparse")
    #
    # print(sparse)
    # print(type(sparse))
    # print(sparse.__dict__)
    # #没有遍历三个稀疏向量全部揉在一起  三个列表分别表示位置 数据 行索引
    # # 整理的时候不好区分哪几个位置和数据是同一个字典向量
    # #期望的结构
    # # return {
    #     # "dense":[[你好的稠密],[世界的稠密],[杨幂的稠密]],
    #     # "sparse":[{}，{}，{}]
    # # }
    #
    # for item in sparse:
    #     print(item,type(item),item.indices)
    #     print(item.__dict__) #三个字典向量自己有自己的位置 数据，整理起来直接去整理即可

    # 把其它数据类型转化为list列表类型，并且把列表当中的数据类型强制转化为python的数据类型
    return {
        "dense": [item.tolist() for item in result.get("dense")],
        "sparse": [dict(zip(item.indices.tolist(),item.data.tolist())) for item in result.get("sparse")]
    }


if __name__ == '__main__':
    result = get_bge_m3_embeddings(["世界","杨幂"])
    print(json_format(result))
