var uuid = document.getElementById("job_tests_details").getAttribute("data-job-uuid");
var socket = new WebSocket(
    'ws://' + window.location.host +  '/ws/job_tests_details/' + uuid);
    socket.onmessage = function(e) {

    var data = JSON.parse(e.data);
    var message = data['message'];
    var test = message['test'];
    var test_uuid = test['uuid'];
    var test_start_time = test['start_time'];
    var test_time_taken = test['time_taken'];
    var test_time_taken_eta = test['time_taken_eta'];
    var test_status = test['status'];

    let passed = document.getElementById("job_tests_passed");
    let failed = document.getElementById("job_tests_failed");
    let aborted = document.getElementById("job_tests_aborted");
    let skipped = document.getElementById("job_tests_skipped");
    let not_started = document.getElementById("job_tests_not_started");

    let data_tr_test = document.querySelector('[data-tr-test="' + test_uuid + '"]');
    let data_td_start_time = document.querySelector('[data-td-start-time="' + test_uuid + '"]');
    let data_td_eta = document.querySelector('[data-td-eta="' + test_uuid + '"]');
    let data_td_status = document.querySelector('[data-td-status="' + test_uuid + '"]');

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


    if(test_start_time == null){
        test_start_time = "Pending..."
    }
    data_td_start_time.innerHTML = "<a href=\"/test/" + test_uuid + "\">" + test_start_time + "</a>";

    /* ETA */
    if(test_status === 1 || test_status === 2){
        if(test_time_taken_eta !== null ){
            data_td_eta.innerHTML = "<a href=\"/test/" + test_uuid + "\">ETA: " + test_time_taken_eta + "</a>";
        }
        else{
            data_td_eta.innerHTML = "<a href=\"/test/" + test_uuid + "\">Pending...</a>";
        }
    }
    else{
        if(test_time_taken !== null){
            data_td_eta.innerHTML = "<a href=\"/test/" + test_uuid+ "\">" + test_time_taken + "</a>";
        }
        else{
            data_td_eta.innerHTML = "<a href=\"/test/" + test_uuid + "\">Pending...</a>";
        }
    }

    /* Status */
    if(test_status === 1){
        data_td_status.innerHTML = "<a href=\"/test/" + test_uuid + "\" class=\"ui gray basic label\">Not Started</a>";
    }
    else if(test_status === 2){
        data_td_status.innerHTML = "<a href=\"/test/" + test_uuid+ "\" class=\"ui blue basic label\">In Progress</a>";
    }
    else if(test_status === 3){
        data_tr_test.className = "ui positive";
        data_td_status.innerHTML = "<a href=\"/test/" + test_uuid + "\" class=\"ui green basic label\">Passed</a>";
    }
    else if(test_status === 4){
        data_td_status.innerHTML = "<a href=\"/test/" + test_uuid + "\" class=\"ui red basic label\">Failed</a>";
        data_tr_test.className = "ui negative";
    }
    else if(test_status === 5){
        status = "<a href=\"/test/" + test_uuid + "\" class=\"ui yellow basic label\">Skipped</a>";
        data_tr_test.className = "ui warning";
    }
    else if(test_status === 6){
        data_td_status.innerHTML = "<a href=\"/test/" + test_uuid + "\" class=\"ui red basic label\">Aborted</a>";
        data_tr_test.className = "ui negative";
    }

};
socket.onclose = function() {
    console.error('Socket closed unexpectedly');
};
