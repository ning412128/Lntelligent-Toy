from flask import Flask,render_template
from serv import content,get_set_anything,user,devices,friend,chats
app = Flask(__name__)

app.register_blueprint(content.content)
app.register_blueprint(get_set_anything.gsa)
app.register_blueprint(user.user)
app.register_blueprint(devices.devices)
app.register_blueprint(friend.friend)
app.register_blueprint(chats.chats)

# 玩具开机页面
@app.route("/")
def toy_on():
    return render_template("WebToy.html")

if __name__ == '__main__':
    app.run("0.0.0.0",9527,debug=True)