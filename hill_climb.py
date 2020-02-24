from copy import copy, deepcopy
import time
import random
import numpy as np
import math

class HillClimb:
    def __init__(self, sites, terrain):
        self.sites = sites
        self.terrain = deepcopy(terrain)
        S=[]
        X=[]
        for i,x in enumerate(self.terrain):
        	for j,y in enumerate(x):
        		if y=="S":
        			S.append([i,j])
        		if y=="X":
        			X.append([i,j])
        self.S=S
        self.X=X
        self.I=[]
        self.R=[]
        self.C=[]
   # Function for generating random zone positions
    def place(self,maxnum,site):
    	num=random.randint(0,maxnum-1)

    	itr=0
    	while(itr<num):
    		i=random.randint(0,len(self.terrain)-1)
    		j=random.randint(0,len(self.terrain[0])-1)
    		if ([i,j] in self.I) or ([i,j] in self.R) or ([i,j] in self.C) or ([i,j] in self.X):
    			continue
    		site.append([i,j])
    		itr+=1
    # Function to get the neighbourhood of a site
    def neighbourhood(self,i,j,n):
    	if n==2:
    		return [[i+1,j],[i+1,j+1],[i+1,j-1],[i,j+1],[i+1,j-1],[i-1,j+1],[i-1,j-1],[i-1,j],[i+2,j],[i-2,j],[i,j+2],[i,j-2]]
    	else:
    		return [[i+1,j],[i+1,j+1],[i+1,j-1],[i,j+1],[i+1,j-1],[i-1,j+1],[i-1,j-1],[i-1,j],[i+2,j],[i-2,j],[i,j+2],[i,j-2],[i+3,j],[i-3,j],[i,j+3],[i,j-3],[i+2,j+1],[i-2,j+1],[i+2,j-1],[i-2,j-1],[i+1,j+2],[i-1,j+2],[i+1,j-2],[i-1,j+2]]
    
    # Function to draw the map
    def draw_map(self,I,R,C,terrain):
   		map_terrain=deepcopy(terrain)
   		for i,j in I:
   			map_terrain[i][j]="I"
   		for i,j in R:
   			map_terrain[i][j]="R"
   		for i,j in C:
   			map_terrain[i][j]="C"
   		return map_terrain

   	# Function to calculate the score of the map
    def map_cost(self,I,R,C,S,X,terrain):
    	cost=0
    	for index, cord in enumerate(I):
    		if cord not in S:
    			cost=cost+2+int(terrain[cord[0]][cord[1]])
    		temp = deepcopy(I)
    		temp.pop(index)
    		for x,y in temp:
    			neighbourhood=self.neighbourhood(x,y,2)
    			if cord in neighbourhood:
    				cost=cost-2
    		for x,y in R:
    			neighbourhood=self.neighbourhood(x,y,3)
    			if cord in neighbourhood:
    				cost=cost+5

    	for index, cord in enumerate(C):
    		if cord not in S:
    			cost=cost+2+int(terrain[cord[0]][cord[1]])
    		temp = deepcopy(C)
    		temp.pop(index)
    		for x,y in temp:
    			neighbourhood=self.neighbourhood(x,y,2)
    			if cord in neighbourhood:
    				cost=cost+4
    		for x,y in R:
    			neighbourhood=self.neighbourhood(x,y,3)
    			if cord in neighbourhood:
    				cost=cost-4

    	for i,j in C:
    		if [i,j] not in S:
    			cost=cost+2+int(terrain[i][j])

    	for i,j in S:
    		if [i,j] in I+R+C:
    			cost= cost+1
    			continue
    		n=self.neighbourhood(i,j,2)
    		for x,y in R:
    			if [x,y] in n:
    				cost=cost-10
    	for i,j in X:
    		n=self.neighbourhood(i,j,2)
    		for x,y in I:
    			if [x,y] in n:
    				cost= cost+10
    		for x,y in R+C:
    			if [x,y] in n:
    				cost=cost+20

    	return cost

    # Function to get the neighbourhood information of a configuration
    def move_list(self):
    	move_log=[]
    	for i in range(len(self.terrain)):
    		for j in range(len(self.terrain[0])):
    			for t in range(len(self.I)):
    				if ([i,j] in self.I) or ([i,j] in self.R) or ([i,j] in self.C) or ([i,j] in self.X):
    					continue
    				val = self.I[t]
    				self.I[t]=[i,j]
    				cost=self.map_cost(self.I,self.R,self.C,self.S,self.X,self.terrain)
    				map_terrain=self.draw_map(self.I,self.R,self.C,self.terrain)
    				move_log.append(deepcopy([self.I,self.R,self.C,map_terrain,cost]))
    				self.I[t]=val

    			for t in range(len(self.R)):
    				if ([i,j] in self.I) or ([i,j] in self.R) or ([i,j] in self.C) or ([i,j] in self.X):
    					continue
    				val = self.R[t]
    				self.R[t]=[i,j]
    				cost=self.map_cost(self.I,self.R,self.C,self.S,self.X,self.terrain)
    				map_terrain=self.draw_map(self.I,self.R,self.C,self.terrain)
    				move_log.append(deepcopy([self.I,self.R,self.C,map_terrain,cost]))
    				self.R[t]=val
    			for t in range(len(self.C)):
    				if ([i,j] in self.I) or ([i,j] in self.R) or ([i,j] in self.C) or ([i,j] in self.X):
    					continue
    				val = self.C[t]
    				self.C[t]=[i,j]
    				cost=self.map_cost(self.I,self.R,self.C,self.S,self.X,self.terrain)
    				map_terrain=self.draw_map(self.I,self.R,self.C,self.terrain)
    				move_log.append(deepcopy([self.I,self.R,self.C,map_terrain,cost]))
    				self.C[t]=val
    	return move_log
    
    # Function to get the temperature which decays over time
    def cooldown(self,elapsed_time):
    	a=1
    	r=0.9
    	return a*(1-r)**(elapsed_time)

    # Function to calculate the probability of chosing a configuration
    def annealingProb(self,error,temp):
    	return math.e**(error/temp)

   	# Function to get the random restarts
    def random_restart(self):
    	# Random Initialization of the map
    	self.I=[]
    	self.R=[]
    	self.C=[]
    	self.place(self.sites[0],self.I)
    	self.place(self.sites[1],self.C)
    	self.place(self.sites[2],self.R)
    	# Finding the cost and drawing the map for initial configuration
    	start_cost=self.map_cost(self.I,self.R,self.C,self.S,self.X,self.terrain)
    	map_terrain=self.draw_map(self.I,self.R,self.C,self.terrain)
    	return start_cost,map_terrain

    # Function to perform simulated annealing
    def simulated_annealing(self,start_time,restart_time,start_cost,map_terrain,cost_list,map_list,time_list,time_limit):
    	# Starting the simulated Annealing
    	t=True
    	restart_time=time.time()
    	while(t):
    		
    		# Getting the neighbourhood of the initial configuration
    		move_log=self.move_list()
    		
    		# Checking the elapsed time
    		elapsed_time = time.time() - restart_time

    		# Setting the temperature for annealing
    		temp = self.cooldown(elapsed_time)

    		#Defining the time for each annealing run
    		if elapsed_time >time_limit/40:
    			t=False
    			break

    		# Chosing a random configuration from the neighbourhood
    		i=random.randint(0,len(move_log)-1)
    		possible_map = move_log[i]
    		possible_cost=possible_map[4]

    		# Checking the difference in the cost between the prospective and current configuration
    		error= start_cost - possible_cost

    		# If error is positive, Therefore the configuration is definitely better. Hence we move to it 
    		if error>0:
    			self.I=possible_map[0]
    			self.R=possible_map[1]
    			self.C=possible_map[2]
    			map_terrain=self.draw_map(self.I,self.R,self.C,self.terrain)
    			start_cost=possible_cost

    		# If error is not positive, we will use probablity to move to next configuration
    		else:
    			probablilty=self.annealingProb(error,temp)
    			if random.randint(0,100) < probablilty*100:
    				self.I=possible_map[0]
    				self.R=possible_map[1]
    				self.C=possible_map[2]
    				map_terrain=self.draw_map(self.I,self.R,self.C,self.terrain)
    				start_cost=possible_cost
    	# Gathering the costs and maps obtained after each random run
    	cost_list.append(start_cost)
    	map_list.append(map_terrain)
    	time_list.append(time.time()-start_time)
    # Function to solve the planning problem
    def solve(self):
    	start_time=time.time()
    	cost_list=[]
    	map_list=[]
    	time_list=[]
    	time_limit=10
    	while(time.time()-start_time<time_limit):
    		start_cost,map_terrain=self.random_restart()
    		if start_cost==0:
    			continue
    		restart_time=time.time()
    		self.simulated_annealing(start_time,restart_time,start_cost,map_terrain,cost_list,map_list,time_list,time_limit)
		

		################################
		####### PRINTING RESULTS #######
		################################    	

    	print("The Score of the map generated is: ",-1*min(cost_list))
    	itr=0
    	for i,j in enumerate(cost_list):
    		if itr==1:
    			continue
    		if j==min(cost_list):
    			print("The Time from start at which it was achieved: %0.2f Seconds"%time_list[i])
    			print("The Required map is: ")
    			for x in map_list[i]:
    				print(x)
    			itr=1
