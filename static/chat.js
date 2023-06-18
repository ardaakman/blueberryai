// on wndow load
window.onload = function() {
    // get call id from url
    // show grayMessage
    grayMessage("Chat started with ..");
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

    // Access the properties of the JavaScript object
    var message = jsonData.message;
    var sender = jsonData.sender;

    console.log("Message from server ", event.data);
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
        } else {
            show_toast("Error Occured");
        }
    }
    );
}

function sendMessage() {
    const call_id = document.getElementById("call_id").value;
    const message = document.getElementById("message").value;
    // fetch post
    fetch("/send_message", {
        method: "POST",
        body: JSON.stringify({
            call_id: call_id,
            message: message
        })
    })
    .then(response => response.json())
    .then(result => {
        console.log(result)
        if (result.status == 'success') {
            console.log("Message sent");
            var chat = document.getElementById("chat");
            var chatBubble = document.createElement("div");
            chatBubble.classList.add("chat-bubble");
            chatBubble.classList.add("chat-caller");
            var chatText = document.createElement("div");
            chatText.classList.add("chat-text");
            var chatTextP = document.createElement("p");
            chatTextP.innerText = message;
            chatText.appendChild(chatTextP);
            chatBubble.appendChild(chatText);
            chat.appendChild(chatBubble);
            chat.scrollTop = chat.scrollHeight;
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