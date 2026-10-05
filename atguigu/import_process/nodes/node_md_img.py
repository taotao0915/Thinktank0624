# atguigu/import_process/nodes/node_md_img.py
import base64
import os
import re
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any

from langchain.chat_models import init_chat_model
from minio.deleteobjects import DeleteObject

from atguigu.config.config import LLMConfig, MinioConfig
from atguigu.import_process.base import NodeBase
from atguigu.import_process.state import ImportGraphState
from atguigu.tool import json_format_tool
from atguigu.tool.logger import logger
from tool.minio_client_tool import get_minio_client


class NodeMDImg(NodeBase):
    """
    MarkDown图片处理节点：多模态图片理解
    """

    name = "node_md_img"

    def process(self, state: ImportGraphState):
        # 获取md路径和内容
        md_path_obj,md_content = self.check_md_path(state)

        # 获取到内容后再去拿到images文件夹
        image_dir_obj = md_path_obj.parent / "images"
        if not image_dir_obj or not image_dir_obj.exists():
            logger.info("images文件夹不存在")
            return {
                "md_content": md_content
            }

        # 获取images每张图片的名字
        image_names = os.listdir(image_dir_obj)
        if not image_names:
            logger.info("images文件夹中没有图片")
            return {
                "md_content": md_content
            }

        # 获取图片的上下文暂存
        image_with_context_list = self.get_image_with_context_list(image_dir_obj, image_names, md_content)
        # 获取图片的摘要暂存
        image_with_summary_list = self.get_image_with_summary_list(image_with_context_list)
        # 上传图片到minio，并且拿到图片的网络路径暂存
        image_with_summary_and_url_list = self.upload_minio(image_with_summary_list, md_path_obj)
        # 把得到的摘要和图片的网络路径url替换原来的，并且备份新的内容到新的文件
        md_content, new_md_path_obj = self.update_md_file_content(image_with_summary_and_url_list, md_content, md_path_obj)
        # 返回新的md_content和新的路径
        return {
            "md_content": md_content,
            "md_path": str(new_md_path_obj)
        }

    def update_md_file_content(self, image_with_summary_and_url_list: list[Any], md_content: str, md_path_obj: Path) -> tuple[str, Path]:
        for image_with_summary_and_url in image_with_summary_and_url_list:
            pattern = re.compile(r"!\[.*?\]\(.*?" + re.escape(image_with_summary_and_url["image_name"]) + r"\)")
            md_content = pattern.sub(
                lambda  _: f"![{image_with_summary_and_url.get('summary')}]({image_with_summary_and_url.get('image_url')})",
                md_content
            )

        new_md_path_obj = md_path_obj.parent / f"{md_path_obj.stem}_new.md"
        with open(new_md_path_obj, "w", encoding="utf-8") as f:
            f.write(md_content)
        return md_content, new_md_path_obj

    def upload_minio(self, image_with_summary_list: list[Any], md_path_obj: Path) -> list[Any]:
        # todo把图片的url继续根据上面的image_with_summary_list再去整理 {}
        # 1 上传图片到minio的哪个目录下
        # 如果有父子目录，这里尽量不要用Path对象，因为Path对象在拼接的时候会把路径当中的斜杠整错
        # 最终在minio当中目录父子级是连在一起的
        upload_dir = MinioConfig.minio_img_dir + "/" + f"{datetime.now().strftime("%Y%m%d")}" + "/" + f"{md_path_obj.stem}"
        # 2、上传文件到目录下，首先先做幂等性删除
        minio_client = get_minio_client()
        # 获取老图片的生成器对象
        old_img_generator = minio_client.list_objects(
            bucket_name=MinioConfig.minio_bucket_name,
            prefix=upload_dir,
            recursive=True
        )
        # print(old_img_generator)
        # 循环遍历生成器拿到所有的老图片对象，而且由于删除的api里面要求删除的图片对象必须是DeleteObject对象
        # 所以我们把老图片拿到后还得进行转化
        delete_object_list = [DeleteObject(item.object_name) for item in old_img_generator]
        errors = minio_client.remove_objects(
            bucket_name=MinioConfig.minio_bucket_name,
            delete_object_list=delete_object_list
        )
        # 遍历生成器，真正的删除动作
        for error in errors:
            print("error occurred when deleting object", error)

        image_with_summary_and_url_list = []
        for image_with_summary in image_with_summary_list:
            minio_client.fput_object(
                bucket_name=MinioConfig.minio_bucket_name,
                object_name=upload_dir + "/" + image_with_summary.get("image_name"),
                file_path=image_with_summary.get("image_path")
            )
            url = f"http://{MinioConfig.minio_endpoint}/{MinioConfig.minio_bucket_name}/{upload_dir}/{image_with_summary.get('image_name')}"
            image_with_summary_and_url_list.append({
                **image_with_summary,
                "image_url": url
            })
        return image_with_summary_and_url_list

    def get_image_with_summary_list(self, image_with_context_list: list[Any]) -> list[Any]:
        # 初始化模型对象
        llm = init_chat_model(
            model=LLMConfig.vl_model,
            model_provider="openai",
            api_key=LLMConfig.openai_api_key,
            base_url=LLMConfig.openai_api_base,
            temperature=LLMConfig.llm_default_temperature,
        )

        # 定义一个双端队列
        # from queue import Queue   同步队列
        # from asyncio import Queue 异步队列
        q = deque(maxlen=30)
        image_with_summary_list = []

        for image_with_context in image_with_context_list:
            current_time = time.time()
            # 获取每张图片的上文下文图片内容，交给大模型进行识别，但是大模型在识别的时候有频率限定
            # 限定频率 限频限流，这里是要用到一个令牌桶算法（难点）
            # 1、想办法判断q当中有没有空位，一上来每个图片进来的时候先盲清一下q
            while q and current_time - q[0] >= 60:
                q.popleft()

            # 2、盲清完后，q要么就是满了，要么就有位置
            if len(q) >= q.maxlen:
                # 满了等待
                need_wait_time = 60 - (current_time - q[0])
                if need_wait_time > 0:
                    time.sleep(need_wait_time)

                # 等待过后，重新获取当前时间，去q当中清理
                current_time = time.time()
                while q and current_time - q[0] >= 60:
                    q.popleft()

            q.append(current_time)

            # 把图片转换成base64编码
            with open(f"{image_with_context.get('image_path')}", "rb") as f:
                image_bytes = f.read()

            base64_bytes = base64.b64encode(image_bytes).decode("utf-8")
            # print(f'data:image/jpeg;base64,' + b64_str)

            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                # 这里用的是本地图片的路径，如果要使用网络上的图片，则需要换成对应的url就得处理这些图片（minio）
                                # 除了网络路径之外，还可以对图片进行编码，然后放到base64当中，把base64的编码url放入提示词
                                "url": 'data:image/jpeg;base64,' + base64_bytes,
                            },
                        },
                        {
                            "type": "text",
                            "text": f"""
                                                这是一张图片，图片上文部分为"{image_with_context.get("pre_text")}"，
                                        下文部分为"{image_with_context.get("post_text")}"，请用中文简要总结这张图片的摘要,字数在50字以内。
                                    """
                        },
                    ],
                },
            ]

            res = llm.invoke(messages)
            image_with_summary_list.append({
                "image_name": image_with_context.get("image_name"),
                "summary": res.content,
                "image_path": str(image_with_context.get("image_path")),
            })
        return image_with_summary_list

    def get_image_with_context_list(self, image_dir_obj, image_names: list[str], md_content) -> list[Any]:
        # 遍历每个图片的名字，从md内容当中找对应的图片及对应的图片上下文进行保存
        IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
        image_with_context_list = []  # 拿到上下文后图片暂存的位置，后面还要继续处理
        for image_name in image_names:
            suffix = Path(image_name).suffix.lower()
            if suffix not in IMAGE_EXTENSIONS:
                logger.info(f"{image_name} 不是图片，已跳过")
                continue

            pattern = re.compile(r"!\[.*?\]\(.*?" + re.escape(image_name) + r"\)")
            match = pattern.search(md_content)
            # logger.info(f"match:{match}")
            if not match:
                logger.info(f"{image_name} 在md文件中未找到")
                continue

            start, end = match.span()
            # 获取图片的上下文
            pre_text = md_content[max(start - 250, 0):start]
            post_text = md_content[end:min(end + 250, len(md_content))]
            # 每张图片拿到上下文之后先去暂存，每个图片都整理成字典
            image_with_context_list.append({
                "image_name": image_name,
                "pre_text": pre_text,
                "post_text": post_text,
                "image_path": str(image_dir_obj / image_name)# 后期大模型除了上下文也要图片内容
            })
        return image_with_context_list

    def check_md_path(self, state: ImportGraphState) -> tuple[Path, str]:
        md_path = state.get("md_path")
        if not md_path:
            logger.info("md_path不能为空")
            raise ValueError("md_path不能为空")
        md_path_obj = Path(md_path)
        if not md_path_obj.exists():
            logger.info("md_path不存在")
            raise ValueError("md_path不存在")
        with md_path_obj.open("r", encoding="utf-8") as f:
            md_content = f.read()
        return md_path_obj,md_content


if __name__ == '__main__':
    node = NodeMDImg()
    init_state = {
        "md_path":r"D:\output0624\hak180产品安全手册\hak180产品安全手册.md"
    }
    result = node(init_state)
    logger.info(json_format_tool.json_format(result))