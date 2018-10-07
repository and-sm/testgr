var socket = new WebSocket(
    'ws://' + window.location.host +  '/ws/running_jobs_count/');
    socket.onmessage = function(e) {
    var data = JSON.parse(e.data);
    var message = data['message'];
    element = document.querySelector('#running_jobs_count');
    if(message == null){
        element.className = "";
        element.innerHTML = "";
    }
    else {
        element.className = "item";
        element.innerHTML = "<span>Currently running jobs: <strong>"
            + message + "</strong></span>";
    }
};
socket.onclose = function(e) {
    console.error('Socket closed unexpectedly');
};
