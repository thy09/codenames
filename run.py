#! encoding=utf-8
from flask import Flask,render_template,request,redirect, url_for, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
import random

app = Flask(__name__)
app.config["SECRET_KEY"] = 'neverguess'
sockio = SocketIO(app)

def create_app():
    return app

games = {}
words = []
words = set()
count = 25
rbx = [9,8,1]

def add_sentence(game, sentence):
    game["discussion"].append(sentence)
    emit("discussion",{"data":sentence},room = str(game["id"]))

@sockio.on('connect',namespace = "/sock")
def connect():
    pass

@sockio.on('update',namespace = "/sock")
def update_msg(msg):
    game = games.get(str(msg["data"].get("id")))
    sentence = msg["data"].get("say")
    if not sentence or not game:
        return
    add_sentence(game, sentence)

@sockio.on('pass', namespace = '/sock')
def pass_round(msg):
    game = games.get(str(msg["data"].get("id")))
    group = msg["data"].get("group")
    if group != game["status"]:
        return
    add_sentence(game, "回合%d:主动转换，队伍%d开始提示"%(game["round"], group))
    if game["can_pass"] == False:
        game["round"] += 1
        game["can_pass"] = True
    game["status"] = 3-group
    room = str(game["id"])
    emit("pass",{"status":game["status"]}, room = room)


@sockio.on('open', namespace='/sock')
def open_msg(msg):
    game = games.get(str(msg["data"].get("id")))
    idx = msg["data"].get("idx")
    if not game or idx<0 or idx>count-1:
        return
    group = msg["data"].get("group")
    if not game["opened"][idx] in [group, 3]:
        game["opened"][idx] += group
    group_dist = {1:"b", 2:"r"}
    ori_round = game["round"]
    correct = False
    if game["dist"][idx] == 'g' or game["dist"][idx] == group_dist[group]:
        game["opened"][idx] = 3
        result = "正确"
        game["status"] = group
        game["to_guess"] -= 1
        game["can_pass"] = False
        correct = True
    else:
        result = "错误"
        game["round"] += 1
        game["status"] = 3 - group
        game["can_pass"] = True
        game["error"] += 1
    death_dist = {1:"z", 2:"y"}
    if (game["to_guess"] == 0):
        game["status"] = "win"
    if game["dist"][idx] == 'x' or game["dist"][idx] == death_dist[group]:
        game["status"] = "death"
    roomid = str(game["id"])
    emit("open",{"data":{"idx":idx, "val":game["opened"][idx], "status":game["status"]}},room = roomid)
    sentence = "回合%d: 队伍%d猜了 %s" % (ori_round, group, game["words"][idx])
    if correct:
        sentence = "%s 正确" % sentence
    else:
        sentence = "%s 第%d个错误" % (sentence, game["error"])
    add_sentence(game, sentence)
    if game["status"] == "win":
        add_sentence(game, "全部猜对，游戏胜利")
    elif game["status"] == "death":
        add_sentence(game, "猜到死亡词汇，游戏结束")
    elif game["status"] != group:
        add_sentence(game, "队伍转换，队伍%d开始提示"%(group))

@sockio.on("join",namespace="/sock")
def join(msg):
    roomid = str(msg["id"])
    join_room(roomid)


@app.route("/captain")
def captain():
    game = games.get(request.args.get("id"))
    if game == None:
        idx = initial_game(request.args.get("start"), request.args.get("is_pic"))
        return redirect(url_for(".member",id=idx))
    return render_template("codenames.html")

@app.route("/member")
def member():
    game = games.get(request.args.get("id"))
    if game == None:
        idx = initial_game(request.args.get("start"))
        return redirect(url_for(".member",id=idx))
    return render_template("codenames.html")

@app.route("/status")
def status():
    game = games.get(request.args.get("id"))
    if game == None:
        return jsonify({"status":"INVALID_ID"})
    return jsonify({"status":"success","game":game})

@app.route("/open",methods = ["POST"])
def openpos():
    game = games.get(request.args.get("id"))
    idx = int(request.args.get("idx"))
    game["opened"][idx] = 1
    return jsonify({"status":"success"})

@app.route("/submit",methods = ["POST"])
def submit_sentence():
    game = games.get(request.args.get("id"))
    sentence = request.form["say"]
    game["discussion"].append(sentence)
    return jsonify({"status":"success"})


@app.route("/update_info")
def update_info():
    game = games.get(request.args.get("id"))
    if game == None:
        return jsonify({"status":"INVALID_ID"})
    res = {"opened":game["opened"],
            "discussion":game.get("discussion",[])[-10:]}
    return jsonify({"status":"success","game":res})

@app.route("/allgame")
def allgame():
    return jsonify({"idx":games.keys()})

def initial_game(start, is_pic = False):
    upper = 100000000
    idx = random.randint(1,upper)
    while (games.has_key(idx)):
        idx = random.randint(0,upper)
    game = {}
    game['status'] = None
    game["round"] = 1
    game["can_pass"] = True
    game["error"] = 0
    game["to_guess"] = duet[0]+duet[1]+duet[2]
    game["words"] = gen_words(is_pic)
    game["opened"] = [0]*25
    game["dist"] = gen_dist_duet()
    game["discussion"] = []
    game["id"] = idx
    games[str(idx)] = game
    return idx

duet = [6,6,3,3]
def gen_dist_duet():
    xx = random.randint(0, duet[3])
    dist = ['r'] * duet[0] + ['b'] * duet[1] + ['g'] * duet[2] + \
    ['x'] * xx + ['y'] * (duet[3]-xx) + ['z']*(duet[3]-xx) + \
    ['p'] * (count - sum(duet) - duet[3] + xx)
    random.shuffle(dist)
    return dist

def gen_dist(start):
    dist = ['r']*rbx[0] + ['b']*rbx[1] + ['x']*rbx[2] + ['p']*(count-sum(rbx))
    if start == 'b':
        dist[0] = 'b'
    random.shuffle(dist)
    return dist

def gen_words(is_pic = False):
    if is_pic:
        return [u"图片"] * count
    return random.sample(words,count)

def load_words(fname):
    for line in open(fname,'r'):
        if line.find("##")>-1:
            continue
        word = line.rstrip()
        words.add(line.rstrip())

load_words('codenames.words')
load_words("codenames.words.2nd")
if __name__ == "__main__":
    app_ = create_app()
    app_.debug = True
    #sockio.run(app)
    sockio.run(app,port=24442)
   # app_.run(host='0.0.0.0',port = 23332)
