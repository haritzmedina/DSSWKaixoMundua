(function(){
    window.onload = function(){
        // Add change event handlers
        document.getElementById('nameInput').addEventListener('change', uploadChanges);
        document.getElementById('privacySelector').addEventListener('change', uploadChanges);
        document.getElementById('delete').addEventListener('click', deleteImage);
        document.getElementById('setAsBackground').addEventListener('click', setAsBackground);
        document.getElementById('setAsProfilePhoto').addEventListener('click', setAsProfilePhoto);
    };

    // Modify ajax function
    function uploadChanges(event){
        var photo_id = document.getElementById('photo').dataset.photoId;
        var name = document.getElementById('nameInput').value;
        var privacy = document.getElementById('privacySelector').value;
        $.post("/api/photo/modify/"+photo_id, {name: name, privacy: privacy}, function(data){
            // TODO show result to user
            console.log(data);
        });
    }

    function deleteImage(event){
        var messageToDisplay = document.getElementById("trans").dataset.wantToDelete;
        // Ask user if want to delete image
        if(confirm(messageToDisplay)){
            var photo_id = document.getElementById('photo').dataset.photoId;
            $.get("/api/photo/delete/"+photo_id, function(data){
                if(data.result=="OK"){
                    window.location = "/photos";
                }
                else{
                    // TODO Show error to user
                    console.log(data);
                }
            });
        }
    }

    function setAsBackground(event){
        var messageToDisplay = document.getElementById("trans").dataset.setAsBackground;
        if(confirm(messageToDisplay)){
            var photo_id = document.getElementById('photo').dataset.photoId;
            var user_id = document.getElementById("userinfo").dataset.userId;
            $.post("/api/user/"+user_id+"/changeUserData/", {background: photo_id}, function(data){
                window.location.reload(false);
            })
        }
    }

    function setAsProfilePhoto(event){
        var messageToDisplay = document.getElementById("trans").dataset.setAsProfilePhoto;
        if(confirm(messageToDisplay)){
            var photo_id = document.getElementById('photo').dataset.photoId;
            var user_id = document.getElementById("userinfo").dataset.userId;
            $.post("/api/user/"+user_id+"/changeUserData/", {photo: photo_id}, function(data){
                console.log(data);
            })
        }
    }
})();