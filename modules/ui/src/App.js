//import logo from './logo.svg';
//import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import Button from 'react-bootstrap/Button';
import Jumbotron from 'react-bootstrap/Jumbotron';
import Dropdown from 'react-bootstrap/Dropdown';


//Connect to the socket server.
//const io = require("socket.io-client");
import socketio from "socket.io-client";
var socket = socketio.connect('http://192.168.0.31:5000');
socket.on('connect',console.log('Connected to socket.io server!!'));

var indexes = {};
socket.on('indexes', function(msg){
    indexes['s0'] = msg['s0'];
    indexes['s1'] = msg['s1'];
    indexes['s2'] = msg['s2'];
    console.log('Server Indexes Received: ', indexes);
    var Sensor0 = Number(indexes['s0']) + 1;
    //$('#Sensor0').html(Sensor0); 
    var Sensor1 = Number(indexes['s1']) + 1;
    //$('#Sensor1').html(Sensor1); 
    var Sensor2 = Number(indexes['s2']) + 1;
    //$('#Sensor2').html(Sensor2); 
});
function getDropDownVal1() {
    var selectedvalue1 = 1;
    //var selectedvalue1 = document.getElementById("DropDown1").value;   
    indexes['s0'] = selectedvalue1;
    console.log('User Index Change s0: ', indexes);
    socket.emit("index_change", indexes);
};
function getDropDownVal2() {
    var selectedvalue2 = 1;
    //var selectedvalue2 = document.getElementById("DropDown2").value;
    indexes['s1'] = selectedvalue2;
    console.log('User Index Change s1: ', indexes);
    socket.emit("index_change", indexes);
};
function getDropDownVal3() {
    var selectedvalue3 = 1;
    //var selectedvalue3 = document.getElementById("DropDown3").value;
    indexes['s2'] = selectedvalue3;
    console.log('User Index Change s2: ', indexes);
    socket.emit("index_change", indexes);
};
//Incoming Temp Readings
socket.on('newtemps', function(temp_in){
    console.log('TEMP UPDATE', temp_in);
    var sensor1 = indexes['s0'];
    var Temp1 = temp_in[sensor1];
    //$('#Temp1').html(Temp1);        
    var sensor2 = indexes['s1'];
    var Temp2 = temp_in[sensor2];
    //$('#Temp2').html(Temp2);        
    var sensor3 = indexes['s2'];
    var Temp3 = temp_in[sensor3];
    //$('#Temp3').html(Temp3);
});

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <Jumbotron>
          <h1>MOON BREW CO.</h1>
          <p>SMOKER PI LIVE FEED & COTROL PANEL</p>
          <p>Version 1.0.0</p>
        </Jumbotron>

        <Button variant="primary">Primary</Button>{' '}
      </header>
      
      <table class="table">        
        <thead>
          <tr>
            <th>#</th>
            <th>Sensor Name</th>
            <th>Sensor ID</th>
            <th>(toggle)</th>
            <th>Current Value</th>
          </tr>
        </thead>
        <tbody>          
          <tr>
            <td>1</td>
            <td>Smoker Temp</td>
            <td>Sensor1</td>
            <td>
            <Dropdown>
              <Dropdown.Toggle variant="success" id="dropdown-basic">
                Edit
              </Dropdown.Toggle>
              <Dropdown.Menu>
                <Dropdown.Item href="#/action-1">1</Dropdown.Item>
                <Dropdown.Item href="#/action-2">2</Dropdown.Item>
                <Dropdown.Item href="#/action-3">3</Dropdown.Item>
              </Dropdown.Menu>
            </Dropdown>
            </td>

            <td>Test</td>
          </tr>
          <tr>
            <td>2</td>
            <td>Meat Temp 1</td>
            <td>Test</td>
            <td>
              Test                   
            </td>
            <td>TEst</td>
          </tr>          
          <tr>
            <td>3</td>
            <td>Meat Temp 2</td>
              <td></td>
              <td>
                Test! Fuck yeah!  
            </td>
            <td>Test</td>
          </tr>
        </tbody>
      </table>
    </div>
  );
};
export default App;
