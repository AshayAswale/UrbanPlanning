import numpy as np
from copy import deepcopy
import random
import uuid


class GeneticAlgo():

    def __init__(self, max_locations, urban_map):
        self.urban_map = urban_map
        self.max_locations = max_locations
        self.height = len(urban_map)
        self.width = len(urban_map[0])

        self.cost_key_map = []
        self.key_indus_dict = {}
        self.key_comm_dict = {}
        self.key_resi_dict = {}
        self.locations_x = []
        self.locations_s = []
        self.locations_s_master = []

        self.max_population = 1
        self.elitism_percent = 10
        self.culling_percent = 10
        self.mutation_percent = 10

    def getXS(self):
        self.locations_x = np.where(self.urban_map == 'X')
        self.locations_x = np.transpose(self.locations_x)

        self.locations_s = np.where(self.urban_map == 'S')
        self.locations_s = np.transpose(self.locations_s)
        self.locations_s = np.array(self.locations_s)
        self.locations_s_master = deepcopy(self.locations_s)

    def solve(self):
        self.getXS()
        self.overwriteSceneLocation()
        for _ in range(len(self.cost_key_map), self.max_population):
            unique_id = uuid.uuid4().hex[:8]
            for i in range(3):
                self.fillLocations(unique_id, i)
            cost = self.getCostMap(unique_id)
            self.locations_s = deepcopy(self.locations_s_master)
            self.printCity(unique_id)
            print("total cost: ", self.cost_key_map)

    def fillLocations(self, key, icr):
        loc_i = []
        no_of_loc = random.randint(0, self.max_locations[icr])
        for _ in range(no_of_loc):
            self.getRowCol(loc_i, icr)
        icr_dict = self.getICR(icr)
        icr_dict[key] = loc_i

    def getRowCol(self, loc_i, icr):
        row = random.randint(0, self.height-1)
        col = random.randint(0, self.width-1)
        if (np.all(self.locations_x == [row, col], 1)).any():
            self.getRowCol(loc_i, icr)
            return
        elif len(loc_i) != 0:
            if len(loc_i) == 1:
                if loc_i[0][0] == row and loc_i[0][1] == col:
                    self.getRowCol(loc_i, icr)
                    return
            else:
                if(np.all(loc_i == [row, col], 1)).any():
                    self.getRowCol(loc_i, icr)
                    return
        elif (np.all(self.locations_s == [row, col], 1)).any():
            for i in range(len(self.locations_s)):
                if self.locations_s[i][0] == row and self.locations_s[i][1] == col:
                    self.locations_s = np.delete(self.locations_s, i, 0)
        loc_i.append([row, col])

    def getCostMap(self, key):
        cost = 0
        for i in range(3):
            cost += self.getBuildCost(key, i)

        self.cost_key_map.append([cost, key])
        return cost

    def getBuildCost(self, key, icr):
        a = self.getICR(icr)
        locations = a[key]
        build_cost = 2
        total_cost = 0
        for locn in locations:
            location_cost = int(self.urban_map[int(locn[0]), int(locn[1])])
            total_cost += build_cost + location_cost

        return total_cost

    def getICR(self, icr):
        if icr == 0:
            return self.key_indus_dict
        elif icr == 1:
            return self.key_comm_dict
        elif icr == 2:
            return self.key_resi_dict

    def overwriteSceneLocation(self):
        for s in self.locations_s_master:
            self.urban_map[s[0], s[1]] = '1'

    def printCity(self, key):
        print(self.urban_map)
        print(self.key_indus_dict[key])
        print(self.key_comm_dict[key])
        print(self.key_resi_dict[key])
        # print("\n\n")

        print_copy = deepcopy(self.urban_map)

        for scn in self.locations_s_master:
            print_copy[scn[0], scn[1]] = 'S'
        for ind in self.key_indus_dict[key]:
            print_copy[ind[0], ind[1]] = 'I'
        for com in self.key_comm_dict[key]:
            print_copy[com[0], com[1]] = 'C'
        for resi in self.key_resi_dict[key]:
            print_copy[resi[0], resi[1]] = 'R'

        # print(print_copy)
        # print("\n\n")
