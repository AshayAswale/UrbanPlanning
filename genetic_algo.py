import sys
import numpy as np
from copy import deepcopy
import random
import uuid
import time

"""
In this code the ICR stands for Industrial Commertial and Residential regions
The ICR values are hardcoded as:
0 - Industrial 
1 - Commertial
2 - Residential

Also when there is a variable named icr, that variable has the value of 
which location is to be considered amongs these 3 values.
"""
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

        self.max_population = 100
        self.elitism_percent = 10
        self.culling_percent = 5
        self.mutation_percent = 10
        self.time_achieved = 0.0


    def solve(self):
        """
        The calling function to solve the map problem
        """
        # First create a list of all the X and S in the map
        self.getXS()

        # For solving purpose, consider all the S as Location Value 1
        self.overwriteSceneLocation()

        # Populate the map with the locations at random blocks
        self.populate()
        print("First Generation Best Points: ", self.points_key_map[0][0])
        
        # Start the genetic algorithm code
        self.startGenetics()

        # Print the final solution for the solving
        self.printResults()

    def getXS(self):
        """
        Creates a list of X and S in the urban map
        """
        self.locations_x = np.where(self.urban_map == 'X')
        self.locations_x = np.transpose(self.locations_x)

        self.locations_s = np.where(self.urban_map == 'S')
        self.locations_s = np.transpose(self.locations_s)
        self.locations_s = np.array(self.locations_s)
        self.locations_s_master = deepcopy(self.locations_s)

    def overwriteSceneLocation(self):
        """
        overwrites the S in map with its cost of location
        """
        for s in self.locations_s_master:
            self.urban_map[s[0], s[1]] = '1'


#############################################
#### P O P U L A T I N G   T H E   M A P ####
#############################################

    def populate(self):
        """
        Populate the map with randomly generated locations
        """
        for _ in range(len(self.points_key_map), self.max_population):
            count = 0

            # Each location is stored with its own unique ID. The locations
            # are traced back with this unique ID only
            unique_id = uuid.uuid4().hex[:8]
            for i in range(3):
                self.fillLocations(unique_id, i)
                count += len(self.getICR(i)[unique_id])
            if count == 0:
                loc_i = []
                self.getRowCol(loc_i, unique_id, random.randint(0, 2))
            points = self.getPointsMap(unique_id)
            self.points_key_map.append([points, unique_id])
            # self.printCity(unique_id)
        self.points_key_map.sort(reverse=True)

    def fillLocations(self, key, icr):
        """
        For a given structure, generate a location from the map
        """
        loc_i = []
        no_of_loc = random.randint(0, self.max_locations[icr])
        no_of_loc = self.max_locations[icr]
        for _ in range(no_of_loc):
            self.getRowCol(loc_i, key, icr)
            # self.getMyRowCol(loc_i, icr)
        icr_dict = self.getICR(icr)
        icr_dict[key] = loc_i

    def getRowCol(self, loc_i, key, icr):
        """
        Generate a new location where:
            There is no X
            If overwrites S, then delete S
            There is no other site present already
        """
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
        if (np.all(self.locations_s == [row, col], 1)).any():
            self.getRowCol(loc_i, key, icr)
            return
        elif len(loc_i) != 0:
            for prev_loc in loc_i:
                if prev_loc[0] == row and prev_loc[1] == col:
                    self.getRowCol(loc_i, key, icr)
                    return
        # elif (np.all(self.locations_s == [row, col], 1)).any():
        #     for i in range(len(self.locations_s)):
        #         # Kuch to panga hai
        #         if self.locations_s[i][0] == row and self.locations_s[i][1] == col:
        #             self.locations_s = np.delete(self.locations_s, i, 0)
        #             break
        loc_i.append([row, col])

    def getMyRowCol(self, loc_i, icr):
        """
        Function to be used for testing purpose. 
        It will pop-up the locations at given position.
        """
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

