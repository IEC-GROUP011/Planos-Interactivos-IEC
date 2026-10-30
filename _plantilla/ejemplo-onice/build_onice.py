import sys, json, os, re
sys.path.insert(0,os.path.dirname(__file__))
from geo import *
from shapely.geometry import Polygon, box, Point, MultiPoint, MultiPolygon
from shapely.ops import unary_union
from shapely import affinity
OUT=sys.argv[1]
ED={'E1-1':'E1','E1-2':'E1','E2-1':'E2','E2-2':'E2','E3-1':'E3','E3-2':'E3','E4':'E4'}
COL={'E1':1,'E2':2,'E3':3,'E4':4}
DISP={'E1':2,'E2':3,'E3':4,'E4':5}
STR={'E1-1':58,'E1-2':59,'E2-1':60,'E2-2':61,'E3-1':62,'E3-2':63,'E4':64}
def zone(rs,buf=13):
    u=unary_union([box(r.x0,r.y0,r.x1,r.y1).buffer(buf,join_style=2) for r in rs]).buffer(6).buffer(-6)
    if isinstance(u,MultiPolygon): u=u.convex_hull
    return u.simplify(1.5)
def P(poly): return [[round(x,1),round(y,1)] for x,y in poly.exterior.coords][:-1]
def L(poly): p=poly.representative_point() if not poly.contains(poly.centroid) else poly.centroid; return [round(p.x,1),round(p.y,1)]
blocks={}
for b,(sp,dps) in BLOCKS.items():
    S,assign,polys=cub_assign(b)
    # resolve panels in 2 highlights: deepest inside
    cubs={}
    for i,a in assign.items():
        k=a[0]
        if len(a)>1:
            c=Point(*centers([S[i]])[0]); k=max(a,key=lambda k:polys[k].exterior.distance(c) if polys[k].contains(c) else -1)
        cubs.setdefault(k,[]).append(i)
    blocks[b]={'S':S,'cubs':{k:sorted(v) for k,v in sorted(cubs.items())},'dps':dps}
# disposición: transforms struct(block) -> disp(edificio)
tf={}
for b in BLOCKS:
    e=ED[b]; Dp=rects(d[DISP[e]-1],MAIN,5); S=blocks[b]['S']
    inv,n,nm=register(S,Dp,False); s,t=register.last
    tf[b]=(float(s),float(t[0]),float(t[1])); blocks[b]['D']=Dp
    print(b,'disp match',n,'/',len(Dp),'s=%.4f'%s)
# missing cubiertas: disp panels not covered by any block cub
for e in ('E1','E2','E3','E4'):
    bs=[b for b in BLOCKS if ED[b]==e]; Dp=blocks[bs[0]]['D']; dc=centers(Dp); used=set()
    for b in bs:
        s,tx,ty=tf[b]; S=blocks[b]['S']
        for k,ix in blocks[b]['cubs'].items():
            for i in ix:
                c=centers([S[i]])[0]*s+[tx,ty]; j=np.hypot(*(dc-c).T).argmin()
                if np.hypot(*(dc[j]-c))<4: used.add(j)
    left=[j for j in range(len(Dp)) if j not in used]
    print(e,'disp panels',len(Dp),'covered',len(used),'left',len(left))
    if left:
        # paneles de borde que el recuadro del minimapa no cubría: a la cubierta con el panel más cercano
        own=[]  # (disp_center, block, cubk)
        for b in bs:
            s,tx,ty=tf[b]; S=blocks[b]['S']
            for k,ix in blocks[b]['cubs'].items():
                for i in ix: own.append((centers([S[i]])[0]*s+[tx,ty],b,k))
        oc=np.array([o[0] for o in own])
        for j in left:
            dd=np.hypot(*(oc-dc[j]).T); n=dd.argmin(); _,b,k=own[n]
            assert dd[n]<60, ('panel lejano',e,dd[n])
            s,tx,ty=tf[b]; S=blocks[b]['S']; sc=centers(S); c=(dc[j]-[tx,ty])/s; i=int(np.hypot(*(sc-c).T).argmin())
            assert np.hypot(*(sc[i]-c))<6
            if i not in blocks[b]['cubs'][k]: blocks[b]['cubs'][k].append(i)
            print('   borde ->',b,k,'dist %.0f'%dd[n])
# strings per sheet (labels)
strings={}; items={}
for b,pn in STR.items():
    labs=[]
    for blk in d[pn-1].get_text('dict')['blocks']:
        for l in blk.get('lines',[]):
            for sp_ in l['spans']:
                m=re.match(r'(S\d+)\s*\((\d+)\)',sp_['text'].strip())
                if m: labs.append((m.group(1),int(m.group(2))))
    items[b]=sorted({x[0] for x in labs},key=lambda x:int(x[1:]))
    for sid,n in labs: strings.setdefault(ED[b],{})[sid]=n
