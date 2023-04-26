import os

objs =os.listdir(r'C:\Users\Lenovo\Desktop\pics')

with open(r'C:\Users\Lenovo\Desktop\pics.txt', 'w') as fp:
    for item in objs:
        # write each item on a new line
        fp.write("%s\n" % item)
    print('Done')