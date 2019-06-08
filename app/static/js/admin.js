$(document).ready(function(){
    console.log("ADMIN");

    var csrftoken = $('meta[name=csrf-token]').attr('content')

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken)
            }
        }
    });

    console.log(csrftoken);

    $("#timetable-picker").click(function(){
        $.ajax({
          type: 'POST',
          url: "/admin/timetable",
          contentType: "application/json",
          data: JSON.stringify({
            yaer: 1
          }),
          success: function(data){
            console.log(data);
          },
          error: function() {}
        });
    });
});


