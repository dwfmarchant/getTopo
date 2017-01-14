
def writeUBCtopo(x, y, hgt, fname='topo.txt'):

    with open(fname, 'w') as topo_file:
        topo_file.write("{}\n".format(x.size))
        for loc in zip(x.flat, y.flat, hgt.flat):
            line = "{:.2f} {:.2f} {:.2f}\n".format(*loc)
            topo_file.write(line)
