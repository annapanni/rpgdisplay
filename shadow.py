import numpy as np
from numpy.linalg import norm
from itertools import chain

class Obstacles:
    """ Tárolja az akadályokat """
    def __init__(self,polygons):
        edges = chain.from_iterable(Obstacles.edgelist(pol) for pol in polygons)
        self.edges = np.array(list(edges), np.float64)

    @staticmethod
    def edgelist(points):
        """ iterator for convert polygon points to edge-list """
        for i in range(len(points)-1):
            yield [points[i], points[i+1]]
        yield [points[-1], points[0]]

    @staticmethod
    def intersect(a, bs, strict=False):
        """ intersection points of edge a and edge-array b
            returns: np.ma.MaskedArray
            if strict==True intersection point must be on one of bs.
        """
        a1,a2 = a[0], a[1]      # vectors to first edge start and end point
        bs1,bs2 = bs[:,0], bs[:,1]  # list of vectors for the target edges starts and ends 
        va,vbs = a2-a1,bs2-bs1     # vectors for edge a and b
        ii = np.cross( va,vbs )            # if p==0 -> parallel lines : no intersection
        ii = np.ma.masked_equal(ii, 0)      # mask zeros!
        q = np.cross( bs1-a1, va ) / ii     # a1 + q*(a2-a1) -> intersection point
        if strict: 
            q = np.ma.masked_outside(q, 0, 1)  # must be between start and end

        return bs1 + q[:,np.newaxis] * vbs
    
    @staticmethod
    def inside(point, polygon):
        """ returns True if the point is inside of the polygon. (The polygon
            "inside" is ccw defined.) Polygon must be an edge list.
        """
        # get the index of the first edge not directed to the point
        p1, p2 = polygon[:,0] , polygon[:,1]
        ix = np.argmax(np.cross(p2-p1,point-p1) != 0)

        # get first point of that edge 
        testpoint = polygon[ix][0]

        # determine all intersections from point to testpoint
        isect = Obstacles.intersect([point, testpoint], polygon, strict=True) 

        # index of closest intersection point
        ix = np.sum((isect-point)**2, axis=1).argmin() 
        #ix = np.abs(isect[:,0]-point[0]).argmin() # x direction only? 

        # detect ccw direction of the found edge
        return np.cross(polygon[ix][0]-point, polygon[ix][1]-point)  > 0 

    def valid(self,point):
        """False if point is inside an obstacle"""
        return not Obstacles.inside(point, self.edges) 

    def shadows(self,area_rect, viewpoint, debug=False):
        cxmin,cymin,w,h = area_rect
        cxmax,cymax = cxmin + w, cymin + h

        vp = np.array(viewpoint)
        p1, p2 = self.edges[:,0], self.edges[:,1] # edges from viewpoint
        ccw = np.cross((p2-vp) , (p1-vp)) < 0 # counterclockwise directed edges
        nonzero = (p1!=vp).any(axis=1) & (p2 != vp).any(axis=1)

        p1c =   np.where(p1[:,0] <cxmin,0b0001,0) |\
                np.where(p1[:,0] >cxmax,0b0010,0) |\
                np.where(p1[:,1] <cymin,0b0100,0) |\
                np.where(p1[:,1] >cymax,0b1000,0) 

        p2c =   np.where(p2[:,0] <cxmin,0b0001,0) |\
                np.where(p2[:,0] >cxmax,0b0010,0) |\
                np.where(p2[:,1] <cymin,0b0100,0) |\
                np.where(p2[:,1] >cymax,0b1000,0) 

        validedges = self.edges[nonzero & ccw & ((p1c & p2c) == 0)]   # nonzero ccw edges in clip rectangle

        p1,p2 = validedges[:,0]-vp, validedges[:,1]-vp
        mid = p1+p2

        shadow = np.stack(( validedges[:,0], validedges[:,1], 
            p2 / np.expand_dims(norm(p2,axis=1),1) * 1000 +vp,
            mid / np.expand_dims(norm(mid, axis=1),1)* 1000 +vp ,
            p1 / np.expand_dims(norm(p1,axis=1),1)* 1000 +vp,
            ), axis=1)
        
        return shadow.tolist() if not debug else (shadow.tolist(), validedges.tolist())

    def visible(self,area_rect, viewpoint, debug=False):
        cxmin,cymin,w,h = area_rect
        cxmax,cymax = cxmin + w, cymin + h

        vp = np.array(viewpoint)
        # edges from viewpoint
        p1, p2 = self.edges[:,0], self.edges[:,1] 
        # counterclockwise directed edges
        ccw = np.cross((p2-vp) , (p1-vp)) < 0 

        nonzero = (p1!=vp).any(axis=1) & (p2 != vp).any(axis=1)

        p1c =   np.where(p1[:,0] <cxmin,0b0001,0) |\
                np.where(p1[:,0] >cxmax,0b0010,0) |\
                np.where(p1[:,1] <cymin,0b0100,0) |\
                np.where(p1[:,1] >cymax,0b1000,0) 

        p2c =   np.where(p2[:,0] <cxmin,0b0001,0) |\
                np.where(p2[:,0] >cxmax,0b0010,0) |\
                np.where(p2[:,1] <cymin,0b0100,0) |\
                np.where(p2[:,1] >cymax,0b1000,0) 

        validedges = self.edges[nonzero & ccw & ((p1c & p2c) == 0)]   # nonzero ccw edges in clip rectangle
        
        vpoly = np.array([ # initial visibility polygon edges (from Rect) 
            [[cxmin,cymin], [cxmax,cymin]],
            [[cxmax,cymin], [cxmax,cymax]],
            [[cxmax,cymax], [cxmin,cymax]],
            [[cxmin,cymax], [cxmin,cymin]],
            ])
        
        for e in validedges:
            # if both points inside
            if Obstacles.inside(e[0], vpoly) and Obstacles.inside(e[1], vpoly):
                p1, p2 = e[0], e[1]
                x = Obstacles.intersect([vp,p1],vpoly)

        return vpoly[:,0].tolist() if not debug else (vpoly[:,0].tolist(), validedges.tolist())


if __name__ == "__main__":
    center = 300,300
    obst = [[
            (0,0),
            (30,50),
            (170,150),
            (50,200),
            (200,50),
            (400,450),
            (475,410),
            ]]
    fence = list(Obstacles.edgelist(obst[0]))
    assert fence == [
                [(0, 0), (30, 50)], [(30, 50), (170, 150)], 
                [(170, 150), (50, 200)], [(50, 200), (200, 50)], 
                [(200, 50), (400, 450)], [(400, 450), (475, 410)], [(475, 410), (0, 0)]]

    print(Obstacles.inside(np.array((4,4)), np.array(fence)))
    print(Obstacles.inside(np.array((-4,-4)), np.array(fence)))



    o = Obstacles(obst)
    # test intersection
    e = np.array([[10,10],[100,100]])
    ts = np.array([ [[-10,10],[2,-40]], [[0,50],[50,0]], [[20,20],[110,110]], [[90,120],[240,80]], [[12,10],[248,120]]])
    print("nonstrict")
    print(Obstacles.intersect(e,ts, strict=False))
    print("strict")
    print(Obstacles.intersect(e,ts, strict=True))
    print("polygons")
    print (o.shadows((0,0,200,200), center))


        



