var socket = new WebSocket(
    'ws://' + window.location.host +  '/ws/running_jobs/');
    socket.onmessage = function(e) {
    var data = JSON.parse(e.data);
    var message = data['message'];
    var Table = document.getElementById("running_jobs");
    let env = "";
    let tests_passed = "";
    let tests_failed = "";
    let tests_aborted = "";
    let tests_skipped = "";
    let tests_not_started = "";
    if(message == null){
        Table.innerHTML = "<tr><td collspan='3'>No job is running</td></tr>"
    }
    else {
        Table.innerHTML = "";
        message.forEach(function (obj) {
            if(obj.env == null){env = "None"}else{env = obj.env}
            if(obj.tests_passed == null){tests_passed = "<a href=job/" + obj.uuid +
                " class=\"ui green basic label\">0</a>"}
            else{tests_passed = "<a href=job/" + obj.uuid +
                " class=\"ui green basic label\">" + obj.tests_passed + "</a>"}
            if(obj.tests_failed == null){tests_failed = ""}else{tests_failed = "<a href=job/" + obj.uuid +
                " class=\"ui red basic label\">" + obj.tests_failed + "</a>"}
            if(obj.tests_aborted == null){tests_aborted = ""}else{tests_aborted = "<a href=job/" + obj.uuid +
                " class=\"ui darkred basic label\">" + obj.tests_aborted + "</a>"}
            if(obj.tests_skipped == null){tests_skipped = ""}else{tests_skipped = "<a href=job/" + obj.uuid +
                " class=\"ui yellow basic label\">" + obj.tests_skipped + "</a>"}
            if(obj.tests_not_started == null){tests_not_started = ""}else{tests_not_started = "<a href=job/" + obj.uuid +
                " class=\"ui grey basic label\">" + obj.tests_not_started + "</a>"}
            var row = Table.insertRow(0);
            var cell1 = row.insertCell(0);
            cell1.innerHTML = "<a href=job/" + obj.uuid + ">" + obj.start_time + "</a>";
            var cell2 = row.insertCell(1);
            cell2.innerHTML = "<a href=job/" + obj.uuid + ">" + env + "</a>";
            var cell3 = row.insertCell(2);
            cell3.innerHTML = tests_passed + tests_failed + tests_aborted + tests_skipped + tests_not_started;
        })
    }
};
socket.onclose = function(e) {
    console.error('Socket closed unexpectedly');
};
