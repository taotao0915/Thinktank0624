import json
from typing import TypedDict, NotRequired, List

# 1. 定义 RAG 系统中的 Chunk 数据结构
class ChunkData(TypedDict):
    content: str               # 文本内容（必填）
    score: NotRequired[float]  # 匹配分数（选填，因为初始召回时可能没有分数）
    tags: List[str]            # 标签列表（必填）

# 2. 模拟从数据库或向量检索中拿到的原始数据
# 注意：在运行时，它依然是纯粹的 Python dict
raw_chunks: List[ChunkData] = [
    {
        "content": "Qwen3.7-text-rerank 是阿里云发布的通用文本重排序大模型。",
        "score": 0.92,
        "tags": ["AI", "Rerank"]
    },
    {
        "content": "HTTP 400 状态码代表客户端请求错误（Bad Request）。",
        "score": 0.85,
        "tags": ["Network", "HTTP"]
    },
    {
        "content": "这条数据刚召回，还没有经过 Rerank 算分",
        # "score" 键是 NotRequired，所以这里不写也不会触发 IDE 报错
        "tags": ["Pending"]
    }
]

# 3. 编写一个处理函数的示例
def process_chunks(chunks: List[ChunkData]) -> None:
    print("--- 开始处理数据 ---")
    for i, chunk in enumerate(chunks):
        # 像普通字典一样通过 key 访问
        content = chunk["content"]

        # 安全地获取选填字段（推荐使用 .get() 设定默认值，防止运行时 KeyError）
        score = chunk.get("score", 0.0)

        print(f"Chunk [{i}]: 分数={score:.2f} | 内容={content[:20]}...")

# 执行处理
process_chunks(raw_chunks)

# 4. 证明 TypedDict 的本质：它就是普通字典，完美兼容 json 序列化
print("\n--- 序列化为 JSON 字符串 ---")
json_str = json.dumps(raw_chunks, ensure_ascii=False, indent=2)
print(json_str)


# =====================================================================
# 🚨 静态类型检查演示（你可以取消注释下面两行，看看你的 IDE 是否会标红警告）
# =====================================================================
# error_chunk: ChunkData = {"content": "我故意漏掉了必填的 tags 键"}  # IDE 警告：Missing key "tags"
# error_chunk2: ChunkData = {"content": "写错了类型", "tags": "应该传列表而非字符串"} # IDE 警告：Expression of type "str" cannot be assigned to type "List[str]"
