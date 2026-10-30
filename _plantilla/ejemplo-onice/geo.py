import pymupdf, numpy as np
from collections import Counter
PDF='/mnt/user-data/attachments/44e6ff81-6b99-5c6a-b87d-f40892e141f1/61775ab2-PLANOS-ONICE-v2.pdf'
d=pymupdf.open(PDF)
GRAY=(0.58,0.58,0.6)
MAIN=pymupdf.Rect(20,20,1170,585)
MINI=pymupdf.Rect(250,585,765,835)
BLOCKS={'E1-1':(6,list(range(7,13))),'E1-2':(13,list(range(14,20))),'E2-1':(20,list(range(21,27))),'E2-2':(27,list(range(28,34))),
        'E3-1':(34,list(range(35,40))),'E3-2':(40,list(range(41,47))),'E4':(47,list(range(48,58)))}
def near(c,t,e=0.03): return c is not None and len(c)==3 and all(abs(a-b)<e for a,b in zip(c,t))
def rects(pg,clip,minside):
    out=[]
    for x in pg.get_drawings():
        r=x['rect']
        if near(x.get('color'),GRAY) and clip.contains(r) and min(r.width,r.height)>=minside and max(r.width,r.height)<4*minside+40:
            out.append(r)
    # dedupe
    u=[]
    for r in out:
        if not any(abs(r.x0-q.x0)<0.5 and abs(r.y0-q.y0)<0.5 and abs(r.x1-q.x1)<.5 and abs(r.y1-q.y1)<.5 for q in u): u.append(r)
    return u
def hl(pg):
    for x in pg.get_drawings():
        r=x['rect']
        if MINI.contains(r) and (x.get('width') or 0)>2 and x.get('color'):
            pts=[]
            for it in x['items']:
                if it[0]=='re': R=it[1]; pts=[(R.x0,R.y0),(R.x1,R.y0),(R.x1,R.y1),(R.x0,R.y1)]
                elif it[0]=='qu': pts=[(p.x,p.y) for p in it[1]]
                elif it[0]=='l': pts+= [(it[1].x,it[1].y),(it[2].x,it[2].y)]
            return pts,tuple(x['color'])
    return None,None

def centers(R): return np.array([((r.x0+r.x1)/2,(r.y0+r.y1)/2) for r in R])
def register(S,M,flip=False):
    """mini -> sheet: p_sheet = (m - t)/s ; sx=-1 if flip"""
    s=np.median([max(r.width,r.height) for r in M])/np.median([max(r.width,r.height) for r in S])
    cs=centers(S); cm=centers(M)
    if flip: cs2=cs*[-1,1]
    else: cs2=cs
    best=None
    # translation t: m = s*p + t
    votes=Counter()
    for m in cm:
        for p in cs2:
            t=m-s*p; votes[(round(t[0]/1.5),round(t[1]/1.5))]+=1
    (tx,ty),n=votes.most_common(1)[0]; t=np.array([tx*1.5,ty*1.5])
    # refine: matched pairs
    pred=s*cs2+t; pairs=[]
    for i,m in enumerate(cm):
        dd=np.hypot(*(pred-m).T); j=dd.argmin()
        if dd[j]<3: pairs.append((m,cs2[j]))
    if len(pairs)>=3:
        P=np.array([p for _,p in pairs]); Mm=np.array([m for m,_ in pairs])
        A=np.c_[P,np.ones(len(P))]
        # fit m = s*p + t (shared s)
        X=np.r_[P[:,0],P[:,1]]; Y=np.r_[Mm[:,0],Mm[:,1]]
        A=np.zeros((2*len(P),3)); A[:len(P),0]=P[:,0]; A[:len(P),1]=1; A[len(P):,0]=P[:,1]; A[len(P):,2]=1
        sol=np.linalg.lstsq(A,Y,rcond=None)[0]; s=sol[0]; t=np.array([sol[1],sol[2]])
    inv=lambda q:(((q[0]-t[0])/s)*(-1 if flip else 1),(q[1]-t[1])/s)
    register.last=(s,t)
    return inv,len(pairs),len(cm)

from shapely.geometry import MultiPoint, Point
def cub_assign(b):
    sp,dps=BLOCKS[b]
    S=rects(d[sp-1],MAIN,8); cs=centers(S); assign={}; polys={}
    for k,dp in enumerate(dps,1):
        pg=d[dp-1]; M=rects(pg,MINI,4)
        inv,np_,nm=register(S,M,False)
        pts,col=hl(pg)
        poly=MultiPoint([inv(p) for p in pts]).convex_hull
        polys[k]=poly
        for i,c in enumerate(cs):
            if poly.buffer(3).contains(Point(*c)): assign.setdefault(i,[]).append(k)
    return S,assign,polys
def overlay(b,out):
    from PIL import Image, ImageDraw
    S,assign,polys=cub_assign(b); sp=BLOCKS[b][0]
    pm=d[sp-1].get_pixmap(dpi=72); im=Image.frombytes('RGB',(pm.w,pm.h),pm.samples).convert('RGB'); dr=ImageDraw.Draw(im)
    cols=[(255,0,0),(0,160,0),(255,0,255),(0,180,180),(200,120,0),(120,0,200),(0,0,0),(255,128,128),(0,90,0),(90,90,255)]
    for i,r in enumerate(S):
        a=assign.get(i); c=cols[(a[0]-1)%10] if a else (60,60,60)
        dr.rectangle([r.x0,r.y0,r.x1,r.y1],outline=c,width=3 if a else 1)
        if not a: dr.line([r.x0,r.y0,r.x1,r.y1],fill=(0,0,0),width=2)
    for k,p in polys.items():
        dr.polygon(list(p.exterior.coords),outline=cols[(k-1)%10]); x,y=p.exterior.coords[0]; dr.text((x+3,y+3),str(k),fill=cols[(k-1)%10])
    im.crop((0,0,1191,600)).save(out)
