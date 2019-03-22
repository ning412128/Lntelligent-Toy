import requests,os,hashlib,time
from setting import QRCODE,LT_URL,MONGO_DB
from uuid import uuid4


def create_QR(num):
    for i in range(num):
        code = f"{uuid4()}{time.time()}{uuid4()}"
        qr_info = hashlib.md5(code.encode("utf8")).hexdigest()
        res = requests.get(LT_URL%(qr_info))
        qr_path = os.path.join(QRCODE,f"{qr_info}.jpg")
        with open(qr_path,"wb") as f:
            f.write(res.content)

        time.sleep(0.1)

        MONGO_DB.devices.insert_one({"device_key":qr_info})


create_QR(5)
