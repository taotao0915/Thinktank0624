import time
from abc import ABC, abstractmethod
from atguigu.tool.logger import logger
from tool.task_utils import add_running_task, add_done_task, add_node_duration


class NodeBase(ABC):

    name = "NodeBase"

    def __init__(self):
        if self.name == "NodeBase":
            logger.info("子类{self.__class__.__name__}需要提供name属性")
            raise NotImplementedError("子类需要提供name属性")

    def __call__(self, state):
        task_id = state.get("task_id","")
        try:
            logger.info(f"Node {self.name} is processing data...")
            start_time = time.time()
            add_running_task(task_id, self.name)  # 设置节点开始执行的状态
            result = self.process(state)
            logger.info(f"Node {self.name} has finished processing.")
            end_time = time.time()
            add_done_task(task_id, self.name)  # 设置节点执行结束的状态
            add_node_duration(task_id, self.name, end_time - start_time)  # 设置节点执行的时间
            return result
        except Exception as e:
            logger.error(f"{self.name}处理节点出错")
            raise e

    @abstractmethod
    def process(self, state):
        pass

