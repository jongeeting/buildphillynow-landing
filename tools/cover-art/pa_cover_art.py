import json, math, csv, collections
T=json.load(open('/tmp/counties-10m.json'))
sc=T['transform']['scale']; tr=T['transform']['translate']
# decode arcs
arcs=[]
for a in T['arcs']:
    x=y=0; pts=[]
    for dx,dy in a:
        x+=dx; y+=dy; pts.append((x*sc[0]+tr[0], y*sc[1]+tr[1]))
    arcs.append(pts)
def arc(i): return arcs[i] if i>=0 else list(reversed(arcs[~i]))
def ring(idx):
    pts=[]
    for i in idx:
        a=arc(i); pts+= a if not pts else a[1:]
    return pts
geoms=T['objects']['counties']['geometries']
pa=[g for g in geoms if str(g['id']).startswith('42')]
print('PA counties',len(pa), [g['properties']['name'] for g in pa[:3]])
# recommended tracts by county (135 non-Philly from the statewide report) + Philadelphia (82 from the Philadelphia analysis)
rows=list(csv.DictReader(open('/tmp/pa135.csv')))
cnt=collections.Counter(r['county_name'].replace(' County','') for r in rows); cnt['Philadelphia']=82
print(cnt.most_common(6))
LAT0=41.0; K=math.cos(math.radians(LAT0)); S=300.0
allp=[p for g in pa for poly in (g['arcs'] if g['type']=='MultiPolygon' else [g['arcs']]) for r in poly for p in ring(r)]
lon0=min(p[0] for p in allp); lat1=max(p[1] for p in allp)
def proj(p): return ((p[0]-lon0)*K*S,(lat1-p[1])*S)
W=(max(p[0] for p in allp)-lon0)*K*S; H=(lat1-min(p[1] for p in allp))*S
print('state size',round(W),round(H))
def rdp(pts,eps):
    if len(pts)<3: return pts
    (x1,y1),(x2,y2)=pts[0],pts[-1]; dx,dy=x2-x1,y2-y1; n=math.hypot(dx,dy) or 1e-9
    dm=0;ix=0
    for i in range(1,len(pts)-1):
        d=abs(dy*pts[i][0]-dx*pts[i][1]+x2*y1-y2*x1)/n
        if d>dm: dm=d;ix=i
    if dm>eps: return rdp(pts[:ix+1],eps)[:-1]+rdp(pts[ix:],eps)
    return [pts[0],pts[-1]]
def rdp_ring(pts,eps):
    if pts[0]==pts[-1]: pts=pts[:-1]
    if len(pts)<4: return pts
    k=max(range(len(pts)),key=lambda i:(pts[i][0]-pts[0][0])**2+(pts[i][1]-pts[0][1])**2)
    a=rdp(pts[:k+1],eps); b=rdp(pts[k:]+[pts[0]],eps); return a[:-1]+b[:-1]
vw=W*1.06; vh=vw*1.25; vx=-W*0.03; vy=H*0.5-vh*0.40   # state centred a little above the middle, clear of header and title
out=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vx:.0f} {vy:.0f} {vw:.0f} {vh:.0f}" preserveAspectRatio="xMidYMid slice"><g fill="#fff" stroke="#fff" stroke-linejoin="round">']
mx=max(cnt.values())
for g in pa:
    name=g['properties']['name']; c=cnt.get(name,0)
    polys=g['arcs'] if g['type']=='MultiPolygon' else [g['arcs']]
    d=''
    for poly in polys:
        for r in poly:
            pts=[proj(p) for p in ring(r)]; pts=rdp_ring(pts,0.35)
            if len(pts)>=4: d+='M'+' L'.join(f'{x:.1f} {y:.1f}' for x,y in pts)+'Z'
    fo=0.04 if c==0 else round(0.12+0.46*math.sqrt(c/mx),3)
    so=0.5 if c==0 else 0.85
    out.append(f'<path d="{d}" fill-opacity="{fo}" stroke-opacity="{so}" stroke-width="{0.8 if c==0 else 1.2}"/>')
out.append('</g></svg>')
open('/home/user/buildphillynow-landing/assets/art/cover-paoz.svg','w').write(''.join(out))
print('cover-paoz.svg', round(sum(map(len,out))/1024),'KB')
