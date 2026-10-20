import json, numpy as np, cv2, pymupdf, warnings
warnings.filterwarnings('ignore')
from shapely.geometry import Polygon, box, Point, MultiPolygon
from shapely.ops import unary_union
from ov2 import make_tf
from hl import poly_of, FILES, U
HL=json.load(open('highlights.json'))
ed=pymupdf.open(U+'4486ac63-PLANOS-ONICE-EDIFICIOS.pdf')
MAIN=(31,31,1157,572)
TF={1:make_tf(True,0.2,(157,187),676,(447,582),(31,31)),
    2:make_tf(True,0.2,(446,161),270,(447,582),(31,31)),
    3:make_tf(False,0.284,(17,123),960,(447,582),(31,31)),
    4:make_tf(False,0.288,(164-194,217-46),973,(447,582),(31,31))}
NAMES={1:['1.1','1.2','1.3','1.4','1.5','1.6'],2:['2.1','2.2','2.3','2.4','2.5','2.6'],
       3:[f'3.{i}' for i in range(1,11)],4:[f'4.{i}' for i in range(1,8)]}
def near(c,t,e=0.03): return c is not None and all(abs(a-b)<e for a,b in zip(c,t))
def panels(page):
    out=[]
    for x in page.get_drawings():
        if near(x.get('color'),(0.58,0.58,0.6)):
            r=x['rect']
            if MAIN[0]<=r.x0 and r.x1<=MAIN[2]+2 and MAIN[1]<=r.y0 and r.y1<=MAIN[3]+2 and r.width>20 and r.height>20:
                out.append(r)
    return out
def zones(tipo):
    tf=TF[tipo]; page=ed[tipo-1]
    P=panels(page)
    polys=[]
    for pg in HL[str(tipo)]:
        pts=[tf(x,y) for x,y in pg[0]]
        polys.append(Polygon(pts).buffer(0))
    assign={i:[] for i in range(len(polys))}; orphan=[]
    if tipo==2:
        for r in P:
            cx=(r.x0+r.x1)/2*1.25; cy=(r.y0+r.y1)/2*1.25   # px a 90 dpi
            if cy>=500 and cx<600: i=5
            elif cx<240 and cy<470: i=4
            elif cx<600 and cy<430: i=3
            elif cx<1090 and cy<340: i=2
            elif cx>=1090 and cy<400: i=1
            else: i=0
            assign[i].append(r)
        P=[]
    for r in P:
        c=Point((r.x0+r.x1)/2,(r.y0+r.y1)/2)
        cand=[(polys[i].exterior.distance(c) if polys[i].contains(c) else -polys[i].exterior.distance(c),i) for i in range(len(polys))]
        cand.sort(reverse=True)
        d,i=cand[0]
        if d<-25: orphan.append(r)
        assign[i].append(r)
    res=[]
    for i in range(len(polys)):
        rs=assign[i]
        if not rs: res.append(None); continue
        u=unary_union([box(r.x0,r.y0,r.x1,r.y1).buffer(26) for r in rs]).buffer(8).buffer(-8)
        if isinstance(u,MultiPolygon): u=u.convex_hull
        res.append(u.simplify(2.0))
    return res,[len(assign[i]) for i in range(len(polys))],len(P),len(orphan)
if __name__=='__main__':
    out={}
    for t in (1,2,3,4):
        z,counts,n,orph=zones(t)
        print(t,'panels',n,'orphans',orph,'per cubierta',counts)
        out[t]=[None if q is None else [[round(x,1),round(y,1)] for x,y in q.exterior.coords] for q in z]
        # overlay
        pm=ed[t-1].get_pixmap(dpi=90,alpha=False); k=90/72
        a=np.frombuffer(pm.samples,np.uint8).reshape(pm.h,pm.w,3).copy(); ov=a.copy()
        cols=[(255,0,255),(0,160,255),(255,120,0),(0,200,0),(200,0,0),(0,0,255),(128,0,128),(0,128,128),(128,128,0),(255,0,0)]
        for i,q in enumerate(z):
            if q is None: continue
            pts=np.array([(x*k,y*k) for x,y in q.exterior.coords],np.int32)
            cv2.fillPoly(ov,[pts],cols[i%10])
        a=cv2.addWeighted(ov,0.35,a,0.65,0)
        for i,q in enumerate(z):
            if q is None: continue
            pts=np.array([(x*k,y*k) for x,y in q.exterior.coords],np.int32)
            cv2.polylines(a,[pts],True,cols[i%10],3)
            c=q.representative_point(); cv2.putText(a,NAMES[t][i],(int(c.x*k)-20,int(c.y*k)+8),cv2.FONT_HERSHEY_SIMPLEX,1.1,(0,0,0),3)
        cv2.imwrite(f'zones{t}.png',cv2.cvtColor(a[:int(575*k)],cv2.COLOR_RGB2BGR))
    json.dump(out,open('zones.json','w'))
