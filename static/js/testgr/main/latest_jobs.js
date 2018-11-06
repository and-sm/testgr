var socket = new WebSocket(
    'ws://' + window.location.host +  '/ws/latest_jobs/');
    socket.onmessage = function(e) {
    var data = JSON.parse(e.data);
    var message = data['message'];
    var Table = document.getElementById("latest_jobs");
    let env = "";
    let status = "";
    if(message == null){
        Table.innerHTML = ""
    }
    else {
        Table.innerHTML = "";
        message.forEach(function (obj) {
            if(obj.status === 2){
                status = "<a href=job/" + obj.uuid + " class=\"ui ui green basic label\">Passed</a>";
            }
            else if(obj.status === 3){
                status = "<a href=job/" + obj.uuid + " class=\"ui ui red basic label\">Failed</a>";
            }
            else if(obj.status === 4){
                status = "<a href=job/" + obj.uuid + " class=\"ui ui yellow basic label\">Stopped</a>";
            }
            if(obj.env == null){
                env = "not set"
            }
            else{
                env = obj.env
            }
            var row = Table.insertRow(0);
            var cell1 = row.insertCell(0);
            cell1.innerHTML = "<a href=job/" + obj.uuid + ">" + obj.stop_time + "</a>";
            var cell2 = row.insertCell(1);
            cell2.innerHTML = "<a href=job/" + obj.uuid + ">" + obj.time_taken + "</a>";
            var cell3 = row.insertCell(2);
            cell3.innerHTML = "<a href=job/" + obj.uuid + ">" + env + "</a>";
            var cell4 = row.insertCell(3);
            cell4.innerHTML = status;
        })
    }
};
socket.onclose = function(e) {
    console.error('Socket closed unexpectedly');
};
