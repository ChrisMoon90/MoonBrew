import time
import os
from modules.app_config import socketio


class logAPI:
    def __init__(self, a):
        self.running = False
        self.temps = a.temps

    def set_run_state(self, logState):
        self.running = logState
        print("Logging run_state changed: ", self.running)

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

    def toggle_logState(self, logState_in):
        print("logstate: ", logState_in)
        logState = not logState_in
        self.set_run_state(logState)
        if logState == True:
            thread2 = socketio.start_background_task(target=self.save_to_file, sleep = 15)
        else:
            print("Stopping Logging Thread") 
        socketio.emit('logState', logState)

    def delete_log(self):   
        filename = "./logs/Temps.log"
        if os.path.exists(filename):
            os.remove(filename)
            msg = "Temp Log File Successfully Deleted"
            print(msg)
            socketio.emit('log_deleted', msg)
        else:
            print("The file does not exist")