from flask import Flask,render_template,request,redirect, url_for, jsonify
import random

app = Flask(__name__)

games = {}
words = []
count = 25
rbx = [9,8,1]

@app.route("/captain")
def captain():
    game = games.get(request.args.get("id"))
    if game == None:
        idx = initial_game()
        return redirect(url_for(".captain",id=idx))
    return render_template("codenames.html")

@app.route("/member")
def member():
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


@app.route("/allgame")
def allgame():
    return jsonify({"idx":games.keys()})

def initial_game():
    upper = 100000000
    idx = random.randint(1,upper)
    while (games.has_key(idx)):
        idx = random.randint(0,upper)
    game = {}
    game["words"] = gen_words()
    game["opened"] = [0]*25
    game["dist"] = gen_dist()
    games[str(idx)] = game
    return idx

def gen_dist():
    dist = ['r']*rbx[0] + ['b']*rbx[1] + ['x']*rbx[2] + ['p']*(count-sum(rbx))
    random.shuffle(dist)
    return dist

def gen_words():
    return random.sample(words,count)

def load_words(fname):
    for line in open(fname,'r'):
        words.append(line.rstrip())

if __name__ == "__main__":
    app.debug = True
    load_words('codenames.words')
    app.run(port = 8765)
