#!/usr/bin/env python

import sys
minimal = float(sys.argv[1])
maximal = float(sys.argv[2])
value = float(sys.argv[3])
return_value = ((value - minimal) * 100) / (maximal - minimal)
print(return_value)
