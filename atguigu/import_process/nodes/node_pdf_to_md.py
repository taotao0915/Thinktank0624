# atguigu/import_process/nodes/node_pdf_to_md.py
import json
import shutil
import time
import zipfile
from pathlib import Path
from typing import Any

from atguigu.config.config import MinerUConfig
from atguigu.import_process.base import NodeBase
from atguigu.import_process.state import ImportGraphState
from atguigu.tool.json_format_tool import MongoJSONEncoder
from atguigu.tool.logger import logger


class NodePDFToMD(NodeBase):
    """
    PDF 转 Markdown 节点：PDF结构化解析
    """

    name = "node_pdf_to_md"

    def process(self, state: ImportGraphState):
        local_dir_obj, pdf_path, pdf_path_obj = self.check_pdf(state)

        batch_id = self.upload_pdf_file(pdf_path, pdf_path_obj)

        url = self.get_md_zip_url(batch_id)

        md_content, new_origin_md_obj = self.handler_md_zip_url(local_dir_obj, pdf_path_obj, url)

        return {
            "md_content": md_content,
            "md_path": str(new_origin_md_obj)
        }

    def handler_md_zip_url(self, local_dir_obj: Path, pdf_path_obj: Path, url) -> tuple[str, Path]:
        import requests
        res = requests.get(url)
        if res.status_code != 200:
            logger.error(f"下载压缩包失败: {res.status_code}")
            raise Exception(f"下载压缩包失败: {res.status_code}")

        zip_file_path_obj = local_dir_obj / f"{pdf_path_obj.stem}.zip"
        with open(zip_file_path_obj, 'wb') as f:
            f.write(res.content)

        unzip_dir_path_obj = local_dir_obj / f"{pdf_path_obj.stem}"
        if unzip_dir_path_obj.exists():
            shutil.rmtree(unzip_dir_path_obj)
            logger.info(f"解压目录已存在，已删除原目录")

        unzip_dir_path_obj.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_file_path_obj) as zip_ref:
            zip_ref.extractall(unzip_dir_path_obj)

        origin_md_path_obj = unzip_dir_path_obj / f"full.md"
        new_origin_md_obj = origin_md_path_obj.with_name(f"{pdf_path_obj.stem}.md")
        origin_md_path_obj.rename(new_origin_md_obj)

        with open(new_origin_md_obj, 'r', encoding="utf-8") as f:
            md_content = f.read()

        return md_content, new_origin_md_obj

    def get_md_zip_url(self, batch_id) -> Any:
        # 根据batch_id轮询mineru服务器获取压缩包的url地址
        import requests
        token = MinerUConfig.mineru_token
        batch_id = batch_id
        url = f"https://mineru.net/api/v4/extract-results/batch/{batch_id}"
        header = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        max_time = 120
        start_time = time.time()
        # 轮询获取压缩包url
        while True:
            try:
                time.sleep(1)
                res = requests.get(url, headers=header)
                if res.status_code != 200:
                    logger.error(f"轮询请求失败: {res.status_code}")
                    raise Exception(f"轮询请求失败: {res.status_code}")
                result = res.json()

                if result["code"] != 0:
                    logger.error(f"轮询请求获取数据失败")
                    raise Exception(f"轮询请求获取数据失败")

                data = result["data"]

                if data["extract_result"][0].get("state") != "done":
                    logger.warning(f"轮询请求获取数据不正确")
                    raise Exception(f"轮询请求获取数据不正确")

                url = data["extract_result"][0]["full_zip_url"]
                break
            except Exception as e:
                # logger.error(e)
                if (time.time()-start_time) > max_time:
                    logger.error(f"轮询请求获取数据超时")
                    raise Exception(f"轮询请求获取数据超时")
                continue

        logger.info(f"压缩包下载成功，url: {url}")
        return url

    def upload_pdf_file(self, pdf_path: str, pdf_path_obj: Path) -> Any:
        import requests

        token = MinerUConfig.mineru_token
        url = "https://mineru.net/api/v4/file-urls/batch"
        header = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        data = {
            "files": [
                {"name": f"{pdf_path_obj.name}", "data_id": "abcd"}
            ],
            "model_version": "vlm"
        }
        file_path = [f"{pdf_path}"]

        response = requests.post(url, headers=header, json=data)
        if response.status_code != 200:
            logger.error(f"请求失败: {response.status_code}")
            raise Exception(f"请求失败: {response.status_code}")

        result = response.json()
        if result["code"] != 0:
            logger.error(f"请求获取数据失败")
            raise Exception(f"请求获取数据失败")

        batch_id = result["data"]["batch_id"]
        urls = result["data"]["file_urls"]
        for i in range(0, len(urls)):
            with open(file_path[i], 'rb') as f:
                res_upload = requests.put(urls[i], data=f)
                if res_upload.status_code == 200:
                    logger.info(f"{urls[i]}上传成功")
                else:
                    logger.error(f"{urls[i]}上传失败")
                    raise Exception(f"{urls[i]}上传失败")

        logger.info(f"PDF上传成功，batch_id: {batch_id}")
        return batch_id

    def check_pdf(self, state: ImportGraphState) -> tuple[Path, str, Path]:
        pdf_path = state.get("pdf_path")  # 获取PDF路径
        local_dir = state.get("local_dir")  # 获取本地输出目录路径
        if pdf_path is None:
            raise ValueError("缺少PDF路径")

        pdf_path_obj = Path(pdf_path)
        if not pdf_path_obj.exists():
            raise ValueError("PDF文件不存在")

        if local_dir is None:
            raise ValueError("缺少本地输出目录路径")

        local_dir_obj = Path(local_dir)
        if not local_dir_obj.exists():
            local_dir_obj.mkdir(parents=True, exist_ok=True)
        return local_dir_obj, pdf_path, pdf_path_obj


if __name__ == "__main__":
    node = NodePDFToMD()
    init_state = {
        "pdf_path":r"D:\output0624\hak180产品安全手册.pdf",
        "local_dir":r"D:\output0624"
    }
    result = node(init_state)
    logger.info(result)