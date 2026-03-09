
from flask import Flask, render_template, request, redirect, session, jsonify
from flask_socketio import SocketIO, emit, join_room
import sqlite3, os

app=Flask(__name__)
app.secret_key="secret"
socketio=SocketIO(app)

UPLOAD_FOLDER="static/uploads"
os.makedirs(UPLOAD_FOLDER,exist_ok=True)

DB="chat.db"

def init_db():
    conn=sqlite3.connect(DB)
    c=conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS messages(user TEXT,room TEXT,msg TEXT)")
    conn.commit()
    conn.close()

init_db()

@app.route("/",methods=["GET","POST"])
def login():
    if request.method=="POST":
        session["user"]=request.form["user"]
        return redirect("/chat")
    return render_template("login.html")

@app.route("/chat")
def chat():
    if "user" not in session:
        return redirect("/")
    return render_template("chat.html",user=session["user"])

@app.route("/room/<room>")
def room(room):
    conn=sqlite3.connect(DB)
    c=conn.cursor()
    c.execute("SELECT user,msg FROM messages WHERE room=?",(room,))
    history=c.fetchall()
    conn.close()
    return render_template("room.html",room=room,user=session["user"],history=history)

@app.route("/upload",methods=["POST"])
def upload():
    file=request.files["file"]
    path=os.path.join(UPLOAD_FOLDER,file.filename)
    file.save(path)
    return jsonify({"path":path,"name":file.filename})

@socketio.on("join")
def join(data):
    join_room(data["room"])

@socketio.on("message")
def message(data):
    conn=sqlite3.connect(DB)
    c=conn.cursor()
    c.execute("INSERT INTO messages VALUES (?,?,?)",(data["user"],data["room"],data["msg"]))
    conn.commit()
    conn.close()
    emit("message",data,room=data["room"],include_self=False)

@socketio.on("typing")
def typing(data):
    emit("typing",data,room=data["room"],include_self=False)

if __name__=="__main__":
    socketio.run(app,debug=True)
