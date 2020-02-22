import sys
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

        self.points_key_map = []
        self.key_indus_dict = {}
        self.key_comm_dict = {}
        self.key_resi_dict = {}
        self.locations_x = []
        self.locations_s = []
        self.locations_s_master = []

        self.max_population = 10
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
        self.pupulate()
        print("Sorted Points: ", self.points_key_map)
        self.crossover(self.points_key_map[0][1], self.points_key_map[1][1])
        # self.printCity(self.points_key_map[0][1])
        # self.printCity(self.points_key_map[1][1])
        # print("Sorted Points: ", self.points_key_map)

    def pupulate(self):
        for _ in range(len(self.points_key_map), self.max_population):
            unique_id = uuid.uuid4().hex[:8]
            for i in range(3):
                self.fillLocations(unique_id, i)
            points = self.getPointsMap(unique_id)
            self.points_key_map.append([points, unique_id])
            self.locations_s = deepcopy(self.locations_s_master)
            # self.printCity(unique_id)
        self.points_key_map.sort(reverse=True)

    def fillLocations(self, key, icr):
        loc_i = []
        no_of_loc = random.randint(0, self.max_locations[icr])
        # no_of_loc = self.max_locations[icr]
        for _ in range(no_of_loc):
            self.getRowCol(loc_i, key, icr)
            # self.getMyRowCol(loc_i, icr)
        icr_dict = self.getICR(icr)
        icr_dict[key] = loc_i

    def getRowCol(self, loc_i, key, icr):
        row = random.randint(0, self.height-1)
        col = random.randint(0, self.width - 1)
        for i in range(3):
            if key in self.getICR(i):
                rest_loc = self.getICR(i)[key]
                for locs in rest_loc:
                    if locs[0] == row and locs[1] == col:
                        self.getRowCol(loc_i, key, icr)
                        return

        if (np.all(self.locations_x == [row, col], 1)).any():
            self.getRowCol(loc_i, key, icr)
            return
        elif len(loc_i) != 0:
            for prev_loc in loc_i:
                if prev_loc[0] == row and prev_loc[1] == col:
                    self.getRowCol(loc_i, key, icr)
                    return
        elif (np.all(self.locations_s == [row, col], 1)).any():
            for i in range(len(self.locations_s)):
                # Kuch to panga hai
                if self.locations_s[i][0] == row and self.locations_s[i][1] == col:
                    self.locations_s = np.delete(self.locations_s, i, 0)
                    break
        loc_i.append([row, col])

    def getMyRowCol(self, loc_i, icr):
        if icr == 0:
            row = 0
            col = 3
        elif icr == 1:
            row = 2
            col = 2
        else:
            row = 2
            col = 1
        loc_i.append([row, col])

    def getPointsMap(self, key):
        points = 0
        for i in range(3):
            points -= self.getBuildCost(key, i)
            points += self.getNeighbourPoints(key, i)
        return points

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
        # print(self.urban_map)
        # print(self.key_indus_dict[key])
        # print(self.key_comm_dict[key])
        # print(self.key_resi_dict[key])
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

        print(print_copy)
        print("\n")

    def getNeighbourPoints(self, key, icr):
        currentTile = self.getICR(icr)
        locations = currentTile[key]
        points = 0

        points += self.getXcost(locations, icr)
        points += self.getScost(locations, icr)

        if icr == 0:
            points += self.getIcost(locations, key, icr)
        elif icr == 1:
            points += self.getCcost(locations, key, icr)
        else:
            # if icr == 1:
            points += self.getRcost(locations, key, icr)
        return points

    def countXinVicinity(self, pos):
        vicinity_count = 0
        for X in self.locations_x:
            for P in pos:
                manh_dist = self.getManhDist(X, P)
                if manh_dist <= 2:
                    vicinity_count += 1
        return vicinity_count

    def getXcost(self, pos, icr):
        points = 0
        cost = -10 if icr == 0 else -20
        X_vicnt = self.countXinVicinity(pos)
        if X_vicnt > 0:
            points += X_vicnt * cost
        return points

    def getScost(self, pos, icr):
        points = 0
        cost = 10 if icr == 2 else 0
        S_vicnt = self.countSinVicinity(pos)
        if S_vicnt > 0:
            points += S_vicnt * cost
        return points

    def getIcost(self, pos, key, icr):
        points = 0
        if len(pos) == 1:
            return 0

        for i in range(len(pos)):
            for j in range(i+1, len(pos)):
                manh_dist = self.getManhDist(pos[i], pos[j])
                if manh_dist <= 2:
                    points += 2
        return points

    def getCcost(self, com_pos, key, icr):
        points = 0
        resi_pos = self.getICR(2)[key]

        for i in range(len(com_pos)):
            for j in range(len(resi_pos)):
                manh_dist = self.getManhDist(com_pos[i], resi_pos[j])
                if manh_dist <= 3:
                    points += 8     # We are not adding while analyzing Residential. Hence adding double here

        if len(com_pos) > 1:
            for i in range(len(com_pos)):
                for j in range(i+1, len(com_pos)):
                    manh_dist = self.getManhDist(com_pos[i], com_pos[j])
                    if manh_dist <= 2:
                        points += -4
        return points

    def getRcost(self, resi_pos, key, icr):
        points = 0
        indus_pos = self.getICR(0)[key]

        for i in range(len(indus_pos)):
            for j in range(len(resi_pos)):
                manh_dist = self.getManhDist(indus_pos[i], resi_pos[j])
                if manh_dist <= 3:
                    points += -5

        return points

    @staticmethod
    def getManhDist(pos_1, pos_2):
        row_dist = pos_1[0] - pos_2[0]
        col_dist = pos_1[1] - pos_2[1]
        manh_dist = abs(row_dist) + abs(col_dist)
        return manh_dist

    def countSinVicinity(self, pos):
        vicinity_count = 0
        for S in self.locations_s:
            for P in pos:
                manh_dist = self.getManhDist(S, P)
                if manh_dist <= 2:
                    vicinity_count += 1
        return vicinity_count

    def crossover(self, key_1, key_2, new=False):
        list_1 = []
        list_2 = []
        for i in range(3):
            for locs in self.getICR(i)[key_1]:
                list_1.append([i, locs[0], locs[1]])
            for locs in self.getICR(i)[key_2]:
                list_2.append([i, locs[0], locs[1]])
        min_ct = int(len(list_1)/2)
        for _ in range(min_ct)
            rand = random.randint(0,len(list_1))
            temp_1 = list_1.pop(rand)
            icr = temp[0]
            for i in range(len(list_2))
                
