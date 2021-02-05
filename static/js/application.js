//connect to the socket server.
var socket = io()

function getDropDownVal1() {
    var selectedValue1 = document.getElementById("DropDown1").value;
    return selectedValue1;
}
function getDropDownVal2() {
    var selectedValue2 = document.getElementById("DropDown2").value;
    return selectedValue2
}

//Add function to emit sensor change only when index changed
    //console.log("Dropdown1 Index = ", selectedValue1);
    //socket.emit('sensor_change', { index: selectedValue1});
//make if statment to check for values from python

$(document).ready(function(){
    //Incoming Temp Readings
    socket.on('newtemps', function(msg){
        console.log('TEMP UPDATE', msg);
        temp_in = msg;
        selectedValue1 = getDropDownVal1();
        var Temp1 = temp_in[selectedValue1];
        $('#Temp1').html(Temp1);
        selectedValue2 = getDropDownVal2();
        var Temp2 = temp_in[selectedValue2];
        $('#Temp2').html(Temp2);
    });
    
    socket.on('connected', function(msg){
        console.log('After connect', msg);
    });
    
    socket.on('connect', function() {
        socket.send('User has connected!');
    });
});

