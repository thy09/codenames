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
count = 25
rbx = [9,8,1]

@sockio.on('connect',namespace = "/sock")
def connect():
    pass

@sockio.on('update',namespace = "/sock")
def update_msg(msg):
    print msg
    game = games.get(str(msg["data"].get("id")))
    sentence = msg["data"].get("say")
    print msg,sentence,game
    if not sentence or not game:
        return
    game["discussion"].append(sentence)
    emit("discussion",{"data":sentence},room = str(game["id"]))

@sockio.on('open', namespace='/sock')
def open_msg(msg):
    game = games.get(str(msg["data"].get("id")))
    idx = msg["data"].get("idx")
    if not game or idx<0 or idx>count-1:
        return
    game["opened"][idx] = 1
    roomid = str(game["id"])
    print rooms(),roomid
    emit("open",{"data":idx},room = roomid)

@sockio.on("join",namespace="/sock")
def join(msg):
    print rooms()
    roomid = str(msg["id"])
    print roomid
    join_room(roomid)
    print "joined"


@app.route("/captain")
def captain():
    game = games.get(request.args.get("id"))
    if game == None:
        idx = initial_game(request.args.get("start"))
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

def initial_game(start):
    upper = 100000000
    idx = random.randint(1,upper)
    while (games.has_key(idx)):
        idx = random.randint(0,upper)
    game = {}
    if start == 'r':
        game["start"] = 'r'
    else:
        game["start"] = 'b'
    game['status'] = game['start']
    game["words"] = gen_words()
    game["opened"] = [0]*25
    game["dist"] = gen_dist(game["start"])
    game["discussion"] = []
    game["id"] = idx
    games[str(idx)] = game
    return idx

def gen_dist(start):
    dist = ['r']*rbx[0] + ['b']*rbx[1] + ['x']*rbx[2] + ['p']*(count-sum(rbx))
    if start == 'b':
        dist[0] = 'b'
    random.shuffle(dist)
    return dist

def gen_words():
    return random.sample(words,count)

def load_words(fname):
    for line in open(fname,'r'):
        if line.find("##")>-1:
            continue
        words.append(line.rstrip())

load_words('codenames.words')
if __name__ == "__main__":
    app_ = create_app()
    app_.debug = True
    #sockio.run(app)
    sockio.run(app,port=23332)
   # app_.run(host='0.0.0.0',port = 23332)
