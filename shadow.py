import math
import numpy as np
from itertools import tee, count
from pygame.math import Vector2


def cw(edge):
    """ return true if the edge is counter clockwise directed """
    ((x1,y1),(x2,y2)) = edge
    return (x1*y2)-(y1*x2) < 0

def ccw(edge):
    return not cw(edge)

def clip(rect, edgelist):
    """ clip edgelist to rectangular area"""
    def clip_edge(edge): # -> edge (or None if not contained)
        cx1,cy1,w,h = rect
        cx2,cy2 = cx1 + w, cy1 + h
        p1, p2 = edge

        def code(p):
            code = 0b000
            if p[0] < cx1: code  = 0b0001  
            if p[0] > cx2: code  = 0b0010  
            if p[1] < cy1: code |= 0b0100  
            if p[1] > cy2: code |= 0b1000  
            return code

        code1 , code2 = code(p1), code(p2)
        
        if code1 == 0 and code2 == 0 :  return edge # completely inside
        if code1 & code2 != 0:          return None # completely outside

        # at least one of the point is outside (find it)
        outpoint,otherpoint = (p1,p2) if code1 == 0 else (p2,p1)
        ### TODO: actually clip the edge
        cedge = edge
        return cedge

    return filter(None,map(clip_edge, edgelist))


class Obstacles:
    """ Tárolja az akadályokat """
    def __init__(self,polygons):
        edges = []
        for pol in polygons:
            for i in range(len(pol)-1):
                edges.append([pol[i+1], pol[0]])
        self.obstacles = np.array(edges, np.float64)

    def shadows(self,area_rect, viewpoint):
        vp = np.array(viewpoint)
        et = self.obstacles - vp # transformed edge coordinates
        print(et)
        

def shadow(polygons, viewpoint, maxrange = None, direction=ccw, debug=False):
    """ létrehozza az árnyéktrapézokat
        x2 > x1 kivéve ha "túlfordul" vagyis átlép a 360 fokos határon
        (ez akkor fordul elő ha x1-x2 > pi)
        polygons: list of polygons [[(x,y),(x,y)...], [(x,y),(x,y)..]]
        viewpoint: (x,y)
        maxrange: int
    """
    
    vx,vy = viewpoint

    def offset(x, y):
        return lambda points: list((v[0] + x, v[1] + y) for v in points)

    tr_polygons = map(offset(-vx,-vy), polygons)
    tr_edges = filter(direction, iter_edges(tr_polygons))
    
    if (maxrange is not None):
        cliprect = (-maxrange/2, -maxrange/2, maxrange, maxrange)
        tr_edges = clip(cliprect, tr_edges)
    else :
        maxrange = 500

    quads = []
    debugdata = []

    for p1, p2 in tr_edges:
        v1,v2 = Vector2(p1), Vector2(p2)
        try:
            vm = (v1.normalize()+v2.normalize())
            if debug: debugdata.append((p1,p2))
            tdek = (v1, v2, v2.normalize()*maxrange, vm.normalize()*maxrange, v1.normalize()*maxrange)
            quads.append(offset(vx,vy)(tdek))
        except ValueError:
            pass

    return quads if not debug else (quads,debugdata)





if __name__ == "__main__":
    center = 300,300
    pontok = [
            (0,0),
            (30,50),
            (170,150),
            (50,200),
            (200,50),
            (400,450),
            (475,410),
            ]

    print('polar test:')
    for p in pontok:
        pol = to_polar(p) 
        orig = list(round(x,10) for x in from_polar(pol))
        print(p,"->", (pol[0]*180/math.pi, pol[1] ),  "->", orig)
        assert(list(p) == orig) 
        print("-----------------------")
    print()

    print (shadows(pontok, center, 200))


    



