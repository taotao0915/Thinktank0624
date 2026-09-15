# atguigu/import_process/nodes/node_entry.py
from pathlib import Path

from atguigu.import_process.base import NodeBase
from atguigu.import_process.state import ImportGraphState
from atguigu.tool.logger import logger


class NodeEntry(NodeBase):
    """
    入口节点：任务分发
    """

    name = "node_entry"

    def process(self, state: ImportGraphState):
        local_file_path = state.get("local_file_path")  # 获取输入文件路径

        if local_file_path is None:
            raise ValueError("缺少文件路径")

        path = Path(local_file_path)
        if not path.exists():
            raise ValueError("文件不存在")

        file_title = path.stem  # 文件名（不包括后缀）
        suffix = path.suffix  # 文件后缀
        if suffix == ".pdf":
            return {
                "is_pdf_read_enabled": True,
                "file_title": file_title,
                "pdf_path": local_file_path
            }
        elif suffix == ".md":
            return {
                "is_md_read_enabled": True,
                "file_title": file_title,
                "md_path": local_file_path
            }
        else:
            raise ValueError(f"文件格式{suffix}不支持")