# implantación polygons
pg=d[0]; outl=[]
for x in pg.get_drawings():
    c=x.get('color')
    if c and not all(abs(v-c[0])<0.01 for v in c):
        pts=[(it[1].x,it[1].y) for it in x['items']]+[(x['items'][-1][2].x,x['items'][-1][2].y)]
        outl.append((tuple(round(v,2) for v in c),Polygon(pts).buffer(0)))
def pick(col,top):
    cand=[p for c,p in outl if c==col]; cand.sort(key=lambda p:p.bounds[1]); return cand[0] if top else cand[-1]
G={}
blue=(0.15,0.46,0.73); green=(0.07,0.61,0.28); red=(0.93,0.12,0.14); yel=(0.96,0.93,0.32)
gr=sorted([p for c,p in outl if c==green],key=lambda p:p.bounds[1]); bl=sorted([p for c,p in outl if c==blue],key=lambda p:p.bounds[1])
G['E1-1'],G['E2-1']=gr[0],gr[1]; G['E1-2'],G['E2-2']=bl[0],bl[1]
R=[p for c,p in outl if c==red][0]; G['E4']=[p for c,p in outl if c==yel][0]
# split red along its long axis at the middle
mrr=R.minimum_rotated_rectangle; xs=list(mrr.exterior.coords)[:4]
e0=np.subtract(xs[1],xs[0]); e1=np.subtract(xs[2],xs[1]); ax=e0 if np.hypot(*e0)>np.hypot(*e1) else e1; ax=ax/np.hypot(*ax)
if ax[0]<0: ax=-ax
c=np.array(R.centroid.coords[0]); nrm=np.array([-ax[1],ax[0]])*400
right=Polygon([c+nrm,c-nrm,c-nrm+ax*400,c+nrm+ax*400]); left=Polygon([c+nrm,c-nrm,c-nrm-ax*400,c+nrm-ax*400])
G['E3-1']=R.intersection(right); G['E3-2']=R.intersection(left)
data={'cfg':{'kind':'fotovoltaica','title':'Visor de planos Ónice','site':{'name':'Calle Ónice','sub':'Málaga · Autoconsumo FV'},
  'obraId':'ONICE','modo':'demo','imgV':'20261030','marcos0':True,
  'capas':[{'id':'estructura','label':'Estructura','nivel':'cubierta'},{'id':'paneles','label':'Paneles','nivel':'cubierta'},{'id':'strings','label':'Strings','nivel':'string'}],
  'alt0':'Implantación con los 4 edificios divididos en 7 bloques'},
  'buildings':[],'strings':{e:[{'id':k,'n':v} for k,v in sorted(m.items(),key=lambda kv:int(kv[0][1:]))] for e,m in strings.items()}}
names=[]
for b in BLOCKS:
    e=ED[b]; S=blocks[b]['S']; s,tx,ty=tf[b]; cubs=[]
    for k,ix in blocks[b]['cubs'].items():
        z=zone([S[i] for i in ix])
        cub={'id':str(k),'n':len(ix),'poly':P(z),'lab':L(z)}
        if k<=len(blocks[b]['dps']): cub['det']={'estructura':f'img/det_{b}_{k}.webp'}; names.append((f'det_{b}_{k}',blocks[b]['dps'][k-1]))
        else: cub['nota']='Sin plano de detalle de estructura en el PDF'
        cubs.append(cub)
    # avoid overlaps between cub zones: shrink by difference in order
    polys=[Polygon(c['poly']) for c in cubs]
    for i in range(len(polys)):
        for j in range(i):
            if polys[i].intersects(polys[j]):
                a=polys[i].difference(polys[j].buffer(1))
                if isinstance(a,MultiPolygon): a=max(a.geoms,key=lambda g:g.area)
                polys[i]=a
        cubs[i]['poly']=P(polys[i].simplify(1.5)); cubs[i]['lab']=L(polys[i])
    g=G[b]
    data['buildings'].append({'id':b,'ed':e,'col':COL[e],'poly':P(g.simplify(0.5)),'lab':L(g),
      'hojas':{'estructura':{'img':f'img/est_{b}.webp'},'paneles':{'img':f'img/disp_{e}.webp','tf':[round(s,5),round(tx,2),round(ty,2)]},'strings':{'img':f'img/str_{b}.webp','items':items[b]}},
      'cubs':cubs})
    names+= [(f'est_{b}',BLOCKS[b][0]),(f'str_{b}',STR[b])]
    print(b,[(c['id'],c['n']) for c in cubs],'strings',items[b])
for e,pn in DISP.items(): names.append((f'disp_{e}',pn))
names.append(('general_1',1))
json.dump(data,open(os.path.join(OUT,'data.json'),'w'),ensure_ascii=False)
json.dump(names,open(os.path.join(OUT,'pages.json'),'w'))
print('strings',data['strings'])
print('images',len(names))
