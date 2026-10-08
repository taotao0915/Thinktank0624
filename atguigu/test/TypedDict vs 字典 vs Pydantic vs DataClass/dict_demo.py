import json

# 1. 纯字典数据的初始化
# 没有任何类定义，直接使用大括号 {}，键名完全靠开发者肉眼和记忆来保证正确
raw_chunks = [
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
        # 故意不写 "score" 键，模拟刚召回无分数的情况
        "tags": ["Pending"]
    }
]

print("--- 1. 字典属性访问 ---")
# 必须使用中括号和字符串键访问：chunk["key"]
# 🚨 警告：如果直接用 chunk["score"]，第三条数据会直接触发 KeyError 崩溃！
for i, chunk in enumerate(raw_chunks):
    # 安全写法：使用 .get() 并在找不到键时提供默认值
    score = chunk.get("score", 0.0)
    print(f"Chunk [{i}]: 分数={score:.2f} | 标签={chunk['tags']}")


print("\n--- 2. 在 RAG 中模拟 Rerank 降序排序 ---")
# 针对纯字典的排序逻辑：
# 必须使用 x.get("score")，并妥善处理 None 或键不存在的情况，否则会报 TypeError 崩溃
rerank_chunks = sorted(
    raw_chunks,
    key=lambda x: x.get("score") if x.get("score") is not None else -float('inf'),
    reverse=True
)

for i, chunk in enumerate(rerank_chunks):
    # 获取分数用于打印
    score = chunk.get("score", 0.0)
    print(f"排名 {i+1} | 分数: {score:.2f} | 文本: {chunk['content'][:10]}...")


print("\n--- 3. 序列化为 JSON 字符串（原生支持） ---")
# 🚀 字典最大的优势：天生就是 JSON 的亲兄弟，不需要任何转换，直接 dumps
json_str = json.dumps(rerank_chunks, ensure_ascii=False, indent=2)
print(json_str)


# =====================================================================
# 🚨 纯字典的隐患演示（运行期和编写期都不会拦截，隐患直接带入下游）
# =====================================================================
print("\n--- 4. 演示纯字典对脏数据的“零防御力” ---")
# 即使手抖把 score 写成了字符串，把 tags 写成了数字，Python 依然会无条件放行
dirty_chunk = {
    "content": "我是脏数据",
    "score": "极高分",  # 应该是 float 却写成了 str
    "tags": 12345      # 应该是 list 却写成了 int
}
raw_chunks.append(dirty_chunk)
print("【警告】脏数据成功混入列表，直到下游代码使用到它时（比如做数学计算），程序才会突然崩溃。")
