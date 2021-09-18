import time
import os
from modules.app_config import socketio


class logAPI:
    def __init__(self, a):
        self.running = False
        self.temps = a.temps

    def set_run_state(self, logState):
        self.running = logState

    def save_to_file(self, sleep):
        print("Starting Logging")
        while self.running:
            filename = "./logs/Temps.log"
            formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            msg = "%s, %s\n" % (formatted_time, self.temps)
            print("Saving to File: %s" %self.temps)
            with open(filename, "a") as file:
                file.write(msg)
            socketio.sleep(sleep)
        print("Log Thread Terminated")

    def send_log_state(self):
        socketio.emit('logState', self.running)
        print("LogState Sent: ", self.running)
    
    def send_fetched_log_state(self):
        socketio.emit('fetched_logState', self.running)
        print("Fetched LogState Sent: ", self.running)

    def toggle_logState(self, logState_in):
        logState = not logState_in
        self.set_run_state(logState)
        if logState == True:
            thread2 = socketio.start_background_task(target=self.save_to_file, sleep = 15)
        else:
            print("Stopping Logging Thread") 
        self.send_log_state()

    def delete_log(self):   
        filename = "./logs/Temps.log"
        if os.path.exists(filename):
            os.remove(filename)
            msg = "Temp Log File Successfully Deleted"
            print(msg)
            socketio.emit('log_deleted', msg)
        else:
            print("The file does not exist")