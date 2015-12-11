var map;
function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        center: {lat: 43, lng: -2},
        zoom: 8
    });
}
