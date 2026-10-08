import json
from dataclasses import dataclass, asdict
from typing import List, Optional

# 1. 定义数据结构（真正作为自定义类对象）
@dataclass
class ChunkClass:
    content: str
    tags: List[str]
    # 在 dataclass 中，默认值可以直接写在属性后面，不需要 NotRequired
    score: Optional[float] = None

# 2. 真正的实例化方式：必须使用 类名(参数)
# 这样在内存中创建的才是真正的 ChunkClass 对象，而不是普通字典
raw_chunks: List[ChunkClass] = [
    ChunkClass(
        content="Qwen3.7-text-rerank 是阿里云发布的通用文本重排序大模型。",
        tags=["AI", "Rerank"],
        score=0.92
    ),
    ChunkClass(
        content="HTTP 400 状态码代表客户端请求错误（Bad Request）。",
        tags=["Network", "HTTP"],
        score=0.85
    ),
    ChunkClass(
        content="这条数据刚召回，还没有经过 Rerank 算分",
        tags=["Pending"] # score 默认是 None
    )
]

print("--- 1. 对象属性访问演示 ---")
# 此时可以通过极其顺手的 点号（.`） 直接访问或修改属性，IDE 会有完美的自动补全提示
for chunk in raw_chunks:
    print(f"标签: {chunk.tags} | 内容: {chunk.content[:15]}...")

print("\n--- 2. 在 RAG 中模拟 Rerank 算分和重排序 ---")
# 模拟上一轮我们讨论的 Rerank 降序排序逻辑（完美避开 None 导致的 TypeError）
rerank_chunks = sorted(
    raw_chunks,
    key=lambda x: x.score if x.score is not None else -float('inf'),
    reverse=True
)

for i, chunk in enumerate(rerank_chunks):
    # 如果 score 为 None 则打印 0.00
    current_score = chunk.score if chunk.score is not None else 0.0
    print(f"排名 {i+1} | 分数: {current_score:.2f} | 文本: {chunk.content[:10]}...")

print("\n--- 3. 序列化为 JSON 字符串 ---")
# 🚨 关键点：如果直接运行 json.dumps(rerank_chunks) 会直接报错
# 必须先调用 asdict() 将对象列表转换为字典列表，再扔给 json.dumps
chunks_as_dict = [asdict(chunk) for chunk in rerank_chunks]

json_str = json.dumps(chunks_as_dict, ensure_ascii=False, indent=2)
print(json_str)
