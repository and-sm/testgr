var socket = new WebSocket(
    'ws://' + window.location.host +  '/ws/running_jobs/');
    socket.onmessage = function(e) {
    var data = JSON.parse(e.data);
    var message = data['message'];
    var Table = document.getElementById("running_jobs");
    let env = "";
    let status = "";
    if(message == null){
        Table.innerHTML = "<tr><td collspan='3'>No job is running</td></tr>"
    }
    else {
        Table.innerHTML = "";
        message.forEach(function (obj) {
            status = "<a href=job/" + obj.uuid + " class=\"ui blue basic label\">Running</a>";
            if(obj.env == null){
                env = "not set"
            }
            else{
                env = obj.env
            }
            var row = Table.insertRow(0);
            var cell1 = row.insertCell(0);
            cell1.innerHTML = "<a href=job/" + obj.uuid + ">" + obj.start_time + "</a>";
            var cell2 = row.insertCell(1);
            cell2.innerHTML = "<a href=job/" + obj.uuid + ">" + env + "</a>";
            var cell3 = row.insertCell(2);
            cell3.innerHTML = status;
        })
    }
};
socket.onclose = function(e) {
    console.error('Socket closed unexpectedly');
};
