
$(document).ready(function(){
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port); // + '/test2');
    var numbers_received = 0;
    var numbers_received2 = 0;
    
    //Incoming Temp Readings 1
    socket.on('newtemp1', function(msg1) {
        console.log("Received temp1 = " + msg1.temp1);
        numbers_received1 = msg1.temp1
        $('#temp1').html(numbers_received1);
    });
    
    //Incoming Temp Readings 2
    socket.on('newtemp2', function(msg2) {
        console.log("Received temp2 = " + msg2.temp2);
        numbers_received2 = msg2.temp2
        $('#temp2').html(numbers_received2);
    });
});
