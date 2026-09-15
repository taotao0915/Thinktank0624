from abc import ABC, abstractmethod
from atguigu.tool.logger import logger

class NodeBase(ABC):

    name = "NodeBase"

    def __init__(self):
        if self.name == "NodeBase":
            logger.info("子类{self.__class__.__name__}需要提供name属性")
            raise NotImplementedError("子类需要提供name属性")

    def __call__(self, state):
        logger.info(f"Node {self.name} is processing data...")
        result = self.process(state)
        logger.info(f"Node {self.name} has finished processing.")
        return result

    @abstractmethod
    def process(self, state):
        pass

