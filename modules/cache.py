from modules.app_config import *

class CacheAPI:
    def __init__(self):
        self.cache = {

            "init": [],
            "sensors":[],
            "hardware":[],

        }
        print(self.cache)

    def initializer(self):
        for i in self.cache("init"):
            print(i)
            thread = "thread_%s" % i
            thread = socketio.start_background_task(target=i["function"], device=i["device"], dev_id=i["dev_id"], sleep=i["sleep"])
