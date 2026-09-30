import json, math, hashlib
D=json.load(open('/home/user/buildphillynow/public/data/phila-neighborhoods.json'))
LON0,LAT1=-75.2803,40.1380
S=2000.0; K=math.cos(math.radians(40.0))
def proj(lon,lat): return ((lon-LON0)*K*S, (LAT1-lat)*S)
def rdp(pts,eps):
    if len(pts)<3: return pts
    (x1,y1),(x2,y2)=pts[0],pts[-1]; dx,dy=x2-x1,y2-y1; n=math.hypot(dx,dy) or 1e-9
    dmax=0;idx=0
    for i in range(1,len(pts)-1):
        d=abs(dy*pts[i][0]-dx*pts[i][1]+x2*y1-y2*x1)/n
        if d>dmax: dmax=d;idx=i
    if dmax>eps: return rdp(pts[:idx+1],eps)[:-1]+rdp(pts[idx:],eps)
    return [pts[0],pts[-1]]
def rdp_ring(pts,eps):
    if pts[0]==pts[-1]: pts=pts[:-1]
    if len(pts)<4: return pts
    k=max(range(len(pts)),key=lambda i:(pts[i][0]-pts[0][0])**2+(pts[i][1]-pts[0][1])**2)
    a=rdp(pts[:k+1],eps); b=rdp(pts[k:]+[pts[0]],eps)
    return a[:-1]+b[:-1]
def area(ring):
    a=0
    for i in range(len(ring)):
        x1,y1=ring[i]; x2,y2=ring[(i+1)%len(ring)]; a+=x1*y2-x2*y1
    return abs(a)/2
hoods=[]
for f in D['features']:
    g=f['geometry']; polys=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
    rings=[]; A=0; cx=cy=0; n=0; bx0=by0=1e9; bx1=by1=-1e9
    for p in polys:
        for j,ring in enumerate(p):
            pr=[proj(x,y) for x,y in ring]
            for x,y in pr: bx0=min(bx0,x); bx1=max(bx1,x); by0=min(by0,y); by1=max(by1,y)
            s=rdp_ring(pr,0.55)
            if j==0:
                A+=area(pr)
                for x,y in pr: cx+=x; cy+=y; n+=1
            if len(s)>=4: rings.append(s)
    if not rings or n==0: continue
    d=' '.join('M'+' L'.join(f'{x:.1f} {y:.1f}' for x,y in r)+'Z' for r in rings)
    hoods.append(dict(name=f['properties']['MAPNAME'],d=d,area=A,cx=cx/n,cy=cy/n,bb=(bx0,by0,bx1,by1)))
W=(-74.9558-LON0)*K*S; H=(LAT1-39.8670)*S
print('map size',round(W),round(H),'hoods',len(hoods))
CC={'Center City East','Chinatown','Old City','Society Hill','Rittenhouse','Logan Square','Washington Square West','Fitler Square','Callowhill','Spring Garden','Fairmount','University City','Graduate Hospital'}
cc_pts=[(h['cx'],h['cy']) for h in hoods if h['name'] in CC]
ccx=sum(p[0] for p in cc_pts)/len(cc_pts); ccy=sum(p[1] for p in cc_pts)/len(cc_pts)
def quant(vals,bins=5):
    s=sorted(vals); return [s[int(len(s)*i/bins)] for i in range(1,bins)]
def binof(v,q): return sum(1 for t in q if v>=t)
FILLS=[0.03,0.07,0.12,0.18,0.26]
def build(fname, vb, metric, highlight=None, seed=0):
    x,y,w,h=vb
    if metric=='area': vals=[hh['area'] for hh in hoods]
    elif metric=='dist': vals=[-math.hypot(hh['cx']-ccx,hh['cy']-ccy) for hh in hoods]
    elif metric=='ew': vals=[hh['cx']+0.35*hh['cy'] for hh in hoods]
    elif metric=='hash': vals=[int(hashlib.md5((hh['name']+str(seed)).encode()).hexdigest()[:6],16) for hh in hoods]
    q=quant(vals)
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x:.0f} {y:.0f} {w:.0f} {h:.0f}" preserveAspectRatio="xMidYMid slice">',
         '<defs><linearGradient id="f" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4a4a4a"/><stop offset="0.3" stop-color="#fff"/><stop offset="0.55" stop-color="#fff"/><stop offset="0.85" stop-color="#3c3c3c"/><stop offset="1" stop-color="#2a2a2a"/></linearGradient>',
         f'<mask id="m" maskUnits="userSpaceOnUse" x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}"><rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" fill="url(#f)"/></mask></defs>',
         '<g mask="url(#m)" fill="#fff" stroke="#fff" stroke-linejoin="round">']
    for hh,v in zip(hoods,vals):
        b=binof(v,q); hl=highlight and hh['name'] in highlight
        fo=0.42 if hl else FILLS[b]; so=0.95 if hl else 0.42; sw=1.5 if hl else 0.8
        out.append(f'<path d="{hh["d"]}" fill-opacity="{fo}" stroke-opacity="{so}" stroke-width="{sw}"/>')
    out.append('</g></svg>')
    open('/home/user/buildphillynow-landing/assets/art/'+fname,'w').write(''.join(out))
    return sum(len(p) for p in out)
# 4:5 viewboxes
def vbox(cx,cy,h): w=h*0.8; return (cx-w/2,cy-h/2,w,h)
def fit(names,pad=1.45,min_h=150,down=0.10):
    bs=[hh['bb'] for hh in hoods if hh['name'] in names]
    assert bs, names
    x0=min(b[0] for b in bs); y0=min(b[1] for b in bs); x1=max(b[2] for b in bs); y1=max(b[3] for b in bs)
    w=x1-x0; h=y1-y0
    H=max(h*pad, w*pad/0.8, min_h)
    return vbox((x0+x1)/2,(y0+y1)/2+H*down,H)
HPF=['Logan Square','Hawthorne','Callowhill','Francisville','Spruce Hill','Fishtown - Lower Kensington','Port Richmond']
OZ=['Cobbs Creek','Walnut Hill','North Central','Hartranft','Franklinville','Stanton','Tioga','Haddington']
sizes={}
sizes['ccd']=build('cover-ccd.svg', vbox(ccx+6,ccy+18,140), 'area', highlight=CC)
sizes['hpf']=build('cover-hpf.svg', fit(HPF), 'area', highlight=set(HPF))
sizes['phloz']=build('cover-phloz.svg', fit(OZ,pad=1.3), 'area', highlight=set(OZ))
for k,v in sizes.items(): print(k, f'{v/1024:.0f}KB')
missing=[n for n in HPF+OZ if n not in {hh["name"] for hh in hoods}]; print('names not found:',missing)
