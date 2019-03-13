$(document).ready(function(){
    $('#username').keyup(function(){
        console.log("You are checking if your First name is available")
        var data = $("#regForm").serialize()
        $.ajax({
            method: "POST",
            url: "/username",
            data: data
        })
        .done(function(res){
            $('#usernameMsg').html(res)
        })
        return false;
    })


    
    $('#search_bar').keyup(function(){
        console.log("You are using the search bar function")
        var data = $("#search_form").serialize()
        var precheck= $('#search_bar').val();
        if (precheck.length > 0 )
        $.ajax({
            method: "POST",
            url: "/search_bar",
            data: data
        })
        .done(function(res){
            $('#search_msg').html(res)
        })
        if (precheck == 0){
            $('#search_msg').html("")
        }
    })
    return false;
})

