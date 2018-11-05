$("#force_stop_job").click(function () {
    var job_id = $(this).data("job-id");
    var job_force_stop_url = $(this).data("job-force-stop-url");
    $.ajax({
        url : job_force_stop_url,
        type : "POST",
        data: '{"uuid": "' + job_id + '"}',
        contentType: "application/json",
        dataType: 'json',
        success : function(json) {
            if(json['status'] === 'ok'){
            alert("Job stopped!");
            }
        }
    });
});
