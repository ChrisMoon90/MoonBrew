
$(document).ready(function(){
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');
    var socket2 = io.connect('http://' + document.domain + ':' + location.port + '/test2');
    var numbers_received = [];
    var numbers_received2 = 0;

    //receive details from server
    socket.on('newnumber', function(msg) {
        console.log("Received number" + msg.number);
        //maintain a list of ten numbers
        //if (numbers_received.length >= 3){
            //numbers_received.shift()
        //}            
        //numbers_received.push(msg.number);
        //numbers_string = '';
        //for (var i = 0; i < numbers_received.length; i++){
            //numbers_string = numbers_string + '<p>' + numbers_received[i].toString() + '</p>';
        //}
        //$('#log').html(numbers_string);
        numbers_received = msg.number
        $('#log').html(numbers_received);
    });
    
    //Incoming Temp Code 1 
    socket2.on('newtemp', function(msg2) {
        console.log("Received number" + msg2.temp);
        numbers_received2 = msg2.temp
        $('#temp').html(numbers_received2);
    });
});
