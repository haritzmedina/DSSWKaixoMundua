(function(){
    window.onload = function(){
        // TODO Add change event handlers
         document.getElementById('nameInput').addEventListener('change', uploadChanges);
         document.getElementById('privacySelector').addEventListener('change', uploadChanges);
    };

    // TODO Create modify ajax function
    function uploadChanges(event){
        var photo_id = document.getElementById('photo').dataset.photoId;
        var name = document.getElementById('nameInput').value;
        var privacy = document.getElementById('privacySelector').value;
        $.post("/api/photo/modify/"+photo_id, {name: name, privacy: privacy}, function(data){
            console.log(data);
        });
    }
})();