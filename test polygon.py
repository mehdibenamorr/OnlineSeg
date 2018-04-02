import numpy as np
from common.common import *
EPS = 1e-9



if __name__ == '__main__':
    n = int(input('n'))
    pol = Polygon()
    for i in range(n):
        a = float(input('a'))
        b = float(input('b'))
        pol.add_vertex(Point(a, b))

    p1 = Point(0, 3)
    p2 = Point(10, 0)
    res = polygon_cut(pol, Line(p1, p2), False)
    for i in range(len(res.vertices)):
        print(res.vertices[i].r, " ", res.vertices[i].i)
