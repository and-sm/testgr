var socket = new WebSocket(
    'ws://' + window.location.host +  '/ws/running_jobs/');
    socket.onmessage = function(e) {
    let data = JSON.parse(e.data);
    let message = data['message'];
    let Table = document.getElementById("running_jobs");
    let remove_job = message['job_remove'];

    if (remove_job){
        deleteRow = document.querySelector('[data-tr-job="' + remove_job + '"]');
        if(deleteRow.parentNode)
        deleteRow.parentNode.removeChild(deleteRow);
    }
    else {

        message.forEach(function (obj) {

            let job_tr = document.querySelector('[data-tr-job="' + obj.uuid + '"]');
            let start_time = document.querySelector('[data-td-start-time="' + obj.uuid + '"]');
            let env = document.querySelector('[data-td-env="' + obj.uuid + '"]');
            let status = document.querySelector('[data-td-status="' + obj.uuid + '"]');
            let data_tests_passed = document.querySelector('[data-tests-passed="' + obj.uuid + '"]');
            let data_tests_failed = document.querySelector('[data-tests-failed="' + obj.uuid + '"]');
            let data_tests_aborted = document.querySelector('[data-tests-aborted="' + obj.uuid + '"]');
            let data_tests_skipped = document.querySelector('[data-tests-skipped="' + obj.uuid + '"]');
            let data_tests_not_started = document.querySelector('[data-tests-not-started="' + obj.uuid + '"]');

            if (job_tr == null) {
                let row = Table.insertRow(0);
                row.setAttribute("data-tr-job", obj.uuid);

                let cell1 = row.insertCell(0);
                cell1.setAttribute("data-td-start-time", obj.uuid);
                cell1.innerHTML = "<a href=job/" + obj.uuid + ">" + obj.start_time + "</a>";

                let cell2 = row.insertCell(1);
                cell2.setAttribute("data-td-env", obj.uuid);
                cell2.innerHTML = "<a href=job/" + obj.uuid + ">" + obj.env + "</a>";

                let cell3 = row.insertCell(2);
                cell3.setAttribute("data-td-status", obj.uuid);

                if(obj.tests_passed !== undefined){
                initial_tests_passed = "<a data-tests-passed=\"" + obj.uuid + "\" href=\"job/" + obj.uuid + "\" " +
                            "class=\"ui green basic label\">" + obj.tests_passed + "</a>";}
                else{initial_tests_passed = ""}
                if(obj.tests_failed !== undefined){
                initial_tests_failed = "<a data-tests-failed=\"" + obj.uuid + "\" href=\"job/" + obj.uuid + "\" " +
                            "class=\"ui red basic label\">" + obj.tests_failed + "</a>";}
                else{initial_tests_failed=""}
                if(obj.tests_aborted !== undefined){
                initial_tests_aborted = "<a data-tests-aborted=\"" + obj.uuid + "\" href=\"job/" + obj.uuid + "\" " +
                            "class=\"ui darkred basic label\">" + obj.tests_aborted + "</a>";}
                else{initial_tests_aborted=""}
                if(obj.tests_skipped !== undefined){
                initial_tests_skipped = "<a data-tests-skipped=\"" + obj.uuid + "\" href=\"job/" + obj.uuid + "\" " +
                            "class=\"ui yellow basic label\">" + obj.tests_skipped + "</a>";}
                else{initial_tests_skipped=""}
                if(obj.tests_not_started !== undefined){
                initial_tests_not_started = "<a data-tests-not-started=\"" + obj.uuid + "\" href=\"job/" + obj.uuid + "\" " +
                            "class=\"ui grey basic label\">" + obj.tests_not_started + "</a>";}
                else{initial_tests_not_started=""}

                cell3.innerHTML = initial_tests_passed + initial_tests_failed + initial_tests_aborted +
                    initial_tests_skipped + initial_tests_not_started;

            } else {

                if (obj.start_time == null) {
                    start_time.innerHTML = ""
                } else {
                    start_time.innerHTML = "<a href=job/" + obj.uuid + ">" + obj.start_time + "</a>"
                }
                if (obj.env == null) {
                    env.innerHTML = "None"
                } else {
                    env.innerHTML = "<a href=job/" + obj.uuid + ">" + obj.env + "</a>"
                }

                if (obj.tests_passed === undefined) {
                    //status.innerHTML = "";
                } else {
                    if (data_tests_passed === null) {
                        status.innerHTML += "<a data-tests-passed=\"" + obj.uuid + "\" href=\"job/" + obj.uuid + "\" " +
                            "class=\"ui green basic label\">" + obj.tests_passed + "</a>"
                    } else {
                        data_tests_passed.innerHTML = obj.tests_passed
                    }
                }

                if (obj.tests_failed === undefined) {
                    //status.innerHTML = "";
                } else {
                    if (data_tests_failed === null) {
                        status.innerHTML += "<a data-tests-failed=\"" + obj.uuid + "\" href=\"job/" + obj.uuid + "\" " +
                            "class=\"ui red basic label\">" + obj.tests_failed + "</a>"
                    } else {
                        data_tests_failed.innerHTML = obj.tests_failed
                    }
                }

                if (obj.tests_aborted === undefined) {
                    //status.innerHTML = "";
                } else {
                    if (data_tests_aborted === null) {
                        status.innerHTML += "<a data-tests-aborted=\"" + obj.uuid + "\" href=\"job/" + obj.uuid + "\" " +
                            "class=\"ui darkred basic label\">" + obj.tests_aborted + "</a>"
                    } else {
                        data_tests_aborted.innerHTML = obj.tests_aborted
                    }
                }

                if (obj.tests_skipped === undefined) {
                    //status.innerHTML = "";
                } else {
                    if (data_tests_skipped === null) {
                        status.innerHTML += "<a data-tests-skipped=\"" + obj.uuid + "\" href=\"job/" + obj.uuid + "\" " +
                            "class=\"ui yellow basic label\">" + obj.tests_skipped + "</a>"
                    } else {
                        data_tests_skipped.innerHTML = obj.tests_skipped
                    }
                }

                if (obj.tests_not_started === undefined) {
                    //status.innerHTML = "";
                } else {
                    if (data_tests_not_started === null) {
                        status.innerHTML += "<a data-tests-not-started=\"" + obj.uuid + "\" href=\"job/" + obj.uuid + "\" " +
                            "class=\"ui grey basic label\">" + obj.tests_not_started + "</a>"
                    } else {
                        data_tests_not_started.innerHTML = obj.tests_not_started
                    }
                }

            }
        })
    }
};
socket.onclose = function(e) {
    console.error('Socket closed unexpectedly');
};
