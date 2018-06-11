
#!/usr/bin/env python

import sys
minimal = float(sys.argv[1])
maximal = float(sys.argv[2])
percentage = float(sys.argv[3])

return_val = ((percentage * (maximal - minimal) / 100) + minimal)
print(return_val)
