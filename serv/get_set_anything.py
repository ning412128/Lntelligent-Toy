from flask import Blueprint,jsonify,send_file,request

from ChatRedis import set_chat
from setting import MONGO_DB,COVER,MUSIC,CHATS,RET,QRCODE
import os,time
from bson import ObjectId
from uuid import uuid4
from baidu_ai import text2audio,audio2text,my_nlp_lowB

gsa = Blueprint("gsa",__name__)

@gsa.route("/get_image/<filename>")
def get_image(filename):
    file_path = os.path.join(COVER,filename)

    return send_file(file_path)


@gsa.route("/get_music/<filename>")
def get_music(filename):
    file_path = os.path.join(MUSIC,filename)

    return send_file(file_path)

@gsa.route("/get_chat/<filename>")
def get_chat(filename):
    file_path = os.path.join(CHATS,filename)

    return send_file(file_path)

@gsa.route("/get_qr/<filename>")
def get_qr(filename):
    file_path = os.path.join(QRCODE,filename)

    return send_file(file_path)


@gsa.route("/upload_reco",methods=["POST"])
def upload_reco():
    chat_info = request.form.to_dict()
    # chat_info = {"chat_id":"123213213","to_user":"123123213","from_user":"123213213212"}
    reco_file = request.files.get("reco")
    file_name = reco_file.filename # 默认录音名字
    reco_file_path = os.path.join(CHATS,file_name)
    reco_file.save(reco_file_path)

    os.system(f"ffmpeg -i {reco_file_path} {reco_file_path}.mp3")
    os.remove(reco_file_path)

    # 存储聊天记录
    chat = {
            "from_user":chat_info.get("from_user"),
            "message":f"{file_name}.mp3",
            "create_time":time.time()
        }
    MONGO_DB.chats.update_one({"_id": ObjectId(chat_info.get("chat_id"))},
                              {"$push":{"chat_list":chat}})


    # 添加to_user未读的from_user消息
    set_chat(chat_info.get("to_user"),chat_info.get("from_user"))

    # # 1.用chatid去查询聊天窗口
    # chat_window = MONGO_DB.chats.find_one({"_id":ObjectId(chat_info.get("chat_id"))})
    # # 2.制造聊天记录
    # chat = {
    #     "from_user":chat_info.get("from_user"),
    #     "message":f"{reco_file_path}.mp3",
    #     "create_time":time.time()
    # }
    # chat_window["chat_list"].append(chat)
    # MONGO_DB.chats.update_one({"_id":ObjectId(chat_info.get("chat_id"))},{"$set":chat_window})

    # 解决消息来源问题
    # from_user app
    # to_user toy
    toy_info = MONGO_DB.toys.find_one({"_id":ObjectId(chat_info.get("to_user"))})
    friend_list = toy_info.get("friend_list")
    xxtx = "No_friend.mp3"
    for friend in friend_list:
        if friend.get("friend_id") == chat_info.get("from_user"):
            remark = friend.get("friend_remark")
            xxtx = text2audio(f"你有来自{remark}的消息")


    RET["code"] = 0
    RET["msg"] = "上传录音"
    RET["data"] = {"filename":xxtx}

    return jsonify(RET)

@gsa.route("/upload_toy",methods=["POST"])
def upload_toy():
    chat_info = request.form.to_dict()
    # chat_info = {"to_user":"123123213","from_user":"123213213212"}
    reco_file = request.files.get("reco")
    file_name = f"{uuid4()}.wav"
    reco_file_path = os.path.join(CHATS,file_name)
    reco_file.save(reco_file_path)

    # 存储聊天记录
    chat = {
            "from_user":chat_info.get("from_user"),
            "message":file_name,
            "create_time":time.time()
        }
    user_list = [chat_info.get("from_user"), chat_info.get("to_user")]
    MONGO_DB.chats.update_one({"user_list":{"$all":user_list}},
                              {"$push":{"chat_list":chat}})

    # 添加to_user未读的from_user消息
    set_chat(chat_info.get("to_user"),chat_info.get("from_user"))

    RET["code"] = 0
    RET["msg"] = "上传录音"
    RET["data"] = {"filename":file_name}

    return jsonify(RET)

@gsa.route("/upload_ai",methods=["POST"])
def upload_ai():
    toy_id = request.form.get("toy_id")
    print(toy_id)
    # 1.保存文件
    reco_file = request.files.get("reco")
    file_name = f"{uuid4()}.wav"
    reco_file_path = os.path.join(CHATS,file_name)
    reco_file.save(reco_file_path)
    # 2.语音转文字
    ai_msg = audio2text(reco_file_path)
    print(ai_msg)
    # 3.文字找到联系人 NLP 自然语言处理
    res = my_nlp_lowB(ai_msg,toy_id)  # res = friend {}

    # 4.与联系人沟通

    return jsonify(res)
