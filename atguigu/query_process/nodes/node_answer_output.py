# atguigu/query_process/nodes/node_answer_output.py
import re

from langchain.chat_models import init_chat_model

from atguigu.config.config import LLMConfig
from atguigu.config.prompt import ANSWER_PROMPT
from atguigu.query_process.base import NodeBase
from atguigu.query_process.state import QueryGraphState
from atguigu.tool.mongo_tool import add_or_update_message
from atguigu.tool.task_utils import put_data


class NodeAnswerOutput(NodeBase):
    """
    节点功能: 答案生成
    """

    # 覆盖基类的 name 属性，标识节点名称
    name: str = "node_answer_output"

    def process(self, state: QueryGraphState):
        answer = state.get("answer")
        task_id = state.get("task_id")
        chunks = state.get("reranked_docs")
        history_list = state.get("history")
        item_names = state.get("item_names")
        session_id = state.get("session_id")
        rewritten_query = state.get("rewritten_query")
        if answer:
            # 当年我们去做意图识别的时候，item_name没有确认，那么就会有答案
            # 把答案也是放入sse队列
            put_data(task_id, "final", {"answer":answer})
        else:
            # 代表意图识别的时候识别出真正的item_name,需要后续进行多路检索  rrf  rerank
            # 拿到最终重排序后的chunks,需要交给大模型，让大模型帮我们总结答案

            #提示词整理
            #1、整理chunk
            context = ""
            for chunk in chunks:
                title = chunk.get("title")
                content = chunk.get("content")
                url = chunk.get("url")
                source = chunk.get("source")
                chunk_content = f"标题：{title}\n内容：{content}\n来源：{source}\n链接：{url}\n\n"
                context = context + chunk_content
            #2、整理历史对话
            history = ""
            for item in history_list:
                h_content = f"{item.get('role')}:{item.get('text')}\n\n"
                history = history + h_content

            #3、整理识别完成的商品名称
            item_names_str = ",".join(item_names)

            #4、整理重写的问题
            question = rewritten_query

            prompt =  ANSWER_PROMPT.format(context=context,history=history,item_names=item_names_str,question=question)

            llm = init_chat_model(
                model=LLMConfig.item_model,
                model_provider="openai",
                api_key=LLMConfig.openai_api_key,
                base_url=LLMConfig.openai_api_base,
                temperature=LLMConfig.llm_default_temperature
            )

            messages = [
                {
                    "role": "user",
                    "content":prompt,
                }
            ]

            res = llm.stream(input=messages)
            for item in res:
                #把流式输出的每个答案，放入sse队列，而且要把每个答案，最终拼接成一个完整的答案，因为后期还得保存历史记录
                put_data(task_id, "delta", {"delta":item.content})
                answer += item.content


            #我们需要把chunk当中用到的图片，自己识别出来，最终推送给前端


            seen = set()  # 用于去重，避免同一张图片重复出现
            md_img_pattern = re.compile(r'!\[.*?\]\((.*?)\)')
            for i, doc in enumerate(chunks):
                # 检查 text 字段中的 Markdown 图片 (主要针对 Local Chunk)
                text = doc.get("content")
                matches = md_img_pattern.findall(text)
                for img_url in matches:
                    img_url = img_url.strip()
                    seen.add(img_url)
            images = list(seen)
            # 最终答案推送完成的标志是final事件，我们在最终其实是单独把图片url列表给推送到前端
            put_data(task_id, "final", {"image_urls":images})



            #保存历史记录
            if answer:
                message_id = add_or_update_message(
                    session_id=session_id,
                    role="assistant",
                    text=answer,
                    item_names=item_names,
                    rewritten_query=rewritten_query,
                )

        return {
            "answer": answer
        }
