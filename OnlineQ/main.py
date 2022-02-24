import io, math
from visualise_graph import Graph, dijsktra
import time


car_count = 1
simlen = 1

class Street:
    start = -1
    end = -1
    name = ""
    length = -1
    fitness = 0

    def __init__(self, line):
        splt = line.split(' ')
        self.start = splt[0]
        self.end = splt[1]
        self.name = splt[2]
        self.length  = int(splt[3])

    def getLightScore(self):
        time = self.fitness/car_count
        if time < 0.9:
            time = 0
        return time*simlen


class Car:
    routes = []
    routes_curr = 0
    routes_rem_curr = 0
    streets = []

    def __init__(self, line):
        splt = line.split(' ')
        self.routes = splt[1:]
        self.routes[-1] = self.routes[-1].strip()

    def step(self, streets):
        if self.routes_curr >= len(streets):
            return
        if(self.routes_rem_curr == 0):
            self.routes_curr += 1
            self.routes_rem_curr = streets[self.routes_curr].length # TODO: We need the actual route length
            val = 1
            for street in self.streets:
                val += street.length
            streets[self.routes_curr].fitness += val/100

class Rule:
    intersection_id = -1
    light_rules = {}
    road_fitness = {}

    def __init__(self, id, rules):
        self.intersection_id = id
        self.light_rules = rules
    
    def calculate_lights(self):
        avg = sum(self.road_fitness.values()) / len(self.road_fitness.values())
        max_fitness = 0
        max_fitness_i = 0
        for i in self.road_fitness:
            fitness = self.road_fitness[i]
            self.light_rules[i] = fitness
            if fitness > avg * 5:
                max_fitness = fitness
                self.light_rules[i] = max_fitness
                max_fitness_i = i
                break
        if max_fitness > 0:
            if max_fitness >= simlen:
                delta = simlen
            else:
                delta = simlen - max_fitness
                delta = delta / (len(self.road_fitness.values()) - 1)
            for i in self.road_fitness:
                fitness = self.road_fitness[i]
                if i != max_fitness_i:
                    self.light_rules[i] = delta

    def serialize(self, fp):
        fp.write(str(self.intersection_id)  + "\n")
        fp.write(str(len(self.light_rules))  + "\n")
        for rule in self.light_rules:
            fp.write(rule + " "  + str(self.light_rules[rule]) + "\n")


def main():
    lines = []
    for fp in ['a.txt',
             'b.txt',
             'c.txt',
             'd.txt',
             'e.txt',
             #'f.txt'
             ]:

        start = time.time()
        with open(fp) as f:
            print('Colculating trafic light arrangement for:' + fp + "!")
            lines = f.readlines()

        split0 = lines[0].split(' ')

        simlen = int(split0[0])
        intersect_count = int(split0[1])
        street_count = int(split0[2])
        car_count = int(split0[3])
        score_mult = int(split0[4])

        streets = []
        cars = []
        for i in range(0, street_count):
            streets.append(Street(lines[i+1]))
        for i in range(0, car_count):
            cars.append(Car(lines[i+1+street_count]))
        print('Read ' + str(len(streets)) + " street(s)!")
        print('Read ' + str(len(cars)) + " car(s)!")
        rules = {}

        badCars = set()
        for i in range(len(cars)):
            car = cars[i]
            if car in badCars:
                continue
            car.optimalTime = 0
            carcannotfinish = False
            car.bad = False
            for route in car.routes:
                for street in streets:
                    if route == street.name:
                        car.optimalTime += street.length
                        if car.optimalTime > simlen:
                            badCars.add(car)
                            carcannotfinish = True
                            break
                if carcannotfinish:
                    for j in range(i, len(cars)):
                        car2 = cars[j]
                        if car2.routes[0] == car.routes[0]:
                            if car2 not in badCars:
                                badCars.add(car2)
                    car.bad = True
                    break
            if car not in badCars:
                car.streets = []
                for route in car.routes:
                    for node in streets:
                        if route == node.name:
                            car.streets.append(node)

        for car in badCars:
            cars.remove(car)

        for i in range(0, simlen):
            for car in cars:
                car.step(streets)
        print('Simulation finished...')

        for node in streets:
            if node.end not in rules:
                rules[node.end] = Rule(node.end, {node.name: 1})
            rules[node.end].road_fitness[node.name] = node.fitness
        
        for rule in rules:
            rules[rule].calculate_lights()


        dump_outfile(rules, fp)
        end = time.time()
        print('Time of calculation: ' + str(end - start))
        
def dump_outfile(rules, infilename):
    with open(infilename[:-3] + ".out", "w") as outf:
        outf.write(str(len(rules))  + "\n")
        for rule in rules:
            rules[rule].serialize(outf)
    print('Output written...')
    

if __name__ == "__main__":
    main()

