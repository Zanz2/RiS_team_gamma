#!/usr/bin/env python

import sys
def return_percent(minimal,maximal,value):
	minimal = float(minimal)
	maximal = float(maximal)
	value = float(value)
	return_value = ((value - minimal) * 100) / (maximal - minimal)
	print(return_value)
	return return_value
min_array =[-1.91999995708, -0.319999992847, -2.5,-1.48000001907,-2.27999997139, -0.40000000596]
max_array=[1.60000002384, 2.75999999046, 0.97000002861, 1.52999997139, 1.21000003815,1.01999998093]
positions_array=[
		[-1.6, 3, 1, 1, 0, -1],
		[-1.55, 1, -1.4, -1, 0, -1],
		[-1.55, 1, -1.4, -1, 0, 2],
		[0, 0, 1, -1, 0, 2],
		[0, 0, 1, -1, 0, -1]
	]


percentage_array = [
			[0, 0, 0, 0, 0, 0], 
			[0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0]
			]
		

for element in range(6):
	#print(element)
	for row in range(5):
		#print(row)
		value_to_input = return_percent(min_array[element],max_array[element],positions_array[row][element])
		if(value_to_input<0):
			value_to_input = 0
		if(value_to_input>100):
			value_to_input = 100
		
		print(value_to_input)
		print("---")		
		percentage_array[row][element] = float(value_to_input)
		print(element)
		print(row)
		print("==")

print(percentage_array)
