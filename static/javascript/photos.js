/**
 * Created by Haritz on 22/12/2015.
 */

(function(){
    window.onload = function(){

        Dropzone.autoDiscover = false;

        function createNewDropzone(){
            // Request blob upload url to GAE and create dropzone uploader
            $.ajax({
                dataType: "json",
                url: "/photos/upload/path",
                data: {},
                success: function(data){
                    var dropzone = new Dropzone("div#photo-dropzone", {
                        url: data.data.url,
                        acceptedFiles: "image/*",
                        clickable: true,
                        success: function(uploader, response){
                            // Show image on page
                            var imageId = response.data.photo_id;
                            showImage(imageId);
                            // Change dropzone url
                            dropzone.destroy();
                            createNewDropzone();
                        }
                    });
                }
            });
        }

        function showImage(photo_id){
            // Create image
            var img = document.createElement('img');
            img.src = "/photos/download/"+photo_id;
            img.classList.add("photo");
            // Append to container
            var container = document.getElementById('photoContainer');
            container.insertBefore(img, container.firstChild);
        }

        /* Create the dynamic content */

        // File uploader: Check if user can upload images, and create a dropzone for it
        var dropzone = document.getElementById("photo-dropzone");
        if(dropzone){
            createNewDropzone();
        }

        // Photos visualization
        // TODO Retrieve all photos
        $.getJSON("/photos/manage/list", {}, function(data){
            var photos = data.data.photos;
            for(var i=0;i<photos.length;i++){
                photo = photos[i];
                showImage(photo.photo_id);
            }
        });


    };
})();

