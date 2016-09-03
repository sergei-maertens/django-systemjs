import google from 'google-maps';


export default class App {
    constructor() {
        document.getElementById('js-hook').innerText = 'myapp/app.js was loaded';

        new google.maps.Map(document.getElementById('map'), {
          center: {lat: -34.397, lng: 150.644},
          zoom: 8
        });
    }
}
