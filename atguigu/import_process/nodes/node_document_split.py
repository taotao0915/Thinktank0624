# atguigu/import_process/nodes/node_document_split.py
import re
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

from atguigu.import_process.base import NodeBase
from atguigu.import_process.state import ImportGraphState
from tool.json_format_tool import json_format
from tool.logger import logger


class NodeDocumentSplit(NodeBase):
    """
    文档切分节点：智能文档切片
    """

    name = "node_document_split"

    def process(self, state: ImportGraphState):
        file_title, md_content, md_path_obj = self.get_md_content(state)
        split_section_list = self.get_section_list(file_title, md_content)
        final_section_list = self.get_final_chunk_list(split_section_list, md_path_obj)
        return {
            "chunks": final_section_list
        }

    def get_final_chunk_list(self, split_section_list, md_path_obj):
        spliter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", "。", "！", "？", "；", ".", "!", "?", ";", " "],
            chunk_size=300,
            chunk_overlap=50,
            length_function=len,
            add_start_index=True,
        )
        final_chunk_list = []
        for split_section in split_section_list:
            # 准备对每个section进行判断来细切
            title = split_section.get("title")
            content = split_section.get("content")
            real_content = content[len(title) + 2:] if content.startswith("#") else content

            if len(real_content) <= 300:
                final_chunk_list.append({
                    **split_section,
                    "part": 0  # 代表这个区块没被切过，序号就是0
                })
                continue

            if "<table" in real_content:
                final_chunk_list.append({
                    **split_section,
                    "part": 0  # 代表这个区块没被切过，序号就是0
                })
                continue

            split_text_list = spliter.split_text(real_content)
            for idx, split_text in enumerate(split_text_list, start=1):
                final_chunk_list.append({
                    **split_section,
                    "part": idx,  # 代表这个区块被切过了，序号就是1开始
                    "content": title + "\n\n" + split_text
                })

        # print(json_format(final_chunk_list))
        split_chunk_json_obj = md_path_obj.parent / "split_chunks.json"
        with open(split_chunk_json_obj, 'w', encoding='utf-8') as f:
            f.write(json_format(final_chunk_list))
        return final_chunk_list

    def get_section_list(self, file_title, md_content):
        split_line_list = md_content.split("\n")

        is_in_block = False
        marker = None
        code_pattern = r"^(`{3,}|~{3,})"  # ()代表分组捕获，捕获匹配到的原文内容，一个正则可以是9个，后期我们要拿哪个分组的内容，就用
        title_pattern = r'^\s*#{1,6}\s+.+'
        current_idx = 0

        # 第一种方式
        split_chunk_list = []  # 放的是每个标题前面的所有行组成的小列表，整体是一个二维列表
        for idx, split_line in enumerate(split_line_list):
            split_line = split_line.strip()
            match = re.match(code_pattern, split_line)
            if match:
                if not is_in_block:
                    marker = match.group(1)
                    is_in_block = True
                else:
                    if marker == match.group(1):
                        is_in_block = False
                        marker = None
            #           过了这个if   如果     is_in_block为True代表这个行还在代码块当中，如果是False，代表这个行不在代码块当中,再去判断是不是标题
            if not is_in_block and re.match(title_pattern, split_line):
                #                #确定这个行是标题
                split_chunk_list.append(split_line_list[current_idx:idx])
                current_idx = idx
        split_chunk_list.append(split_line_list[current_idx:])
        # print(json_format(split_chunk_list))

        split_section_list = []
        for chunk in split_chunk_list:
            content = "\n".join(chunk)
            title = chunk[0] if content.startswith("#") else "无标题"
            split_section_list.append(
                {
                    "title": title,
                    "file_title": file_title,
                    "content": content
                }
            )
        print(json_format(split_section_list))
        return split_section_list

    def get_md_content(self, state):
        md_path = state.get("md_path")
        if not md_path:
            logger.error("没有找到文件路径")
            raise Exception("没有找到文件路径")
        md_path_obj = Path(md_path)
        if not md_path_obj.exists():
            logger.error("没有找到文件")
            raise Exception("没有找到文件")
        file_title = state.get("file_title")
        if not file_title:
            logger.error("没有找到文件标题")
            raise Exception("没有找到文件标题")
        with open(md_path, "r", encoding="utf-8") as f:
            md_content = f.read()
        #       内容拿到后，我们首先要按行切分，所以我们要统一换行符
        md_content = md_content.replace("\r\n", "\n").replace("\r", "\n")
        return file_title, md_content, md_path_obj


if __name__ == '__main__':
    node = NodeDocumentSplit()
    init_state = {
        "md_path": r"D:\output0624\hak180产品安全手册\hak180产品安全手册_new.md",
        "file_title": "hak180产品安全手册"
    }

    result = node(init_state)
    logger.info(json_format(result))
