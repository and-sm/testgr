var uuid = document.getElementById("job_details").getAttribute("data-job-uuid");
var chatSocket = new WebSocket(
    'ws://' + window.location.host +  '/ws/job_details/' + uuid);
chatSocket.onmessage = function(e) {

    var data = JSON.parse(e.data);
    var message = data['message'];

    let status = document.getElementById("job_status");

    if(message['status'] === "1"){
        status.innerHTML = "Status: <span class=\"ui blue small header\">In Progress</span>";
    }
    else if(message['status'] === "2"){
        status.innerHTML = "Status: <span class=\"ui green small header\">Passed</span>";
    }
    else if(message['status'] === "3"){
        status.innerHTML = "Status: <span class=\"ui red small header\">Failed</span>";
    }
    else if(message['status'] === "4"){
        status.innerHTML = "Status: <span class=\"ui red small header\">Stopped</span>";
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
chatSocket.onclose = function(e) {
    console.error('Socket closed unexpectedly');
};
