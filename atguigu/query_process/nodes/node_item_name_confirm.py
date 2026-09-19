# atguigu/query_process/nodes/node_item_name_confirm.py

import json

from langchain.chat_models import init_chat_model

from atguigu.query_process.base import NodeBase
from atguigu.query_process.state import QueryGraphState
from atguigu.tool.logger import logger
from config.config import LLMConfig, MilvusConfig
from config.prompt import ITEM_NAME_EXTRACT_SYSTEM_PROMPT, ITEM_NAME_EXTRACT_TEMPLATE
from tool.bge_m3_tool import get_bge_m3_embeddings
from tool.json_format_tool import json_format
from tool.milvus_client_tool import create_search_request, hybrid_search
from tool.mongo_tool import get_recent_messages, add_or_update_message, update_history_item_names


class NodeItemNameConfirm(NodeBase):
    """
    节点功能：确认用户问题中的核心商品名称。
    """

    # 覆盖基类的 name 属性，标识节点名称
    name: str = "node_item_name_confirm"

    def process(self, state: QueryGraphState):
        # 1、获取原始问题、会话ID等信息，拿到历史记录整理历史记录的字符串
        history_text, message_id, original_query, session_id = self.get_history_text(state)
        # 2、提取商品名称，并重写问题
        item_names, rewritten_query = self.get_llm_item_names(history_text, original_query)

        final_item_names = []
        answer = "不好意思，我暂时无法理解你的问题。你可以重新提问吗？"
        if item_names:
            # 3、如果识别的item_names存在就进行混合检索
            search_item_names = self.hybrid_search_item_names(item_names)
            # 4、商品名称对齐
            answer, final_item_names = self.align_item_names(answer, final_item_names, search_item_names)

        # 5、最终根据answer决定要不要保存助手消息的历史记录及回填item_names和rewritten_query到历史记录
        message_id = self.handler_history(answer, final_item_names, message_id, rewritten_query, session_id)

        return {
            "session_id": session_id,
            "message_id": message_id,
            "original_query": original_query,
            "rewritten_query": rewritten_query,
            "answer": answer,
            "item_names": final_item_names,  # 提取出的商品名称
            "history": get_recent_messages(session_id)  # 上面更新完成需要重新获取才能得到回填后的数据
        }


    def handler_history(self, answer, final_item_names, message_id, rewritten_query, session_id):
        if answer:
            # 如果有answer代表没有确认的商品名称，需要用户去确认或者重新提问，此时助手就把这个答案要通过后面答案输出节点推送给前端客户
            # 这个答案输出就得保存历史记录
            message_id = add_or_update_message(
                session_id=session_id,
                role="assistant",
                text=answer
            )
        # 把历史记录拿到，所有的这些历史记录都要回填item_names和rewritten_query
        history_list = get_recent_messages(session_id)
        ids = [history.get("_id") for history in history_list]
        if ids:
            update_history_item_names(ids, final_item_names, rewritten_query)
        return message_id

    def align_item_names(self, answer, final_item_names, search_item_names):
        # 商品名称对齐
        # 已经可以确认的商品名列表
        confirm_item_names = [
            item.get("search_item_name")
            for item in search_item_names
            if item.get("score") >= 0.85
        ]
        # 候选，可能是这些商品名字，后期需要用户来确认
        option_item_names = [
            item.get("search_item_name")
            for item in search_item_names
            if item.get("score") >= 0.6 and item.get("score") < 0.85
        ]
        if confirm_item_names:
            final_item_names = confirm_item_names
            answer = ""
        elif option_item_names:
            final_item_names = []
            answer = f"请确认一下你问的商品是下面哪个？{",".join(option_item_names)}"
        else:
            final_item_names = []
            answer = "不好意思，我暂时无法理解你的问题。你可以重新提问吗？"
        return answer, final_item_names

    def hybrid_search_item_names(self, item_names):
        #             遍历item_names，拿一个就去milvus当中检索
        embeddings = get_bge_m3_embeddings(item_names)
        dense = embeddings.get("dense")
        sparse = embeddings.get("sparse")
        search_item_names = []
        for idx, item_name in enumerate(item_names):
            reqs = create_search_request(
                dense[idx],
                sparse[idx],
                "dense_vector",
                "sparse_vector"
            )

            res = hybrid_search(
                MilvusConfig.item_name_collection,
                reqs,
                ranker=(0.7, 0.3),
                output_fields=["item_name"]
            )

            # print(json_format(res))
            # 每个识别的名字进行混合检索的结果都是二维列表，我们关注的是这个二维列表当中的第一个元素，也是一个列表
            # 我们需要把这个列表当中的每个字典（milvus当中查找的结果）整理一下存储到一个列表当中
            if res:
                for item in res[0]:
                    search_item_names.append({
                        "origin_item_name": item_name,
                        "search_item_name": item.get("entity", {}).get("item_name"),
                        "score": item.get("distance")
                    })
        return search_item_names

    def get_llm_item_names(self, history_text, original_query):
        llm = init_chat_model(
            model=LLMConfig.item_model,
            model_provider="openai",
            api_key=LLMConfig.openai_api_key,
            base_url=LLMConfig.openai_api_base,
            temperature=LLMConfig.llm_default_temperature,
        )
        messages = [
            {"role": "system", "content": ITEM_NAME_EXTRACT_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": ITEM_NAME_EXTRACT_TEMPLATE.format(history_text=history_text, original_query=original_query)
            }
        ]
        res = llm.invoke(messages)
        res_json = res.content
        if res_json.startswith("```json"):
            res_json = res_json.replace("```json", "").replace("```", "")
        result = json.loads(res_json)
        item_names = result.get("item_names", [])
        item_names = [item.replace(" ", "").replace("\n", "").replace("\t", "") for item in item_names]
        rewritten_query = result.get("rewritten_query")
        if not rewritten_query:
            rewritten_query = original_query
        return item_names, rewritten_query


    def get_history_text(self, state):
        session_id = state.get("session_id")
        original_query = state.get("original_query")
        if not session_id:
            logger.error("session_id必须传递")
            raise ValueError("session_id必须传递")
        if not original_query:
            logger.error("original_query必须传递")
            raise ValueError("original_query必须传递")
        # 获取最近的10条历史记录，后期要和原始问题一起交给大模型
        history_list = get_recent_messages(session_id)
        # 把这一次用户问的问题作为历史记录存储
        message_id = add_or_update_message(session_id, "user", original_query)
        # 把历史记录整理成字符串
        history_text = ""
        for history in history_list:
            role = history.get("role")
            text = history.get("text")
            history_text += f"{role}: {text}\n"
        print(history_text)
        return history_text, message_id, original_query, session_id




if __name__ == "__main__":

    # 模拟会话历史
    session_id = "test_001"
    # add_or_update_history(session_id, "user", "咨询下烫金机。")
    # add_or_update_history(session_id, "assistant", "您好。请问是哪个型号")
    # add_or_update_history(session_id, "user", "hak180")
    # add_or_update_history(session_id, "assistant", "具体有什么问题呢？")

    # 初始化图状态
    init_state = {
        "session_id": "test_001",
        "original_query": "咋用？"
    }

    # 创建节点对象
    node_item_name_confirm = NodeItemNameConfirm()
    # 执行节点的单元测试
    result = node_item_name_confirm(init_state)
    # 将返回的图状态进行json序列化
    logger.info(json_format(result))
