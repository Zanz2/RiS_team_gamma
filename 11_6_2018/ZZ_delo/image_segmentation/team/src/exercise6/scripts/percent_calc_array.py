#!/usr/bin/env python

import sys
def return_percent(minimal,maximal,value):
	minimal = float(minimal)
	maximal = float(maximal)
	value = float(value)
	return_value = ((value - minimal) * 100) / (maximal - minimal)
	print(return_value)
	return return_value
#min_array =[-1.91999995708, -0.319999992847, -2.5,-1.48000001907,-2.27999997139, -0.40000000596]
#max_array=[1.60000002384, 2.75999999046, 0.97000002861, 1.52999997139, 1.21000003815,1.01999998093]

min_array =[-1.64999997616, -0.340000003576, -2.47000002861, -1.60000002384, -2.3599998951, -0.230000004172]
max_array=[1.67999994755, 2.78999996185, 0.899999976158, 1.59000003338, 1.12999999523, 1.19000005722]

#positions_array=[
#		[-1.6, 3, 1, 1, 0, -1],
#		[-1.55, 1, -1.4, -1, 0, -1],
#		[-1.55, 1, -1.4, -1, 0, 2],
#		[0, 0, 1, -1, 0, 2],
#		[0, 0, 1, -1, 0, -1]
#	]

positions_array=[
			[-1, 3, -3, -1, 0, 0],
			[-2, 3, -3, -1, 0, 0],
			[-2, 1.45, -1.6, -1.3, 0, 0],
			[-2, 1.45, -1.6, -1.3, 0, 3],
			[-2, 2.5, -1.6, -1.3, 0, 3],
			[-0.5, 0.5, 0, -1, 0, 3],
			[-0.5, 0.5, 0, -1, 0, 0],
			[-1.18, 3, -1.6, -1, 0, 0],
			[-1.18, 1.45, -1.6, -1.3, 0, 0],
			[-1.18, 1.45, -1.6, -1.3, 0, 3],
			[-1.18, 2.5, -1.6, -1.3, 0, 3],
			[-0.5, 0.5, 0, -1, 0, 3],
			[-0.5, 0.5, 0, -1, 0, 0],
			[-0.5, 3, -1.6, -1.3, 0, 0],
			[-0.8, 1.45, -1.6, -1.3, 0, 0],
			[-0.8, 1.45, -1.6, -1.3, 0, 3],
			[-0.8, 2.5, -1.6, -1.3, 0, 3],
			[-0.5, 0.5, 0, -1, 0, 3],
			[-0.5, 0.5, 0, -1, 0, 0],
			[-1, 3, -3, -1, 0, 0]
		]


percentage_array = [
			[0, 0, 0, 0, 0, 0], 
			[0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0], 
			[0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0], 
			[0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0], 
			[0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0],
			[0, 0, 0, 0, 0, 0]
			]
		

for element in range(6):
	#print(element)
	for row in range(20):
		print(element)
		print(min_array[element])
		print(max_array[element])
		print(positions_array[row][element])
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
