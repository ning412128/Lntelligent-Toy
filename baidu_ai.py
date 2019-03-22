from setting import BAIDU_YUYIN as client ,YUYIN_CONFIG,CHATS,MONGO_DB
from uuid import uuid4
from bson import ObjectId
import os

def text2audio(answer):
    # 语音合成
    result = client.synthesis(answer, 'zh', 1, YUYIN_CONFIG)

    # 识别正确返回语音二进制 错误则返回dict 参照下面错误码
    res_file_name = f"{uuid4()}.mp3"
    file_path = os.path.join(CHATS,res_file_name)

    if not isinstance(result, dict):
        with open(file_path, 'wb') as f:
            f.write(result)
        return res_file_name

def audio2text(filePath):
    # 开始语音识别
    # 读取文件
    os.system(f"ffmpeg -y -i {filePath} -acodec pcm_s16le -f s16le -ac 1 -ar 16000 {filePath}.pcm")
    with open(f"{filePath}.pcm", 'rb') as fp:
        res = client.asr(fp.read(), 'pcm', 16000, {
            'dev_pid': 1537,
        })
    if res.get("result"):
        return res.get("result")[0]
    else:
        return None


def my_nlp_lowB(ai_msg,toy_id):
    # 自然语言处理
    if "发消息" in ai_msg: # ai_msg = "我要给男神发消息"
        # 3.文字找到联系人 NLP 自然语言处理
        toy_info = MONGO_DB.toys.find_one({"_id":ObjectId(toy_id)})
        print(toy_info)
        for friend in toy_info.get("friend_list"):
            if friend.get("friend_remark") in ai_msg or friend.get("friend_nick") in ai_msg:
                filename = text2audio(f"可以按消息建给{friend.get('friend_remark')}发消息了")
                friend["filename"] = filename
                return friend


    if "我想听"in ai_msg or "我要听" in ai_msg or"播放"in ai_msg or"来一首"in ai_msg:
        content_list = MONGO_DB.content.find({})
        for content in content_list :
            if content.get("title") in ai_msg:
                return {"music":content.get("music")}
