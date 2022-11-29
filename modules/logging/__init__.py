import time
import os
from modules.app_config import socketio


class logAPI:
    def __init__(self, a):
        self.running = False
        self.temps = a.temps
        self.filename = "./logs/Temps.csv"

    def set_run_state(self, logState):
        self.running = logState

    def save_to_file(self, sleep):
        print("Starting Logging")
        while self.running: 
            formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            msg = "%s, %.3f, %.3f, %.3f" % (formatted_time, self.temps[0], self.temps[1], self.temps[2])
            print("Saving to File: %s" % msg)
            if os.path.exists(self.filename):
                with open(self.filename, "a") as f:
                    f.write("%s\n" % msg)
                socketio.sleep(sleep)
            else:
                print("Temp.csv file does not exist. File will be created.")
                header = "Time, Sensor 1, Sensor 2, Sensor 3\n"
                with open(self.filename, 'a') as f:
                    f.write(header)
                    f.write(msg)
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
        if os.path.exists(self.filename):
            os.remove(self.filename)
            msg = "Temp Log File Successfully Deleted"
            print(msg)
            socketio.emit('log_deleted', msg)
        else:
            print("The file does not exist")