#############################################
###### C O S T   C A L C U L A T I O N ######
#############################################

    def getPointsMap(self, key):
        """
        Calculates and returns the Points of the map
        """
        points = 0
        for i in range(3):
            # Get the cost for building the site at the given locations
            points -= self.getBuildCost(key, i)
            
            # Get the points scored due to the neighbouring criteria
            points += self.getNeighbourPoints(key, i)
        return points

    def getBuildCost(self, key, icr):
        """
        Returns the cost of building a site at the given location 
        """
        a = self.getICR(icr)
        locations = a[key]
        build_cost = 2
        total_cost = 0
        for locn in locations:
            location_cost = int(self.urban_map[int(locn[0]), int(locn[1])])
            total_cost += build_cost + location_cost

        return total_cost

    def getNeighbourPoints(self, key, icr):
        """
        Returns the points scored due to the neighbouring criteria
        """
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
            points += self.getRcost(locations, key, icr)
        return points

    def getXcost(self, pos, icr):
        """
        Returns the points to be deducted due to vicinity of nuclear site
        """
        points = 0
        cost = -10 if icr == 0 else -20
        X_vicnt = self.countXinVicinity(pos)
        if X_vicnt > 0:
            points += X_vicnt * cost
        return points

    def countXinVicinity(self, pos):
        """
        Returns the number of Nuclear sites in the vicinity of the location
        """
        vicinity_count = 0
        for X in self.locations_x:
            for P in pos:
                manh_dist = self.getManhDist(X, P)
                if manh_dist <= 2:
                    vicinity_count += 1
        return vicinity_count

    def getScost(self, pos, icr):
        """
        Returns the points to be scored due to vicinity of the Scenic location
        """
        points = 0
        cost = 10 if icr == 2 else 0
        S_vicnt = self.countSinVicinity(pos)
        if S_vicnt > 0:
            points += S_vicnt * cost
        return points

    def countSinVicinity(self, pos):
        """
        Returns the points scored due to vicinity to the Scenic location
        """
        vicinity_count = 0
        for S in self.locations_s:
            for P in pos:
                manh_dist = self.getManhDist(S, P)
                if manh_dist <= 2:
                    vicinity_count += 1
        return vicinity_count

    def getIcost(self, pos, key, icr):
        """
        Returns the points scored by the Industrial sites in the map
        """
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
        """
        Returns the points scored by the Commercial sites in the map
        """
        points = 0
        resi_pos = self.getICR(2)[key]

        # Points due to vicinity to Residential Locations
        for i in range(len(com_pos)):
            for j in range(len(resi_pos)):
                manh_dist = self.getManhDist(com_pos[i], resi_pos[j])
                if manh_dist <= 3:
                    points += 8     # We are not adding while analyzing Residential. Hence adding double here

        # Points deducted due to competition. 
        if len(com_pos) > 1:
            for i in range(len(com_pos)):
                for j in range(i+1, len(com_pos)):
                    manh_dist = self.getManhDist(com_pos[i], com_pos[j])
                    if manh_dist <= 2:
                        points += -4
        return points

    def getRcost(self, resi_pos, key, icr):
        """
        Returns the points scored by the Residential locations 
        """
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
        """
        Returns the Manhattan distance of two given locations
        """
        row_dist = pos_1[0] - pos_2[0]
        col_dist = pos_1[1] - pos_2[1]
        manh_dist = abs(row_dist) + abs(col_dist)
        return manh_dist

