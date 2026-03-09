
var socket
var user
var room

function init(u,r){
user=u
room=r

socket=io()

socket.emit("join",{room:room})

socket.on("message",function(data){

var div=document.createElement("div")
div.className="other"
div.innerHTML=data.user+": "+data.msg

document.getElementById("messages").appendChild(div)

})

socket.on("typing",function(data){

document.getElementById("typing").innerHTML=data.user

setTimeout(()=>{
document.getElementById("typing").innerHTML=""
},1000)

})

document.getElementById("msg").addEventListener("keypress",function(e){
if(e.key==="Enter") send()
})

}

function send(){

var msg=document.getElementById("msg").value

if(msg.trim()=="") return

var div=document.createElement("div")
div.className="me"
div.innerHTML=msg+" ✓✓"

document.getElementById("messages").appendChild(div)

socket.emit("message",{user:user,msg:msg,room:room})

document.getElementById("msg").value=""

}

function typing(){

socket.emit("typing",{user:user+" typing...",room:room})

}

function sendFile(){

var file=document.getElementById("file").files[0]

var form=new FormData()
form.append("file",file)

fetch("/upload",{
method:"POST",
body:form
})
.then(res=>res.json())
.then(data=>{

var name=data.name
var path=data.path
var msg=""

if(name.endsWith(".jpg")||name.endsWith(".png")){
msg="<img src='"+path+"' width=200>"
}

else if(name.endsWith(".mp4")){
msg="<video src='"+path+"' width=250 controls></video>"
}

else if(name.endsWith(".pdf")||name.endsWith(".doc")||name.endsWith(".docx")){
msg="<a href='"+path+"' target='_blank'>📄 "+name+"</a>"
}

socket.emit("message",{user:user,msg:msg,room:room})

})

}
