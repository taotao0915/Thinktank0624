# def node_a(state):
#     pass
#
#
# builder = StateGraph(state_schema=ImportGraphState)
#
# builder.add_node("node_a",node_a)
# nodea我们只是添加到节点，这个节点函数并不是我们自己加括号调用的，而是graph框架在执行的时候自动调用的
# 我们现在的感受是，调用nodea 就会执行一个函数的业务代码


# 函数节点转化为类式节点

# class NodeA:
#     def __call__(self, state):
#         pass
#
#
# builder = StateGraph(state_schema=ImportGraphState)
# builder.add_node("node_a", NodeA())
# __call__是一个魔法方法，一个这个类的实例化对象被当做函数用的时候也就是加括号的时候，就会调用这个方法



# 如果图当中有多个节点，每个节点后期都对应一个类，每个类里面都有__call__方法
# 此时我们就可以抽一个父类，在父类当中写一个共同的__call__方法



# 如果把call抽离到父类当中，子类每个节点的业务是不一样的，怎么办呢？
# 让每个节点都先去执行父类的call,父类做成一个抽象类
# 1、父类不能实例化对象
# 2、父类里面必须有一个抽象方法
# 3、子类必须实现父类的抽象方法（重写）
# 最终 在父类当中写一个抽象方法process,那么所有的子类都必须实现这个方法，在子类的这个方法当中自己写自己的业务逻辑
# 父类的__call__方法当中调用process




