import json
from typing import List, Optional
from pydantic import BaseModel, Field

# 1. 定义数据模型（必须继承自 BaseModel）
class ChunkModel(BaseModel):
    content: str                                      # 必填字符串
    tags: List[str] = Field(default_factory=list)    # 必填列表，若不传默认为空列表 []
    score: Optional[float] = None                     # 选填浮点数，默认为 None

# 2. 实例化对象（推荐使用关键字传参）
# 在创建的那一刻，Pydantic 会自动在“运行时”检查类型是否正确！
raw_chunks: List[ChunkModel] = [
    ChunkModel(
        content="Qwen3.7-text-rerank 是阿里云发布的通用文本重排序大模型。",
        tags=["AI", "Rerank"],
        score=0.92
    ),
    ChunkModel(
        content="HTTP 400 状态码代表客户端请求错误（Bad Request）。",
        tags=["Network", "HTTP"],
        score=0.85
    ),
    ChunkModel(
        content="这条数据刚召回，还没有经过 Rerank 算分",
        tags=["Pending"] # score 会自动默认为 None
    )
]

print("--- 1. 对象属性访问与修改 ---")
# 像 dataclass 一样，使用点号 (.) 访问，IDE 会有完美的自动补全提示
first_chunk = raw_chunks[0]
print(f"第一个 Chunk 的内容: {first_chunk.content}")
# 也可以直接修改属性
first_chunk.score = 0.99
print(f"修改后的分数: {first_chunk.score}")


print("\n--- 2. 在 RAG 中模拟 Rerank 降序排序 ---")
# 同样使用上一轮讨论的降序逻辑，完美避开 None 导致的 TypeError
rerank_chunks = sorted(
    raw_chunks,
    key=lambda x: x.score if x.score is not None else -float('inf'),
    reverse=True
)
for i, chunk in enumerate(rerank_chunks):
    current_score = chunk.score if chunk.score is not None else 0.0
    print(f"排名 {i+1} | 分数: {current_score:.2f} | 文本: {chunk.content[:10]}...")


print("\n--- 3. 原生序列化为 JSON 字符串（完胜 dataclass） ---")
# 🚨 Pydantic V2 提供了极其强大的模型转字典/JSON 的内置方法，完全不需要 json.dumps 和 asdict！
# 方法 A：直接转为 Python 字典列表
chunks_dict_list = [chunk.model_dump() for chunk in rerank_chunks]

# 方法 B：直接把整个列表丢给 Pydantic 的 TypeAdapter 或者手动序列化
# 这里为了和前面保持一致，我们使用内置的 model_dump_json()，它比原生 json.dumps 快数倍
for chunk in rerank_chunks:
    print(chunk.model_dump_json())


# =====================================================================
# 🚨 运行时“强类型拦截”演示（Pydantic 最核心的终极武器）
# =====================================================================
print("\n--- 4. 触发运行时类型校验异常 ---")
try:
    # 故意把 score 传成字符串 "很棒"，把 tags 传成数字 123
    error_chunk = ChunkModel(content="测试数据", tags=123, score="很棒")
except Exception as e:
    # 程序在运行到这一行时会立刻拦截并抛出 ValidationError，绝对不会让脏数据流入下游的 RAG 链条
    print("【拦截成功】发现不合规的数据输入：")
    print(e)
