import math
from itertools import tee, count

def iter_edges(poligons):
    """ iterate over all edges of poligons (list of (x,y) points) """
    for pol in poligons:
        for i in range(len(pol)-1):
            yield (pol[i],pol[i+1])
        yield (pol[i+1], pol[0])

def to_polar(point):
    """
    polár koordinátákra vált
    """
    dx,dy = point
    a = math.atan(dx/dy) if dy != 0 else math.pi/2 if dx > 0 else -math.pi/2
    r = math.sqrt(dx*dx + dy*dy)
    if dy < 0 : a += math.pi 
    if a < 0 : a += 2*math.pi
    return (a,r)

def from_polar(ppoint):
    """polárkoordinátákból x,y koordinátákra vált """
    a,r = ppoint
    return (r * math.sin(a), r * math.cos(a)) 

def fok(ppoint):
    return (ppoint[0]*180/math.pi, ppoint[1])

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


def shadows(polygons, viewpoint, maxrange = None, direction=ccw):
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
    debug = []

    for p1, p2 in tr_edges:
        pp1, pp2 = to_polar(p1), to_polar(p2)
        a1, a2 = pp1[0], pp2[0]
        
        debug.append((p1,p2))
        tdek = (p1, p2, from_polar((a2,maxrange)), from_polar((a1,maxrange)) )
        quads.append(offset(vx,vy)(tdek))

    return (quads, debug)


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


    



