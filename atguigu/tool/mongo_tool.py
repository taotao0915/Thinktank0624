import time

from pymongo import MongoClient

from atguigu.config.config import MongoConfig
from atguigu.tool.json_format_tool import json_format

# client = MongoClient('mongodb://user:password@localhost:27017/mydatabase?authSource=admin')
# db = client['mydatabase']
# collection = db['mycollection']
# collection.insert_many() #最终我们其实是想拿到表对象
# 表对象当中封装了增删改查操作方法




mongo_client = None
def get_mongo_client():
    global mongo_client
    if mongo_client is None:
        mongo_client = MongoClient(MongoConfig.mongo_url)
    return mongo_client

mongo_tool = None
def get_mongo_tool():
    global mongo_tool
    if mongo_tool is None:
        client = get_mongo_client()
        db = client[MongoConfig.mongo_db_name] #没有就创建数据库
        mongo_tool = db["chat_history"] #没有就创建集合
        mongo_tool.create_index([("session_id", 1), ("ts", -1)])
        #创建联合唯一索引 目的就是后续执行按照session_id和ts（倒序）查找的时候效率会高
    return mongo_tool

# 查


# 增改（全量改）


# 删
# clear_history清空某个session_id的所有消息
def clear_history(session_id):
    mongo_tool = get_mongo_tool() #拿到表对象
    mongo_tool.delete_many({"session_id": session_id})
# save_chat_message保存历史记录（根据id决定是添加还是修改）
def add_or_update_message(session_id,role,text,rewritten_query=None,item_names=None,ts=None,message_id=None):
    mongo_tool = get_mongo_tool()
    #添加的时候，我们传递过来的数据中是没有_id的
    #修改的时候（全量），我们传递过来的数据中一定有_id
    #除了_id以外，添加和修改的其它数据字段是一样的
    #修改的数据一定是从数据库拿到的所以必然有id
    #添加的数据还没有进过数据库，所以没有id
    if not message_id:
        #添加
        res = mongo_tool.insert_one({
            "session_id": session_id,
            "role": role,
            "text": text,
            "rewritten_query": rewritten_query,
            "item_names": item_names,
            "ts": ts or int(time.time()),
        })
        return res.inserted_id
    else:
        #修改
        res = mongo_tool.update_one({"_id": message_id}, {"$set": {
            "session_id": session_id,
            "role": role,
            "text": text,
            "rewritten_query": rewritten_query,
            "item_names": item_names,
            "ts": ts or int(time.time()),
        }})
        return res.modified_count #仅仅是为了返回一个东西，后期也不用

# get_recent_messages 根据session_id获取最近的n条消息
def get_recent_messages(session_id,n=10):
    mongo_tool = get_mongo_tool()
    res = mongo_tool.find({"session_id": session_id}).sort("ts", -1).limit(n)
    print(res,type(res))
    return list(res)

if __name__ == '__main__':
    # res = add_or_update_message("test_001", "user", "咨询下烫金机。")
    # print(res,type(res))
    # res2 = add_or_update_message("test_001", "assistant", "您好。请问是哪个型号")
    # print(res2)
    # add_or_update_message("test_001", "user", "hak180")
    # add_or_update_message("test_001", "assistant", "具体有什么问题呢？")


    # clear_history("test_001")

    res = get_recent_messages("test_001")
    print(json_format(res))



