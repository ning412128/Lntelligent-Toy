from flask import Blueprint,jsonify,request

from ChatRedis import get_all_chat
from setting import MONGO_DB,RET
from bson import ObjectId

friend = Blueprint("friend",__name__)

@friend.route("/friend_list",methods=["POST"])
def friend_list():
    _id = request.form.get("_id")

    user_info = MONGO_DB.user.find_one({"_id":ObjectId(_id)})
    friend_list = user_info.get("friend_list")
    chat_count = get_all_chat(_id)


    # friend_list.append(chat_count)
    RET["code"] = 0
    RET["msg"] = "查询好友列表"
    RET["data"] = {"friend_list":friend_list,"chat_count":chat_count}

    #方法二
    # for index,friend in enumerate(friend_list):
    #     friend_list[index]["chat_count"] = chat_count.get(friend.get("friend_id"))
    #
    # RET["code"] = 0
    # RET["msg"] = "查询好友列表"
    # RET["data"] = friend_list


    return jsonify(RET)

@friend.route("/add_req",methods=["POST"])
def add_req():
    req_info = request.form.to_dict()

    if req_info.get("type") == "app":
        req_user_info = MONGO_DB.user.find_one({"_id":ObjectId(req_info.get("req_user"))})
    else:
        req_user_info = MONGO_DB.toys.find_one({"_id":ObjectId(req_info.get("req_user"))})

    req_info["req_user_nick"] = req_user_info.get("nickname") if req_user_info.get("nickname") else req_user_info.get("baby_name")
    req_info["req_user_avatar"] = req_user_info.get("avatar")
    req_info["status"] = 0 # 1 同意 2 拒绝 0 不理

    MONGO_DB.request.insert_one(req_info)

    RET["code"] = 0
    RET["msg"] = "发起好友请求"
    RET["data"] = {}

    return jsonify(RET)

@friend.route("/req_list",methods=["POST"])
def req_list():
    _id = request.form.get("_id")
    user_info = MONGO_DB.user.find_one({"_id":ObjectId(_id)})
    bind_toy = user_info.get("bind_toy")

    req = list(MONGO_DB.request.find({"add_user":{"$in":bind_toy},"status":0}))

    for index,item in enumerate(req):
        req[index]["_id"] = str(item.get("_id"))

    RET["code"] = 0
    RET["msg"] = "请求查询"
    RET["data"] = req

    return jsonify(RET)


@friend.route("/ref_req", methods=["POST"])
def ref_req():
    req_id = request.form.get("req_id")
    MONGO_DB.request.update_one({"_id": ObjectId(req_id)}, {"$set": {"status": 2}})

    RET["code"] = 0
    RET["msg"] = "拒绝请求"
    RET["data"] = {}

    return jsonify(RET)


@friend.route("/acc_req",methods=["POST"])
def acc_req():
    req_id = request.form.get("req_id")
    remark = request.form.get("remark")

    MONGO_DB.request.update_one({"_id": ObjectId(req_id)}, {"$set": {"status": 1}})
    req_info = MONGO_DB.request.find_one({"_id": ObjectId(req_id)})

    # 发起请求的用户
    req_user = req_info["req_user"]
    if req_info["type"] == "app":
        req_user_info = MONGO_DB.user.find_one({"_id": ObjectId(req_user)})
    else:
        req_user_info = MONGO_DB.toys.find_one({"_id": ObjectId(req_user)})

    # 被添加的好友 收到请求的用户
    add_user = req_info["add_user"]
    add_user_info = MONGO_DB.toys.find_one({"_id": ObjectId(add_user)})

    # 创建双方聊天的对话框
    chat_window = MONGO_DB.chats.insert_one({"user_list":[req_user,add_user],"chat_list":[]})

    # 发起请求的用户 添加 收到请求的用户
    req2add_friend={
        "friend_id" : add_user,
        "friend_nick" : add_user_info.get("toy_name"),
        "friend_remark" : req_info.get("remark"),
        "friend_avatar" :  add_user_info.get("avatar"),
        "friend_chat" : str(chat_window.inserted_id),
        "friend_type" : "toy"
    }
    # 更新数据
    if req_info["type"] == "app":
        MONGO_DB.user.update_one({"_id": ObjectId(req_user)},{"$push":{"friend_list":req2add_friend}})
    else:
        MONGO_DB.toys.update_one({"_id": ObjectId(req_user)},{"$push":{"friend_list":req2add_friend}})


    # 收到请求的用户 添加 发起请求的用户
    add2req_friend={
        "friend_id": req_user,
        "friend_nick": req_user_info.get("toy_name") if req_user_info.get("toy_name") else req_user_info.get("nickname"),
        "friend_remark": remark,
        "friend_avatar": req_user_info.get("avatar"),
        "friend_chat": str(chat_window.inserted_id),
        "friend_type": req_user_info.get("type")
    }

    MONGO_DB.toys.update_one({"_id": ObjectId(add_user)}, {"$push": {"friend_list": add2req_friend}})

    RET["code"] = 0
    RET["msg"] = "添加好友"
    RET["data"] = {}

    return jsonify(RET)