#############################################
##### G E N E T I C   A L G O R I T H M #####
#############################################

    def startGenetics(self):
        """
        Starts the code for Genetic Algorithm
        """
        start_time = time.time()

        elitism = self.getFraction(self.elitism_percent)
        culling = self.getFraction(self.culling_percent)
        elitism_keys = []
        best_score = 0
        while time.time() - start_time < 10:
            self.points_key_map.sort(reverse=True)
            if best_score != self.points_key_map[0][0]:
                best_score = self.points_key_map[0][0]
                self.time_achieved = time.time() - start_time
            self.getElites(elitism_keys, elitism)
            self.culling(culling)
            self.replicateAndDelete(elitism)
            self.mutation()


    def crossover(self, key_1, key_2):
        """
        Generates the children from the two parents taken as the input.
        Returns the keys of newly generated children
        """
        list_1 = []
        list_2 = []
        for i in range(3):
            list_1.append(self.getICR(i)[key_1])
            list_2.append(self.getICR(i)[key_2])

        child_key_1 = uuid.uuid4().hex[:8]
        child_key_2 = uuid.uuid4().hex[:8]

        rand_icr = random.randint(0, 2)

        self.overlapDeletion(list_1, list_2, rand_icr)

        self.swapListElements(list_1, list_2, rand_icr)

        self.makeEntry(list_1, child_key_1)
        self.makeEntry(list_2, child_key_2)
        return [child_key_1, child_key_2]

    def overlapDeletion(self, list_1, list_2, rand_icr):
        """
        During crossover, if one location is overlapping the other location,
        We override the location with the incomming location.
        """
        self.overlapDeleteFix(list_1, list_2, rand_icr)
        self.overlapDeleteFix(list_2, list_1, rand_icr)

    def overlapDeleteFix(self, list_1, list_2, rand_icr):
        """
        During crossover, if one location is overlapping the other location,
        We override the location with the incomming location.
        """
        poppop = []
        al = [0, 1, 2]
        al.pop(rand_icr)

        for coming in list_2[rand_icr]:
            breakout = False
            for icr_s in al:
                for basic in list_1[icr_s]:
                    row_same = basic[0] == coming[0]
                    col_same = basic[1] == coming[1]
                    if row_same and col_same:
                        poppop.append([icr_s, basic])
                        breakout = True
                        break
                if breakout:
                    break

        for delt in poppop:
            list_1[delt[0]].remove(delt[1])

    @staticmethod
    def swapListElements(list_1, list_2, rand_icr):
        """
        Swaps the content of two incoming lists
        """
        temp = list_1[rand_icr]
        list_1[rand_icr] = list_2[rand_icr]
        list_2[rand_icr] = temp

    def makeEntry(self, list_1, key):
        """
        Registers the new location of ICR into directory
        """
        self.key_indus_dict[key] = list_1[0]
        self.key_comm_dict[key] = list_1[1]
        self.key_resi_dict[key] = list_1[2]

        points = self.getPointsMap(key)
        self.points_key_map.append([points, key])

    def deleteChild(self, key, del_from_map=True):
        """
        Delete the given child from the existance
        """
        del self.key_indus_dict[key]
        del self.key_comm_dict[key]
        del self.key_resi_dict[key]

        if del_from_map:
            for i in range(len(self.points_key_map)):
                if self.points_key_map[i][1] == key:
                    self.points_key_map.pop(i)
                    break

    def culling(self, culling):
        """
        Performs culling to bring the population down
        """
        desired_pop = self.max_population - culling

        # Perform culling while the desired population is reached
        while (len(self.points_key_map)-desired_pop) > 0:
            key = self.points_key_map[-1][1]
            self.deleteChild(key, False)
            del self.points_key_map[-1]

    def getElites(self, elitism_keys, elitism):
        """
        Keep the record of elites
        """
        elitism_keys = []
        for i in range(elitism):
            elitism_keys.append(self.points_key_map[i][1])

    def getFraction(self, percent):
        """
        Returns the integer value of the fraction of value
        """
        fraction = int(self.max_population * (percent / 100))
        return fraction if fraction > 0 else 1

    def replicateAndDelete(self, elitism):
        """
        Generate new child from existing parents, then delete the parents
        """
        mid = int((len(self.points_key_map) - elitism) / 2)
        mid = elitism + mid
        for i in range(0, elitism):
            self.crossover(
                self.points_key_map[i][1], self.points_key_map[i + 1][1])
        for i in range(elitism, mid, 2):

            self.crossover(
                self.points_key_map[i][1], self.points_key_map[i + 1][1])
            self.deleteChild(self.points_key_map[i][1])
            self.deleteChild(self.points_key_map[i + 1][1])

    def mutation(self):
        """
        Performs the mutation
        """
        curr_pop = len(self.points_key_map)
        deficit = self.max_population - curr_pop
        if deficit > 0:
            for i in range(deficit):
                child_keys = self.crossover(
                    self.points_key_map[i][1], self.points_key_map[i + 1][1])
                self.mutate(child_keys[0])
                self.mutate(child_keys[1])
                curr_pop = len(self.points_key_map)
                deficit = self.max_population - curr_pop

    def mutate(self, key):
        """
        Changes random element from the list of location of the newly generated child
        """
        icr_rand = random.randint(0, 2)
        row_col = []
        icr = self.getICR(icr_rand)
        self.getRowCol(row_col, key, icr_rand)
        icr[key][0] = row_col[0]

    def getICR(self, icr):
        """
        Returns the dictionary of locations for requested icr
        """
        if icr == 0:
            return self.key_indus_dict
        elif icr == 1:
            return self.key_comm_dict
        elif icr == 2:
            return self.key_resi_dict


#############################################
###### P R I N T I N G   R E S U L T S ######
#############################################

    def printCity(self, key):
        """
        Prints the city map for the given key
        """

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


    def printResults(self):
        """
        Prints the results as required by the assignment
        """
        print("Solved Best Points: ", self.points_key_map[0][0])
        print("Time at which best score was achieved: ", self.time_achieved)
        self.printCity(self.points_key_map[0][1])
