import json,csv,os
from PIL import Image
W='/workspace'; A=W+'/gold_app'
def img(src,name):
    p=f'{W}/{src}'
    if not os.path.exists(p): return None
    im=Image.open(p).convert('RGB'); im.thumbnail((1000,1000)); im.save(f'{A}/img/{name}.jpg',quality=78)
    return f'img/{name}.jpg'
S=[]
def add(**k): S.append(k)
NF='National forest land: hobby panning generally OK outside withdrawn areas; no digging in scenic area/archaeological sites without permit.'
SP='Oregon state park/ocean shore: OPRD permit required for any mining/digging; panning in beach sand limited to hand tools per OAR 736-021.'
PV='Private land: written landowner permission required.'
cp=json.load(open(W+'/cape_perpetua/out/candidates.json'))
for k,v in cp.items():
    conf='medium' if v['fill']>0.55 else 'low'
    add(id='CP-'+k,cat='lidar',area='Cape Perpetua',name=f'Cape Perpetua lidar pad/pit {k}',lat=v['lat'],lon=v['lon'],conf=conf,owner='USFS (verify)',
        desc=f"Lidar flat/pit feature. Area {v['area']:.0f} m², fill {v['fill']:.2f}, elev {v['elev']:.0f} m.",legal=NF,img=img(f'cape_perpetua/out/site_{k}.png','cp_'+k),src=[])
for v in json.load(open(W+'/cape_perpetua/ledge/candidates.json')):
    add(id='CPL-'+v['id'],cat='lidar',area='Cape Perpetua ledge',name=f"1913 ledge candidate {v['id']}",lat=v['lat'],lon=v['lon'],conf='high' if v['id']=='L1' else 'medium',
        owner='USFS / ODOT right-of-way (verify)',desc=v['desc']+f" (elev {v['elev_m']} m)",legal=NF+' Highway cut: ODOT ROW, no digging.',img=img(f"cape_perpetua/ledge/crop_{v['id']}.png",'cpl_'+v['id']),src=[])
for v in json.load(open(W+'/whiskey_run/out/candidates.json')):
    add(id='WR-'+v['id'],cat='lidar',area='Whiskey Run',name=f"Whiskey Run lidar {v['id']}",lat=v['lat'],lon=v['lon'],conf='medium',owner='Private/Coos County (verify)',
        desc=v['desc'],legal=PV,img=img(f"whiskey_run/out/cand_{v['id']}.png",'wr_'+v['id']),src=[])
for r in csv.reader(open(W+'/whiskey_run/out/mrds_records.csv')):
    try: lat,lon=float(r[4]),float(r[5])
    except: continue
    au='AU' in r[3]
    add(id='MRDS-'+r[0],cat='mrds',area='Coos County',name=r[1].strip('"'),lat=lat,lon=lon,conf='high' if au and 'Producer' in r[2] else ('medium' if au else 'low'),
        owner='Unknown (verify)',desc=f"USGS MRDS {r[0]}: {r[2]}, commodity {r[3].strip()}",legal=PV+' Active claims may exist: check BLM MLRS.',img=None,
        src=[['MRDS record',f'https://mrdata.usgs.gov/mrds/show-mrds.php?dep_id={r[0]}']])
hmap={'1':(1,'cand_1'),'3':(2,'cand_3'),'P6':(3,'cand_P6'),'P7':(4,'cand_P7'),'P8':(4,'cand_P8'),'2':(5,'cand_2'),'5':(6,'cand_5'),'4':(7,'cand_4')}
for v in json.load(open(W+'/heceta/out/candidates.json')):
    rk,f=hmap[v['id']]
    add(id='HH-'+v['id'],cat='lidar',area='Heceta Head',name=f"Heceta lidar {v['id']} (rank {rk})",lat=v['lat'],lon=v['lon'],conf='high' if rk<=2 else 'medium' if rk<=4 else 'low',
        owner='State park / USFS (verify)',desc=v['desc'],legal=SP,img=img(f'heceta/out/{f}.png','hh_'+v['id']),src=[])
