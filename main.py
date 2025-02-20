import simpy
import random

#Constants
work_stations = 6

class Factory(object):
    def __init__(self, env: simpy.Environment):
        self._env = env
        self.station = [simpy.Resource(env, capacity=1) for _ in range(work_stations)]
        self._resupply_device = simpy.Resource(env, capacity = 3)
        self._prod = env.process(self.prod())

    # ---- Produccion Process ----
    def prod(self) -> simpy.Environment:
        while True:
            #Easy cycle for first 3 stations
            for i in range(3):
                yield self._env.timeout(5)
                print(f"Product moving to Workstation {i + 1} at {self._env.now}")
            
            #Hardcoding rest of process /// Find a way to make it a cycle or make it simplier
            selection = random.randint(3, 4)
            if selection == 4:
                print(f"Product moving to Workstation {5} at {self._env.now}")
                yield self._env.timeout(5)
                print(f"Product moving to Workstation {4} at {self._env.now}")
            else:
                print(f"Product moving to Workstation {4} at {self._env.now}")
                yield self._env.timeout(5)
                print(f"Product moving to Workstation {5} at {self._env.now}")

            yield self._env.timeout(5)
            print(f"Product moving to Workstation {6} at {self._env.now}")

    # ---- End of produccion ----

    #Resupply Request
    def resupply(self):
        with self._resupply_device.request() as req:
            yield req
            print("Starting resupply at %d" % self._env.now)
            yield env.timeout(10)
            print("Resupply finished at %d" % self._env.now)
            


env = simpy.Environment()
factory = (Factory(env))
env.run(until=100)
