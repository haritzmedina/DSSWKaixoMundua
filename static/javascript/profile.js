(function(){
    function updateUsernameAndEmail(){
        var user_id = document.getElementById("userinfo").dataset.userId;

        var username = document.getElementById("username").value;
        var email = document.getElementById("email").value;
        $.post("/api/user/"+user_id+"/changeUserData/", {username:username, email:email}, function(data){
            if(data.result=="OK"){
                KaixoMundua.utils.okayResponseBox(document.getElementById("username"));
                KaixoMundua.utils.okayResponseBox(document.getElementById("email"));
            }
        });
    }

    window.onload = function(){
        document.getElementById('username').addEventListener('change', updateUsernameAndEmail);
        document.getElementById('email').addEventListener('change', updateUsernameAndEmail);
    };
})();