for v in json.load(open(W+'/yachats_upper/out/candidates.json')):
    o='/'.join(v['owner'])
    add(id='YU-'+v['id'],cat='lidar',area='Upper Yachats',name=f"Upper Yachats {v['id']} ({v['type']})",lat=v['lat'],lon=v['lon'],conf='medium' if v['relief_m']>=1 else 'low',owner=o,
        desc=v['desc']+f" Elev {v['elev_m']} m, relief {v['relief_m']} m, {v['area_m2']} m².",legal=(NF if o=='USFS' else PV)+' Yachats River is salmon habitat: ODFW in-water work window & DSL rules apply.',img=img(f"yachats_upper/out/cand_{v['id']}.png",'yu_'+v['id']),src=[])
N=[('NEWS-1','1913 Cape Perpetua quartz ledge (Meeks & Brown claims)',44.2865,-124.1122,'high','Vein several feet wide, ~200 ft above sea level, copper stains.',NF,
  [['Siuslaw Pilot Nov 12 1913','https://oregonnews.uoregon.edu/lccn/2024240264/1913-11-12/ed-1/seq-3/'],['Eugene Daily Guard Dec 15 1913','https://oregonnews.uoregon.edu/lccn/sn96088107/1913-12-15/ed-1/seq-5/'],['Morning Oregonian Nov 5 1913','https://oregonnews.uoregon.edu/lccn/sn83025138/1913-11-05/ed-1/seq-7/']]),
 ('NEWS-2','1913 upper Yachats gold report',44.295,-124.0,'low','Location unknown; placed arbitrarily in upper Yachats valley.',PV,[]),
 ('NEWS-3','1930 Prather lost-mine ledge, Heceta Head',44.1384,-124.1127,'medium','Lost ledge reported by Prather at Heceta Head.',SP,[['Eugene Register Aug 3 1930','https://oregonnews.uoregon.edu/lccn/sn96088119/1930-08-03/ed-1/seq-4/']]),
 ('NEWS-4','1930-31 Heceta beach sluicing',44.130,-124.120,'medium','Beach black-sand sluicing near Heceta.',SP,[['Springfield News Jul 10 1930','https://oregonnews.uoregon.edu/lccn/sn97071003/1930-07-10/ed-1/seq-2/'],['Register-Guard Mar 2 1931','https://oregonnews.uoregon.edu/lccn/sn85042472/1931-03-02/ed-1/seq-4/']]),
 ('NEWS-5','China Creek (1930-31 reports)',44.163,-124.118,'medium','China Creek mouth, Carl G. Washburne State Park area (approx from memory, not geocoded—verify).',SP+' Salmon stream: no in-stream digging without ODFW/DSL authorization.',[['Register-Guard Mar 2 1931','https://oregonnews.uoregon.edu/lccn/sn85042472/1931-03-02/ed-1/seq-4/']]),
 ('NEWS-7','Whiskey Run 1853 beach rush / Randolph',43.218,-124.404,'high','1853 black-sand gold rush; boom town Randolph near Whiskey Run mouth.',PV+' Beach below vegetation line: OPRD ocean-shore rules.',[])]
for i,n,la,lo,c,d,l,s in N: add(id=i,cat='news',area='Newspaper',name=n,lat=la,lon=lo,conf=c,owner='Verify',desc=d,legal=l,img=None,src=s,approx=True)
add(id='HOME-1',cat='homestead',area='Cape Perpetua',name="Al Gwynn's place (Gwynn Creek mouth)",lat=44.2717,lon=-124.1105,conf='medium',owner='USFS (verify)',desc='Historic homestead of Al Gwynn near Gwynn Creek mouth.',legal=NF+' ARPA protects historic sites >100 yrs.',img=None,src=[],approx=True)
open(A+'/data.js','w').write('window.SITES='+json.dumps(S)+';')
from collections import Counter; print(len(S),Counter(s['cat'] for s in S))
# land status from BLM SMA (cached by /workspace/sw_oregon/sma.py)
L={'USFS':'USFS','BLM':'BLM','ST':'State','PVT':'Private/Unknown','UND':'Undetermined','LG':'Local gov','BIA':'Tribal (BIA)','USACE':'USACE'}
c=json.load(open('/workspace/sw_oregon/sma_cache.json'))
for s in S: s['land']=L.get(c.get(f"{round(s['lat'],5)},{round(s['lon'],5)}"),'Not checked')
open(A+'/data.js','w').write('window.SITES='+json.dumps(S)+';')
print(Counter(s['land'] for s in S))
