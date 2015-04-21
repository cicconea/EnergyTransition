import sys

f = open('mc.txt', 'w')
i = sys.argv[1]
f.write(i)
f.close()