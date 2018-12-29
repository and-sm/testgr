var uuid = document.getElementById("job_tests_details").getAttribute("data-job-uuid");
var socket = new WebSocket(
    'ws://' + window.location.host +  '/ws/job_tests_details/' + uuid);
socket.onmessage = function(e) {

    var data = JSON.parse(e.data);
    var message = data['message'];
    let TestsTable = document.getElementById("tests_list");

    let passed = document.getElementById("job_tests_passed");
    let failed = document.getElementById("job_tests_failed");
    let aborted = document.getElementById("job_tests_aborted");
    let skipped = document.getElementById("job_tests_skipped");
    let not_started = document.getElementById("job_tests_not_started");


    if(message['passed']) {
        passed.innerHTML = "Passed: " + message['passed'];
    }

    if(message['failed'] > 0 ) {
        failed.innerHTML = "Failed: <span class=\"test_failed\">" + message['failed'] + "</span>";
    }
    else{
        failed.innerHTML = "Failed: " + message['failed'] + "</span>";
    }

    if(message['aborted'] > 0 ) {
        aborted.innerHTML = "Aborted: <span class=\"test_failed\">" + message['aborted'] + "</span>";
    }
    else{
        aborted.innerHTML = "Aborted: " + message['aborted'] + "</span>";
    }

    if(message['skipped'] > 0 ) {
        skipped.innerHTML = "Skipped: <span class=\"test_skipped\">" + message['skipped'] + "</span>";
    }
    else{
        skipped.innerHTML = "Skipped: " + message['skipped'] + "</span>";
    }

    if(message['not_started']) {
        not_started.innerHTML = "Not Started: " + message['not_started'];
    }


    if(message == null){
        TestsTable.innerHTML = ""
    }
    else {
        TestsTable.innerHTML = "";
        message['tests'].forEach(function (obj) {


            if(obj.start_time == null){
                obj.start_time = "Pending..."
            }

            if(obj.time_taken == null){
                obj.time_taken = "Pending..."
            }

            if(obj.time_taken_eta == null){
                obj.time_taken_eta = "Pending..."
            }
            else{
                obj.time_taken_eta = "ETA: " + obj.time_taken_eta
            }

            let tr_class = "";

            if(obj.status === 1){
                status = "<a href=\"/test/" + obj.uuid + "\" class=\"ui ui gray basic label\">Not Started</a>";
            }
            else if(obj.status === 2){
                status = "<a href=\"/test/" + obj.uuid + "\" class=\"ui ui blue basic label\">In Progress</a>";
            }
            else if(obj.status === 3){
                status = "<a href=\"/test/" + obj.uuid + "\" class=\"ui ui green basic label\">Passed</a>";
                tr_class = "ui positive";
            }
            else if(obj.status === 4){
                status = "<a href=\"/test/" + obj.uuid + "\" class=\"ui ui red basic label\">Failed</a>";
                tr_class = "ui negative";
            }
            else if(obj.status === 5){
                status = "<a href=\"/test/" + obj.uuid + "\" class=\"ui ui yellow basic label\">Skipped</a>";
                tr_class = "ui warning";
            }
            else if(obj.status === 6){
                status = "<a href=\"/test/" + obj.uuid + "\" class=\"ui ui red basic label\">Aborted</a>";
                tr_class = "ui negative";
            }

            var row = TestsTable.insertRow(0);
            row.className = tr_class;
            var cell1 = row.insertCell(0);
            cell1.innerHTML = "<a href=\"/test/" + obj.uuid + "\">&nbsp;&nbsp;" + obj.short_identity + "</a>";
            var cell2 = row.insertCell(1);
            cell2.innerHTML = "<a href=\"/test/" + obj.uuid + "\">" + obj.start_time + "</a>";
            var cell3 = row.insertCell(2);
            if(obj.status === 2){
                cell3.innerHTML = "<a href=\"/test/" + obj.uuid + "\">" + obj.time_taken_eta + "</a>";
            }
            else{
                cell3.innerHTML = "<a href=\"/test/" + obj.uuid + "\">" + obj.time_taken + "</a>";
            }
            var cell4 = row.insertCell(3);
            cell4.innerHTML = "<a href=\"/test/" + obj.uuid + "\">" + status + "</a>";
        })
    }
};
socket.onclose = function(e) {
    console.error('Socket closed unexpectedly');
};
