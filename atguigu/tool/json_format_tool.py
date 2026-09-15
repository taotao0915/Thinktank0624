import json

from bson import ObjectId


class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        else:
            return super().default(obj)


def json_format(data):
    return json.dumps(data,indent=4,ensure_ascii=False,cls=MongoJSONEncoder)


