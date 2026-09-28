import tool.task_utils as module_a
import atguigu.tool.task_utils as module_b

print(module_a.__file__ == module_b.__file__)      # True，同一个文件
print(module_a is module_b)                        # False，两个模块
print(module_a.queue_dict is module_b.queue_dict)  # False，两个字典