//Connect to the socket server.
var socket = io()

indexes = {}
socket.on('indexes', function(msg){
    indexes['s0'] = msg['s0'];
    indexes['s1'] = msg['s1'];
    indexes['s2'] = msg['s2'];
    console.log('Server Indexes Received: ', indexes);
});
function getDropDownVal1() {
    var selectedvalue1 = document.getElementById("DropDown1").value;
    indexes['s0'] = selectedvalue1;
    console.log('User Index Change s0: ', indexes);
    socket.emit("index_change", indexes);
}
function getDropDownVal2() {
    var selectedvalue2 = document.getElementById("DropDown2").value;
    indexes['s1'] = selectedvalue2;
    console.log('User Index Change s1: ', indexes);
    socket.emit("index_change", indexes);
}
function getDropDownVal3() {
    var selectedvalue3 = document.getElementById("DropDown3").value;
    indexes['s2'] = selectedvalue3;
    console.log('User Index Change s2: ', indexes);
    socket.emit("index_change", indexes);
}
//Incoming Temp Readings
socket.on('newtemps', function(temp_in){
    console.log('TEMP UPDATE', temp_in);
    var sensor1 = indexes['s0'];
    var Temp1 = temp_in[sensor1];
    $('#Temp1').html(Temp1);        
    var sensor2 = indexes['s1'];
    var Temp2 = temp_in[sensor2];
    $('#Temp2').html(Temp2);        
    var sensor3 = indexes['s2'];
    var Temp3 = temp_in[sensor3];
    $('#Temp3').html(Temp3);
});
