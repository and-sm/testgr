var socket = new WebSocket(
    'ws://' + window.location.host +  '/ws/latest_jobs/');
    socket.onmessage = function(e) {
    var data = JSON.parse(e.data);
    var message = data['message'];
    var Table = document.getElementById("latest_jobs");
    let env = "";
    let tests_passed = "";
    let tests_failed = "";
    let tests_aborted = "";
    let tests_skipped = "";
    let tests_not_started = "";
    let tests_info = "";
    let stopped = "";
    if(message == null){
        Table.innerHTML = ""
    }
    else {
        Table.innerHTML = "";
        message.forEach(function (obj) {
            if(obj.env == null){env = "None"}else{env = obj.env}
            if(obj.tests_passed != null){tests_passed = "<a href=job/" + obj.uuid +
                "/#table_success_tests class=\"ui green basic label\">" + obj.tests_passed + "</a>"}else{tests_passed = ""}
            if(obj.tests_failed != null){tests_failed = "<a href=job/" + obj.uuid +
                "/#table_negative_tests class=\"ui red basic label\">" + obj.tests_failed + "</a>"}else{tests_failed = ""}
            if(obj.tests_aborted != null){tests_aborted = "<a href=job/" + obj.uuid +
                "/#table_negative_tests class=\"ui darkred basic label\">" + obj.tests_aborted + "</a>"}else{tests_aborted = ""}
            if(obj.tests_skipped != null){tests_skipped = "<a href=job/" + obj.uuid +
                "/#table_skipped_tests class=\"ui yellow basic label\">" + obj.tests_skipped + "</a>"}else{tests_skipped = ""}
            if(obj.tests_not_started != null){tests_not_started = "<a href=job/" + obj.uuid +
                "/#table_not_started_tests class=\"ui grey basic label\">" + obj.tests_not_started + "</a>"}else{tests_not_started = ""}
            if(obj.status === 4){stopped = "<a href=job/" + obj.uuid +
                " class=\"ui yellow basic label\">Stopped</a>"}else{stopped = ""}

            let passed_ratio = "";
            if(obj.tests_percentage['passed_percent'] > 0){
                passed_ratio = "<td class=\"selectable\" style=\"width:" + obj.tests_percentage['passed_percent'] + "%;background-color: #5bcd5b\"></td>\n"
            }
            let failed_ratio = "";
            if(obj.tests_percentage['failed_percent'] > 0){
                failed_ratio = "<td class=\"selectable\" style=\"width:" + obj.tests_percentage['failed_percent'] + "%;background-color: #e74c54\"></td>\n"
            }
            let aborted_ratio = "";
            if(obj.tests_percentage['aborted_percent'] > 0){
                aborted_ratio = "<td class=\"selectable\" style=\"width:" + obj.tests_percentage['aborted_percent'] + "%;background-color: #b41f1f\"></td>\n"
            }

            let skipped_ratio = "";
            if(obj.tests_percentage['skipped_percent'] > 0){
                skipped_ratio = "<td class=\"selectable\" style=\"width:" + obj.tests_percentage['skipped_percent'] + "%;background-color: #e8e616\"></td>\n"
            }

            let not_started_ratio = "";
            if(obj.tests_percentage['not_started_percent'] > 0){
                not_started_ratio = "<td class=\"selectable\" style=\"width:" + obj.tests_percentage['not_started_percent'] + "%;background-color: #747576\"></td>\n"
            }

            let job_info_tests_passed = "";
            if(obj.tests_passed){
                job_info_tests_passed = "Passed: " + obj.tests_passed + "%<br>";
            }

            let job_info_tests_failed = "";
            if(obj.tests_failed){
                job_info_tests_failed = "Failed: " + obj.tests_failed + "%<br>";
            }

            let job_info_tests_aborted = "";
            if(obj.tests_aborted){
                job_info_tests_aborted = "Aborted: " + obj.tests_aborted + "%<br>";
            }

            let job_info_tests_skipped = "";
            if(obj.tests_skipped){
                job_info_tests_skipped = "Skipped: " + obj.tests_skipped + "%<br>";
            }

            let job_info_tests_not_started = "";
            if(obj.tests_not_started){
                job_info_tests_not_started = "Not started: " + obj.tests_not_started + "%<br>";
            }

            tests_info = "<strong>Tests:</strong><br>" + job_info_tests_passed + job_info_tests_failed + job_info_tests_aborted +
                job_info_tests_skipped + job_info_tests_not_started;

            var row = Table.insertRow(0);
            var cell1 = row.insertCell(0);
            cell1.classList.add("selectable");
            cell1.innerHTML = "<a href=job/" + obj.uuid + ">" + obj.stop_time + "</a>";
            var cell2 = row.insertCell(1);
            cell2.classList.add("selectable");
            cell2.innerHTML = "<a href=job/" + obj.uuid + ">" + obj.time_taken + "</a>";
            var cell3 = row.insertCell(2);
            cell3.classList.add("selectable");
            cell3.innerHTML = "<a href=job/" + obj.uuid + ">" + env + "</a>";
            var cell4 = row.insertCell(3);
            // added for cell4, because it's not possible to add 'onclick' arg directly to html element
            cell4.onclick = function() { window.location.href = "/job/" + obj.uuid + "/"; };
            cell4.classList.add("job_status", "selectable");
            cell4.setAttribute("data-html", tests_info);
            cell4.innerHTML = "&nbsp;&nbsp;" + tests_passed + tests_failed + tests_aborted + tests_skipped +
                tests_not_started + stopped;
            var cell5 = row.insertCell(4);
            // added for cell5, because it's not possible to add 'onclick' arg directly to html element
            cell5.onclick = function() { window.location.href = "/job/" + obj.uuid + "/"; };
            cell5.setAttribute("data-html", "<strong>Ratio:</strong><br>" +
                "Passed: " + obj.tests_percentage['passed_percent_float'] + "%<br>" +
                "Failed: " + obj.tests_percentage['failed_percent_float'] + "%<br>" +
                "Aborted: " + obj.tests_percentage['aborted_percent_float'] + "%<br>"+
                "Skipped: " + obj.tests_percentage['skipped_percent_float'] + "%<br>"+
                "Not started: " + obj.tests_percentage['not_started_percent_float'] + "%<br>");
            cell5.classList.add("job_status", "one", "wide", "selectable");
            cell5.innerHTML = "<div class=\"progress\">\n" +
                "                            <div>\n" +
                "                                <table class=\"large table_progress\">\n" +
                "                                    <tr>\n" + passed_ratio +
                failed_ratio + aborted_ratio + skipped_ratio + not_started_ratio;
                "                                    </tr>\n" +
                "                                </table>\n" +
                "                            </div>\n" +
                "                        </div>";

            // TODO Rewrite for clean JS

            $('.job_status')
                .popup({
                    on: 'hover'
                })
            ;

        })
    }
};
socket.onclose = function(e) {
    console.error('Socket closed unexpectedly');
};
