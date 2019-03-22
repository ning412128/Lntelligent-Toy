from flask import Blueprint, jsonify
from setting import MONGO_DB

content = Blueprint("content", __name__)


@content.route("/get_content_list", methods=["POST"])
def get_content_list():
    res = list(MONGO_DB.content.find({}))
    print(res)
    for index, item in enumerate(res):
        res[index]["_id"] = str(item.get("_id"))

    return jsonify(res)
