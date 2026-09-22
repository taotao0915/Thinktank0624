#是什么
    #协程也叫微线程，是一种用户态的轻量级线程。协程依赖线程，协程也是并发不能并行，因为协程也是受用户代码控制的
    #协程虽然依赖线程，但是几乎没有任何资源开销，切换的时候没有资源消耗。性能比线程还要高
    #以后碰见io密集型，就用协程的几乎全是协程，线程虽然也可以做到并发，但是性能不如协程
    #和多进程多线程根本不属于一个系统，多进程和多线程是操作系统级别的（操作系统进行控制切换），协程是用户态的（代码进行控制切换）
import asyncio


# 事件循环（可以理解成底层代码，有一个死循环，一直循环每个协程任务，管理协程任务的状态）
    # 协程任务状态：1、就绪 2、挂起 3、运行



    # asyncio
    # 模块（async / await 语法）异步IO库
    #
    # asyncio是Python
    # 标准库中用于异步编程和并发任务管理的核心库。它的基础是事件循环，用来调度协程（coroutines），让它们能够非阻塞地并发执行。
    # 这种编程模型在处理大量I / O密集型任务时非常高效，如网络操作、文件读写等。主要是控制协程的执行顺序
    #
    # 事件循环
    # 管理所有协程任务的状态（就绪 / 运行 / 挂起）。
    # 当协程挂起（如等待 IO响应）时，切换到其他就绪协程。
    # 事件完成后，唤醒对应的协程继续执行。
    # 类似一个死循环遍历列表里面的任务，哪个可以执行哪个不可以执行，哪个可以执行就去执行
    #
    # asyncio的常用方法
    # async 在函数定义前面代表创建一个协程，函数调用后会返回协程，而不是直接执行
    # await 在协程函数中才能使用，用来等待其他异步操作的完成，也是切换协程任务执行的标志
    # run
    # 启动事件循环，传入主协程
    # create_task()
    # 把协程包装成并发任务，可以高并发执行这些任务
    # 开启并发的开关
    # gather
    # 并发执行多个协程任务，需要在run内部调用执行，run是启动事件循环，
    # gather是把多个任务并发执行并收集结果（在已经启动的事件循环中）
    # sleep
    # 模拟异步任务中的延迟
    #

#为什么
    # asyncio在处理并发I / O密集型任务时非常强大，使用它可以避免传统多线程编程中的锁和上下文切换开销。

#怎么做
    # 1单协程任务  asyncio.run(协程任务对象)
    # 2多协程任务
#       把任务先创建成并发任务 asyncio.create_task(协程任务对象)
#       调用asyncio.gather(并发任务)
#       把高并发的代码封装成单协程任务调用run


# async 关键字 异步的意思，一般写在函数定义前面，代表这函数是一个异步函数，也叫协程函数
# 一个函数一旦加了async 函数调用的时候，返回值必然是协程对象而不看return，因为此时函数的代码是没走的
# 要想执行写成函数里面的代码，必须让协程对象进入事件循环，然后才有可能执行

async def get_url(url):
    import requests
    response = requests.get(url)
    return response.status_code


async def main(urls):
    tasks = [asyncio.create_task(get_url(url)) for url in urls]
    result_list = await asyncio.gather(*tasks)  # 并发执行所有的并发任务  效率贼高，返回的每个协程任务执行行吗的返回值组成的列表
    return result_list

if __name__ == '__main__':
    # 单协程任务的使用
    # print(asyncio.run(get_url("http://www.baidu.com")))
    # asyncio.run(get_url("http://www.baidu.com"))

    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # res = loop.run_until_complete(get_url("http://www.baidu.com"))
    # print(res)
    # 多协程任务的使用

    urls = [
        "http://www.baidu.com",
        "http://www.taobao.com",
        "http://www.jd.com"
    ]

    result = asyncio.run(main(urls))
    print(result)











