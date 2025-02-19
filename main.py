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

    def prod(self) -> simpy.Environment:
        while True:
            print("Start prod")
            duration = 5 
            yield self._env.timeout(duration)

            print("Prod start at %d" % self._env.now)
            prod_duration = 2
            yield self._env.timeout(prod_duration)
            print("Prod done at %d" % self._env.now)

    def resupply(self):
        with self._resupply_device.request as req:
            yield req
            print("Starting resupply at %d" % self._env.now)


env = simpy.Environment()
factory = (Factory(env))
env.run(until=30)
