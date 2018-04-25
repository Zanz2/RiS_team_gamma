
#!/usr/bin/env python

import sys
def return_value(minimal,maximal,percentage):
	minimal = float(minimal)
	maximal = float(maximal)
	percentage = float(percentage)
	print("range "+str(minimal)+" to "+str(maximal)+" with percent "+str(percentage))

	return_val = float((float(percentage) * float(maximal - minimal) / float(100)) + float(minimal))
	#print(float(percentage) * float(maximal - minimal)/ float(100))
	#print(float(minimal))
	#print(float(percentage) * float(maximal - minimal)/ float(100) + float(minimal))
	print(return_val)
	return return_val

min_array =[-1.64999997616, -0.340000003576,-2.47000002861,-1.60000002384,-2.3599998951 ,-0.230000004172]
max_array=[1.67999994755, 2.78999996185, 0.899999976158, 1.59000003338, 1.12999999523,1.19000005722]
percentage_array=[[9.090907920867759, 100.0, 100.0, 82.39202747276411, 65.32951189563222, 0.0], [10.511362474021814, 42.85714285717996, 31.70028792307054, 15.946844537917906, 65.32951189563222, 0.0], [10.511362474021814, 42.85714285717996, 31.70028792307054, 15.946844537917906, 65.32951189563222, 100.0], [54.54545362179752, 10.389610213679793, 100.0, 15.946844537917906, 65.32951189563222, 100.0], [54.54545362179752, 10.389610213679793, 100.0, 15.946844537917906, 65.32951189563222, 0.0]]


value_array = [
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
		value_array[row][element] = return_value(min_array[element],max_array[element],percentage_array[row][element])
	
print(value_array)
