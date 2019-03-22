# 喜马拉雅
import requests,os,time

from uuid import uuid4
from setting import MUSIC,COVER,XMLY_URL,XMLY_HEADER,MONGO_DB

res = requests.get(XMLY_URL,headers = XMLY_HEADER)
res_json = res.json()
data_dict = res_json.get("data")
data_list = data_dict.get("tracksAudioPlay")

content_list = []

for context in data_list:
    file_name = uuid4()
    music = context.get("src")
    cover = "http:" + context.get("trackCoverPath")
    title = context.get("trackName")

    music_content = requests.get(music)
    music_path = os.path.join(MUSIC,f"{file_name}.mp3")
    with open(music_path,"wb") as f:
        f.write(music_content.content)

    cover_content = requests.get(cover)
    cover_path = os.path.join(COVER, f"{file_name}.jpg")
    with open(cover_path,"wb") as f:
        f.write(cover_content.content)

    # 有两个名字mp3和jpg，搞出来
    music_info = {
        "music": f"{file_name}.mp3",
        "cover": f"{file_name}.jpg",
        "title": title
    }

    content_list.append(music_info)
    time.sleep(0.5)

MONGO_DB.content.insert_many(content_list)



