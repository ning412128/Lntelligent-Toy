from flask import Blueprint,jsonify,request

from ChatRedis import get_all_chat
from setting import MONGO_DB
from bson import ObjectId

user = Blueprint("user",__name__)

@user.route("/reg",methods=["POST"])
def reg():
    user_info = request.form.to_dict()
    gender = user_info.get("gender")
    user_info["nickname"] = "女神" if gender == "1" else "男神"
    user_info["avatar"] = "mama.jpg" if gender == "1" else "baba.jpg"
    MONGO_DB.user.insert_one(user_info)

    return jsonify({"code":0,"msg":"注册成功"})


@user.route("/login",methods=["POST"])
def login():
    user_info = request.form.to_dict()
    res = MONGO_DB.user.find_one(user_info,{"password":0})
    if res:
        res["_id"] = str(res.get("_id"))
        return jsonify({"code": 0, "msg": "登录成功","data":res})

    return jsonify({"code": 1, "msg": "登录失败，who are you？","data":{}})


@user.route("/auto_login",methods=["POST"])
def auto_login():
    _id = request.form.get("_id")
    res = MONGO_DB.user.find_one({"_id":ObjectId(_id)},{"password":0})
    if res:
        res["_id"] = str(res.get("_id"))
        # 聊天数量
        chat_count = get_all_chat(str(res.get("_id")))
        res["chat_count"] = chat_count
        print(res)
        return jsonify({"code": 0, "msg": "登录成功","data":res})

    return jsonify({"code": 1, "msg": "登录失败，who are you？","data":{}})