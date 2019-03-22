import json
from setting import RDB

# 设置
def set_chat(to_user,from_user):
    # to_user : {from_user : 1}
    # 我 to_user
    # 你 from_user
    to_user_chat = RDB.get(to_user)
    if to_user_chat:
        to_user_chat_dict = json.loads(to_user_chat)
        try:
            to_user_chat_dict[from_user] += 1
        except KeyError:
            to_user_chat_dict[from_user] = 1
    else:
        to_user_chat_dict = {from_user:1}

    RDB.set(to_user,json.dumps(to_user_chat_dict))

# 读取
def get_chat(to_user,from_user):
    to_user_chat = RDB.get(to_user)
    if to_user_chat:
        to_user_chat_dict = json.loads(to_user_chat)
        count = to_user_chat_dict.get(from_user)
        to_user_chat_dict[from_user] = 0

    else:
        to_user_chat_dict = {from_user:0}
        count = 0

    RDB.set(to_user,json.dumps(to_user_chat_dict))

    return count

# 拿出所有的未读消息
def get_all_chat(app_id):
    app_chat = RDB.get(app_id)

    if app_chat:
        app_chat_dict = json.loads(app_chat)
        app_chat_dict["count"] = sum(app_chat_dict.values())
    else:
        app_chat_dict = {"count":0}

    return app_chat_dict
