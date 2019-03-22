from flask import Blueprint,jsonify,request
from setting import MONGO_DB,RET
from bson import ObjectId

devices = Blueprint("devices",__name__)

@devices.route("/device_key",methods=["POST"])
def device_key():
    device_dict = request.form.to_dict()
    res = MONGO_DB.devices.find_one(device_dict)
    # device_key是否已经做过绑定了？
    if res:
        RET["code"] = 0
        RET["msg"] = "扫描成功"
        RET["data"] = device_dict
        toy = MONGO_DB.toys.find_one(device_dict,{"bind_user":0,"friend_list":0,"device_key":0})
        if toy:
            toy["_id"] = str(toy.get("_id"))
            RET["code"] = 2
            RET["msg"] = "添加好友请求"
            RET["data"] = toy

    else:
        RET["code"] = 1
        RET["msg"] = "请不要乱扫"
        RET["data"] = {}

    return jsonify(RET)


@devices.route("/bind_toy",methods=["POST"])
def bind_toy():
    info = request.form.to_dict()
    """
    info = {
        toy_name:toy_name,
        baby_name:baby_name,
        remark:remark,
        device_key : Sdata.device_key,
        user_id:window.localStorage.getItem("user_id")
    }
    """
    # 谁来绑定 - app 用户
    user_info = MONGO_DB.user.find_one({"_id":ObjectId(info.get("user_id"))})

    # 由设备创建玩具
    # // 玩具的名字 √
    # // 伙伴名字 主人名字 √
    # // 谁跟谁绑定 ？ window.localStorage.getItem("user_id")
    # // 主人对用户的称呼 √
    # // 玩具好友列表 ？
    # // 头像 ？

    #创建app与玩具之间聊天的对话窗口
    chat_window = MONGO_DB.chats.insert_one({"user_list":[],"chat_list":[]})

    #填写玩具基本信息
    toy_info = {
        "device_key":info.get("device_key"),
        "toy_name":info.get("toy_name"),
        "baby_name":info.get("baby_name"),
        "bind_user":info.get("user_id"),
        "avatar":"toy.jpg",
        "friend_list":[]
    }

    #创建玩具的第一个好友 - app_user
    toy_first_friend={
        "friend_id":info.get("user_id"),
        "friend_nick":user_info.get("nickname"),
        "friend_remark":info.get("remark"),
        "friend_avatar":user_info.get("avatar"),
        "friend_chat":str(chat_window.inserted_id),
        "friend_type":"app"
    }

    # 将好友信息追加到 玩具基本信息中
    toy_info["friend_list"].append(toy_first_friend)

    toy = MONGO_DB.toys.insert_one(toy_info)
    # 以上就是创建玩具的过程

    # 给App创建好友 - 玩具
    user_add_firend = {
        "friend_id": str(toy.inserted_id),
        "friend_nick": toy_info.get("toy_name"),
        "friend_remark": toy_info.get("baby_name"),
        "friend_avatar": toy_info.get("avatar"),
        "friend_chat": str(chat_window.inserted_id),
        "friend_type": "toy"
    }

    # 增加 app用户的好友
    if user_info.get("friend_list"):
        user_info["friend_list"].append(user_add_firend)
    else:
        user_info["friend_list"] = [user_add_firend]

    # app用户增加玩具绑定信息
    if user_info.get("bind_toy"):
        user_info["bind_toy"].append(str(toy.inserted_id))
    else:
        user_info["bind_toy"] = [str(toy.inserted_id)]

    # 修改用户数据库中的数据
    MONGO_DB.user.update_one({"_id":user_info.get("_id")},{"$set":user_info})
    # MONGO_DB.user.update_one({"_id":user_info.get("_id")},{"$push":{"friend_list":user_add_firend}})

    # 聊天窗口信息绑定
    MONGO_DB.chats.update_one({"_id":chat_window.inserted_id},{"$set":{"user_list":[str(user_info.get("_id")),str(toy.inserted_id)]}})

    RET["code"] = 0
    RET["msg"] = "玩具绑定成功"
    RET["data"] = {}
    return jsonify(RET)


@devices.route("/toy_list",methods=["POST"])
def toy_list():
    _id = request.form.get("_id")
    # 查询用户已经绑定的玩具
    # 1.先查用户再查玩具
    # 2.查玩具的bind_user
    res_list = list(MONGO_DB.toys.find({"bind_user":_id}))

    for index,item in enumerate(res_list):
        res_list[index]["_id"] = str(item.get("_id"))

    RET["code"] = 0
    RET["msg"] = "查询绑定玩具列表"
    RET["data"] = res_list

    return jsonify(RET)



@devices.route("/toy_start",methods=["POST"])
def toy_start():
    device_key = request.form.to_dict()  # {device_key:"123123123"}
    toy = MONGO_DB.toys.find_one(device_key)
    # 玩具是不是授权的 , 是不是绑定的
    if toy:  # 证明玩具已经授权了 并且 绑定了用户
        # 返回内容:除协议外 - 玩具ID
        ret = {
            "toy_id":str(toy.get("_id")),
            "music":"Success.mp3"
        }
        return jsonify(ret) # {"toy_id":str(toy.get("_id"))}
    else:  # 代表玩具没有授权 或 没有绑定
        device = MONGO_DB.devices.find_one(device_key)
        if device:  # 玩具已经授权，但是未进行绑定
            ret = {
                "toy_id": "None",
                "music": "Nobind.mp3"
            }
            return jsonify(ret) # {toy_id:"None"}
        else:  # 代表玩具没有授权
            ret = {
                "music": "Nolic.mp3"
            }
            return jsonify(ret)  # {}
