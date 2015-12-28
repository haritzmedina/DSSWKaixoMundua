/**
 * Created by Haritz on 27/12/2015.
 */

(function(){
    window.onload = function(){
        var activationFields = document.getElementsByClassName('role_level')

        for(var i=0;i<activationFields.length;i++){
            activationFields[i].addEventListener("click", function(event){
                var userId = event.target.parentNode.parentNode.dataset.userId;
                var checked = event.target.checked;
                var option = ""
                if(checked){
                    option = "activateAccountByAdmin"
                }
                else{
                    option = "deactivateAccountByAdmin"
                }
                $.get("/api/user/"+userId+"/"+option+"/", function(data){
                    if(data.result=="FAIL"){
                        alert(data.data.error);
                    }
                })
            });
        }
    };
})();