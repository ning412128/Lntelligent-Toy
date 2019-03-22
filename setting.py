# 目录配置

MUSIC = "Music"
COVER = "Cover"
QRCODE = "QRcode"
CHATS = "Chats"


# 采集配置
XMLY_URL = "https://www.ximalaya.com/revision/play/album?albumId=424529&pageNum=1"
XMLY_HEADER = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"}


# 数据库配置
from pymongo import MongoClient

db_client = MongoClient("127.0.0.1",27017)
MONGO_DB = db_client["IntelligentToy"]

from redis import Redis
RDB = Redis(db=10)



# App数据传输协议
RET = {
    "code":0,
    "msg":"",
    "data":{}
}

# 二维码设置
LT_URL = "http://qr.topscan.com/api.php?text=%s"

# 百度Ai配置
from aip import AipSpeech
APP_ID = '15674271'
API_KEY = 'XkV3bWa9stbsFfXvHDqzWIR2'
SECRET_KEY = 'nIMmNTRSx2u76azSNfz9TTEclnDGmbgh'

BAIDU_YUYIN = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
YUYIN_CONFIG = {
        'vol': 5,
        "spd": 4,
        "pit": 8,
        "per": 4
    }
