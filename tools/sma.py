import json,requests,sys,os,re
from concurrent.futures import ThreadPoolExecutor
cache=json.load(open('sma_cache.json')) if os.path.exists('sma_cache.json') else {}
pts=set()
for o in json.load(open('mines.json')): pts.add((o['lat'],o['lon']))
s=open('/workspace/gold_app/data.js').read();S=json.loads(s[s.index('=')+1:].rstrip(';'))
for o in S: pts.add((round(o['lat'],5),round(o['lon'],5)))
for f in sys.argv[1:]:
    for o in json.load(open(f)): pts.add((round(o['lat'],5),round(o['lon'],5)))
U='https://gis.blm.gov/arcgis/rest/services/lands/BLM_Natl_SMA_LimitedScale/MapServer/identify'
ses=requests.Session()
def q(p):
    k=f'{p[0]},{p[1]}'
    if k in cache: return
    for t in range(3):
        try:
            r=ses.get(U,params=dict(geometry=f'{p[1]},{p[0]}',geometryType='esriGeometryPoint',sr=4326,tolerance=0,mapExtent=f'{p[1]-.01},{p[0]-.01},{p[1]+.01},{p[0]+.01}',imageDisplay='400,400,96',layers='all:1',returnGeometry='false',f='json'),timeout=60).json()
            a=[x['attributes'] for x in r.get('results',[])]
            cache[k]=a[0]['ADMIN_AGENCY_CODE'] if a else 'PVT';return
        except Exception as e: pass
    cache[k]='ERR'
todo=[p for p in pts if f'{p[0]},{p[1]}' not in cache or cache[f'{p[0]},{p[1]}']=='ERR']
print(len(pts),len(todo),flush=True)
with ThreadPoolExecutor(24) as ex:
    for i,_ in enumerate(ex.map(q,todo)):
        if i%500==0: print(i,flush=True);json.dump(cache,open('sma_cache.json','w'))
json.dump(cache,open('sma_cache.json','w'))
import collections;print(collections.Counter(cache.values()))
