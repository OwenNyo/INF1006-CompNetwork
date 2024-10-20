document.addEventListener('DOMContentLoaded', function() {
    var socket = io();  // Connect to the current host and port implicitly
    
    socket.on('connect', function() {
        console.log('Connected to SocketIO server');
    });

    socket.on('disconnect', function() {
        console.log('Disconnected from SocketIO server');
    });

    socket.on('update_data', function(data) {
        updateTemperature(data['TemperatureAndHumidity']);
        updateMotion(data['Motion']);
        updateUltrasonic(data['Ultrasonic']);
        updateLight(data['Light']);
    });

    function updateTemperature(data) {
        if (data.length > 0) {
            var temperature = data[0]['message'].split(',')[0];
            var humidity = data[0]['message'].split(',')[1];
                    
            var temperatureElement = document.getElementById('temperature_value');
            var humidityElement = document.getElementById('humidity_value');
            
            temperatureElement.textContent = temperature + ' °C';
            humidityElement.textContent = humidity + ' %';
            
            if (parseInt(temperature) > 24 || parseInt(humidity) > 55) {
                document.getElementById('aircon-on-img').classList.remove('hidden');
                document.getElementById('aircon-off-img').classList.add('hidden');
            } else {
                document.getElementById('aircon-on-img').classList.add('hidden');
                document.getElementById('aircon-off-img').classList.remove('hidden');
            }
        }
    }

    function updateMotion(data) {
        if (data.length > 0) {
            var motion = data[0]['message'];
            document.getElementById('motion_value').innerHTML = motion;

            if (motion == "Detected") {
                document.getElementById('room-on-img').classList.remove('hidden');
                document.getElementById('room-off-img').classList.add('hidden');
            } else {
                document.getElementById('room-on-img').classList.add('hidden');
                document.getElementById('room-off-img').classList.remove('hidden');
            }
        }        
    }

    function updateUltrasonic(data) {
        if (data.length > 0) {
            var ultrasonic = data[0]['message'];
            document.getElementById('ultrasonic_value').innerHTML = ultrasonic + ' cm';

            var cameraIframe = document.getElementById('camera_iframe');
            if(parseInt(ultrasonic) < 40){
                cameraIframe.style.backgroundColor = ""; 
            } else {
                cameraIframe.style.backgroundColor = "black"; 
            }
        }       
    }

    function updateLight(data) {
        if (data.length > 0) {
            var light = data[0]['message'];
            document.getElementById('light_value').innerHTML = light;

            if (light == "Not Detected") {
                document.getElementById('plant-on-img').classList.remove('hidden');
                document.getElementById('plant-off-img').classList.add('hidden');
            } else {
                document.getElementById('plant-on-img').classList.add('hidden');
                document.getElementById('plant-off-img').classList.remove('hidden');
            }

        }     
    }
});
