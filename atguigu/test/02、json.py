# 是什么
#     json是一种数据格式，俗称叫json串，本质是一个字符串，为了前后端进行数据交互而出现的
import json

from atguigu.tool.json_format import json_format

#     json出来之前，xml是传递请求体参数的主要载体：
#     前后端交互如果需要传递的数据量很大，使用请求体去传递参数的时候，开始用的是xml格式，但是xml太重了，xml是html的爹
#     它也是标签语言比如我们要传递一个对象数据，此时就用xml的标签标识,好处是标签可以自定义，但是html不行
#     <star>
#         <name>杨幂</name>
#         <age>18</age>
#         <gender>女</gender>
#     </star>
#
#     虽然xml可以让我们带大量的数据去后端，但是它毕竟是一个文件，文件一般传递的时候比较重，内容也不单纯，我们要的内容有很多
#     标签的东西，这些东西没用还占带宽，因此xml可以用但是不好。xml本身传递给后端，后端在解析xml的时候也很麻烦
#
#
#     到了现在，xml几乎已经不用来进行前后端交互了。xml现在能看到的就是用来做配置文件，比如nginx的配置文件，因为json
#      json后期就专门用来传递比较复杂的请求体参数



# 为什么
#     json如果没有，假设前端要请求给后端一个复杂数据，就用的是前端js的语法数据类型，假设能够传递给后端，后端pyhon当中是没有
# 前端传递的这种数据类型的，python是没办法去处理前端传递的这个数据。同理，后端给前端反一个后端的python的数据类型，前端就算能
# 接收到，前端js也没有办法去处理后端传递的这个数据类型。因此，json的出现主要就是为了做中转。
# 前端js传递数据给后端的时候先去序列化为json,传递到后端，后端对json进行反序列化，拿到后端语言的数据，之后再进行处理
# 后端返回给前端数据的时候先把数据序列化为json，前端拿到json之后再反序列化，拿到js的数据类型，再用js语法去操作处理
# json就是数据本身做的字符串，没有额外的其它数据开销（标签等），轻量占带宽小，效率高



# 怎么做
# 前端js怎么做,前端有对应的工具。
#     JSON.stringify()  序列化json
#     JSON.parse() 反序列化json

# 后端python怎么做，python也有对应的工具库
#     import json
#     json.dumps() 序列化json
#     json.loads() 反序列化json

# 一般情况下，我们和前端对应数据的时候，前端的对象对应到后端就是字典或者对象，前端的数组对应到后端就是列表
# 我们用的比较多的就是字典或者字典的列表

dict1 = {
    'name':'杨幂',
    'age':18
}

# dict_json = json.dumps(dict1,ensure_ascii=False)
# print(dict_json,type(dict_json))

# 如果这个json串是反给前端的，前端后期需要拿到json后
# JSON.parse(dict_json)转化为前端的对象，进行操作


#如果这个json串是前端发请求给我们传过来的，我们拿到json串之后
# 我们也得把json串转化为python的字典或者对象进行操作
# json_dict = json.loads(dict_json)
# print(json_dict,type(json_dict))
# json_dict["age"] = 40
# print(json_dict,type(json_dict))



# 还有一个用法，直接操作文件,json是可以写入json文件的，也可以是一个文件格式
# json.dump() 会把python的数据序列化直接写入到json文件当中
# json.load() 会把json文件的内容反序列化，转化为python的数据类型
# with open('1.json','w',encoding='utf-8') as f:
#     json.dump(dict1,f,ensure_ascii=False)


# with open('1.json','r',encoding='utf-8') as f:
#     result = json.load(f)
#     print(result,type(result))
