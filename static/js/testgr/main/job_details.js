var uuid = document.getElementById("job_details").getAttribute("data-job-uuid");
var socket = new WebSocket(
    'ws://' + window.location.host +  '/ws/job_details/' + uuid);
socket.onmessage = function(e) {

    var data = JSON.parse(e.data);
    var message = data['message'];

    let status = document.getElementById("job_status");
    let finished_message = document.getElementById("job_finished_message");
    let detach_button_div = document.getElementById("force_stop_job_div");

    if(message['status'] === "1"){
        status.innerHTML = "Status: <span class=\"ui blue small header\">In Progress</span>";
    }
    else if(message['status'] === "2"){
        status.innerHTML = "Status: <span class=\"ui green small header\">Passed</span>";
        finished_message.removeAttribute("style");
        detach_button_div.innerHTML = '';
        detach_button_div.setAttribute("style", "display: None");
    }
    else if(message['status'] === "3"){
        status.innerHTML = "Status: <span class=\"ui red small header\">Failed</span>";
        finished_message.removeAttribute("style");
        detach_button_div.innerHTML = '';
        detach_button_div.setAttribute("style", "display: None");
    }
    else if(message['status'] === "4"){
        status.innerHTML = "Status: <span class=\"ui yellow small header\">Stopped</span>";
        finished_message.removeAttribute("style");
        detach_button_div.innerHTML = '';
        detach_button_div.setAttribute("style", "display: None");
    }

    let job_time_stop = document.getElementById("job_stop_timestamp");
    if(message['stop_time'] != null){
        job_time_stop.innerText = message['stop_time']
    }
    else{
        job_time_stop.innerText = "Pending..."
    }

    let job_time_taken = document.getElementById("job_time_taken");
    if(message['time_taken'] != null){
        job_time_taken.innerText = message['time_taken']
    }
    else{
        job_time_taken.innerText = "Pending..."
    }

};
socket.onclose = function(e) {
    console.error('Socket closed unexpectedly');
};
