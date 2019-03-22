from flask import Blueprint,jsonify,send_file,request

from baidu_ai import text2audio
from setting import MONGO_DB,COVER,MUSIC,CHATS,RET
import os,time
from bson import ObjectId
from ChatRedis import get_chat

chats = Blueprint("chats",__name__)

@chats.route("/chat_list",methods=["POST"])
def chat_list():
    chat_id = request.form.get("chat_id")
    to_user = request.form.get("to_user")
    from_user = request.form.get("from_user")
    chat_window = MONGO_DB.chats.find_one({"_id":ObjectId(chat_id)})
    # chat_list = chat_window.get("chat_list") # ["12313213214134","435278346587263475"]
    get_chat(to_user,from_user)

    RET["code"] = 0
    RET["msg"] = "查询聊天记录"
    RET["data"] = chat_window.get("chat_list")[-20:]

    return jsonify(RET)

@chats.route("/recv_message",methods=["POST"])
def recv_message():
    chat_info = request.form.to_dict()
    # {from_user,to_user}
    chat = MONGO_DB.chats.find_one({"user_list":{"$all":[chat_info.get("from_user"),chat_info.get("to_user")]}})
    chat_list = reversed(chat.get("chat_list"))

    count = get_chat(chat_info.get("to_user"),chat_info.get("from_user"))
    print(count)
    if not count:
        # 没有收到消息
        res = text2audio("没有新的消息")
        return jsonify([{"from_user":chat_info.get("from_user"),"message":res}])

    new_chat_list = []
    for chat in chat_list:
        if chat.get("from_user") == chat_info.get("to_user"):
            continue
        new_chat_list.append(chat)
        if len(new_chat_list) == count:
            break

    # chat_last = chat_list[-1]
    # 1.如果很多条未读？
    # 2.直接回复消息，收取自己的消息
    print(new_chat_list)
    return jsonify(new_chat_list)
