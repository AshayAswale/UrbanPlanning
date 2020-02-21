import sys
import numpy as np
import random
from genetic_algo import GeneticAlgo


def getUrbanMap(argv):
    urban_file = open(argv[0])
    text_from_file = urban_file.readlines()
    urban_map = []

    for i in range(3, len(text_from_file)):
        text_from_file[i] = text_from_file[i].replace('\r', '')
        text_from_file[i] = text_from_file[i].replace('\n', '')
        urban_map.append(text_from_file[i].split(","))

    return np.array(urban_map)


def getMaxLocations(argv):
    urban_file = open(argv[0])
    text_from_file = urban_file.readlines()
    max_locations = []
    for i in range(3):
        max_locations.append(int(text_from_file[i][0]))

    return np.array(max_locations)


def main(argv):
    if len(argv) != 2:
        print("Please enter file to read in followed by Algorithm. e.g. --> \n\npython main.py plan map.txt GA")
        exit()

    urban_map = getUrbanMap(argv)
    max_locations = getMaxLocations(argv)

    if argv[1] == "GA":
        gent = GeneticAlgo(max_locations, urban_map)
        gent.solve()
        pass
    elif argv[1] == "HC":
        pass
    else:
        print("Please enter \nGA: Genetic Algorithm \nHC: Hill Climb")


if __name__ == "__main__":
    main(sys.argv[1:])
