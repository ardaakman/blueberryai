// on wndow load
window.onload = function() {
    // get call id from url
    // show grayMessage
    const recipient = document.getElementById("recipient").innerText;
    grayMessage("Chat started with " + recipient);
}

socket = new WebSocket(`ws://localhost:8201/websocket`);
socket.addEventListener("open", (event) => {
  console.log("WebSocket connection established");
});

socket.addEventListener("close", (event) => {
    console.log("WebSocket connection closed");
    // Perform cleanup or necessary actions here
});

socket.addEventListener("message", (event) => {

    var jsonData = JSON.parse(event.data);
    var jsonData = jsonData.replace(/\\/g, "");
    var jsonData = JSON.parse(jsonData);
    // Access the properties of the JavaScript object
    var message = jsonData.message;
    var sender = jsonData.sender;

    console.log("Message from server ", jsonData);

    // print  message
    console.log("Message: ", message);
    
    var chat = document.getElementById("chat");
    var chatBubble = document.createElement("div");
    chatBubble.classList.add("chat-bubble");
    if (sender == "caller") {
        chatBubble.classList.add("chat-caller");
    } else {
        chatBubble.classList.add("chat-callee");
    }
    var chatText = document.createElement("div");
    chatText.classList.add("chat-text");
    var chatTextP = document.createElement("p");
    chatTextP.innerText = message;
    chatText.appendChild(chatTextP);
    chatBubble.appendChild(chatText);
    chat.appendChild(chatBubble);
    chat.scrollTop = chat.scrollHeight;
});

function grayMessage(message) {
    var chat = document.getElementById("chat");
    var chatBubble = document.createElement("div");
    chatBubble.classList.add("chat-bubble-large");
    var chatText = document.createElement("div");
    chatText.classList.add("chat-text");
    var chatTextP = document.createElement("p");
    chatTextP.innerText = message;
    chatText.appendChild(chatTextP);
    chatBubble.appendChild(chatText);
    chat.appendChild(chatBubble);
    chat.scrollTop = chat.scrollHeight;
}


function endCall() {
    // make fetch post request to /end_call with body call_id
    const call_id = document.getElementById("call_id").value;
    console.log("Call id: ", call_id)
    fetch("/end_call", {
        method: "POST",
        body: JSON.stringify({
            call_id: call_id
        })
    })
    .then(response => response.json())
    .then(result => {
        console.log(result)
        if (result.status == 'success') {
            console.log("Call ended");
            show_toast("Call ended");
            grayMessage("Call ended");
            // set button to disabled
            document.getElementById("end-call").disabled = true;

        } else {
            show_toast("Error Occured");
        }
    }
    );
}

function saveInfo() {
    const call_id = document.getElementById("call_id").value;
    // const message = document.getElementById("message").value;
    // fetch post
    console.log(call_id);
    // create a list of all question-answer values 
    var info = [];
    var questions = document.getElementsByClassName("question-answer");
    // for each question get id and value
    for (var i = 0; i < questions.length; i++) {
        var question = questions[i];
        var id = question.id;
        var value = document.getElementById(id).value;
        var prev = document.getElementById(id + '-prev').value;
        info.push({
            id: id,
            value: value,
            prev: prev
        });
    }
    fetch("/update_personal_info", {
        method: "POST",
        body: JSON.stringify({
            call_id: call_id,
            info: info
        })
    })
    .then(response => response.json())
    .then(result => {
        console.log(result)
        if (result.status == 'success') {
            console.log("Info Updated");
            show_toast("Info Updated");
            // var chat = document.getElementById("chat");
            // var chatBubble = document.createElement("div");
            // chatBubble.classList.add("chat-bubble");
            // chatBubble.classList.add("chat-caller");
            // var chatText = document.createElement("div");
            // chatText.classList.add("chat-text");
            // var chatTextP = document.createElement("p");
            // chatTextP.innerText = message;
            // chatText.appendChild(chatTextP);
            // chatBubble.appendChild(chatText);
            // chat.appendChild(chatBubble);
            // chat.scrollTop = chat.scrollHeight;
        } else {
            show_toast("Error Occured");
        }
    }
    );
}

var auto = false;
function setAuto(call_id) {
    auto = !auto;
    if (auto) {
        show_toast("Auto mode on");
    } else {
        show_toast("Auto mode off");
    }
    console.log("Auto: ", auto);
    
}


function show_toast(message) {
    var toast = document.getElementById('toast');
    toast = bootstrap.Toast.getOrCreateInstance(toast)
    const toastBody = document.getElementById('toast-message');
    toastBody.innerText = message;
    toast.show()
}