import numpy as np
import numpy.linalg as la

class Obstacles:
    """ Tárolja az akadályokat """
    def __init__(self,polygons):
        edges = []
        for pol in polygons:
            for i in range(len(pol)-1):
                edges.append([pol[i], pol[i+1]])
        edges.append([pol[i+1], pol[0]])
        self.edges = np.array(edges, np.float64)

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

        #validedges = self.edges[nonzero &  ((p1c & p2c) == 0)]   # nonzero ccw edges in clip rectangle
        validedges = self.edges[nonzero & ccw & ((p1c & p2c) == 0)]   # nonzero ccw edges in clip rectangle

        p1,p2 = validedges[:,0]-vp, validedges[:,1]-vp
        mid = p1+p2

        shadow = np.stack(( validedges[:,0], validedges[:,1], 
            p2 / np.expand_dims(la.norm(p2,axis=1),1) * 1000 +vp,
            mid / np.expand_dims(la.norm(mid, axis=1),1)* 1000 +vp ,
            p1 / np.expand_dims(la.norm(p1,axis=1),1)* 1000 +vp,
            ), axis=1)
        
        return shadow.tolist() if not debug else (shadow.tolist(), validedges.tolist())

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

    o = Obstacles(obst)
    print (o.shadows((0,0,200,200), center))


        



