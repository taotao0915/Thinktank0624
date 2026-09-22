# 闭包的概念（理解第一）
# 闭包产生的条件
# 1、内外函数嵌套
# 2、内部函数使用外部函数的变量
# 3、外部函数调用返回内部函数
# 闭包的理解
# 闭包我们说的是闭包机制，外部函数每一次调用都会产生一个独立的闭包机制
# 闭包机制是由外部函数每次调用的执行上下文和由它调用所定义的内部函数数据组成的
# 后期如果我们调用内部函数，此时内部函数的数据就会从定义它的外部函数执行上下文当中去找
# 由于每次外部函数调用都会产生新的独立闭包机制，所以后期调用内部函数的时候都不会发生混乱
from collections.abc import Iterable, Iterator

# 闭包的应用场景
# 1. 装饰器
# 2. 做封装
#     让函数外部可以间接去操作函数内部的数据
# 3. 缓存
#      利用闭包外部函数执行上下文的变量销毁不了


# 闭包的缺点
# 内存泄漏 内存无法释放了


# 闭包的注意事项
# 1、闭包千万别滥用
# 2、如果闭包使用完了，手动进行释放  让内部函数数据变为垃圾（f = None）


#装饰器
#是什么 为什么 怎么做
#装饰器是函数，基础就是闭包
#装饰器主要是用来 不改变原有函数的基础上对函数进行增强（增加功能）
#装饰器分类：1、普通装饰器（两层函数） 2、带参装饰器（三层函数） 3、类装饰器（类 + __call__）
#最基本的使用@装饰器函数
#装饰器叠加  装饰器是在函数定义的时候就执行了并不是函数调用，装饰器执行顺序是从下到上
#装饰器会影响原函数的元数据,可以使用functools.wraps来解决把原数据再修改回来


# import time
# def logger_decorator(func):
#     print("日志装饰器开始执行")
#     def wrapper(*args, **kwargs):
#         print(f"函数执行了参数是{args}")
#         result = func(*args, **kwargs)
#         print(f"函数执行结果是{result}")
#         return result
#     return wrapper
#
#
# def timer_decorator(func):
#     print("计时装饰器开始执行")
#     def wrapper(*args, **kwargs):
#         start_time = time.time()
#         result = func(*args, **kwargs)
#         end_time = time.time()
#         print(f"函数执行时间是{end_time - start_time}秒")
#         return result
#     return wrapper
#
#
# @logger_decorator
# @timer_decorator
# def add(a,b):
#     return a + b

#
# from functools import wraps
# def logger_decorator(func):
#     print("日志装饰器开始执行")
#     @wraps(func) #保留原函数的元数据，不发生改变
#     def wrapper(*args, **kwargs):  # 内层函数：接收任意参数，包裹原函数
#         print(f"函数执行了参数是{args}")  # 调用前：打印传入的参数
#         result = func(*args, **kwargs)  # 调用原函数并保存返回值
#         print(f"函数执行结果是{result}")  # 调用后：打印返回结果
#         return result  # 返回原函数结果，保证功能不被改变
#     return wrapper
#
#
# @logger_decorator
# def add(a,b):
#     return a + b
# print(add(10, 20))
# print(add.__name__)


#迭代器
#可迭代对象是拥有迭代器方法,可以拿到迭代器的对象,但是可迭代对象不一定是迭代器
# 什么是迭代器
# 迭代器是一个实现迭代器协议的一个对象
# 迭代器是一个类的实例,这个类必须包含两个方法  __iter__ 和 __next__
# 要实现一个迭代器
#     1、保存当前的初始状态，结束的状态
#     2、写__iter__方法，返回自己
#     3、写__next__方法，返回当前状态，并更新状态  后期我们调用对象的这个方法，就会生成一个数据
#     4、迭代器的结束的时候要抛出StopIteration异常
#迭代器都是不可逆的，只能往前走，不能往后走
#迭代器的作用：惰性生成  节约内存


# str1 = 'abc'
# a = 100
# # 判断一个对象是不是可迭代对象
# print(isinstance(str1, Iterable))
# print(isinstance(a, Iterable))
#
# # 判断一个对象是不是迭代器
# print(isinstance(str1, Iterator))
# print(isinstance(a, Iterator))



#生成器
#生成器是一个特殊的迭代器对象，生成器对象要想获取到必须先要有一个生成器函数
#生成器函数是普通函数包含yield关键字
#函数调用后就会返回一个生成器对象
# 生成器对象也是和迭代器对象一样，也是用来进行惰性生成，节约内存
# 生成器对象要想获取到数据，必须调用对象的__next__()方法 或者 for循环
# 生成器是生成器，生成器也是迭代器，生成器还是可迭代对象
# 生成器对象可以调用send进行双向通信

# def numgenderator(n):
#     num = 1
#     step = 1
#     while num <= n:
#         value = yield num
#         print(value)
#         if value:
#             step = value
#         num += step
#
# num_generator = numgenderator(100)
# # next(num_generator) #==> num_generator.send(None)
# print(num_generator.send(None))  #第一次没有发送值，目的是为了启动生成器的函数执行
# print(num_generator.send(None))
# print(num_generator.send(None))
# print(num_generator.send(None))
# print(num_generator.send(None))
#
#
# # 我要改变步长
# print(num_generator.send(2))
#
# print(num_generator.send(None))
# print(num_generator.send(None))
# print(num_generator.send(None))
#
# # 我要改步长
#
# print(num_generator.send(1))


