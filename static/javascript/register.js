(function(){
    // Password mismatching functionality
    window.onload = function(){
        document.getElementById("password1").onchange = validatePassword;
        document.getElementById("password2").onchange = validatePassword;
    }

    function validatePassword(){
        var pass2=document.getElementById("password2").value;
        var pass1=document.getElementById("password1").value;
        var messageToDisplay = document.getElementById("trans").dataset.passwordMissmatch;
        if(pass1!=pass2){
            document.getElementById("password2").setCustomValidity(messageToDisplay);
        }
        else{
            document.getElementById("password2").setCustomValidity('');
        }
    }

})();