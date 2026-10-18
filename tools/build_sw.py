import json,re
L={'USFS':'USFS','BLM':'BLM','ST':'State','PVT':'Private/Unknown','UND':'Undetermined','LG':'Local gov','BIA':'Tribal (BIA)','USACE':'USACE'}
c=json.load(open('sma_cache.json'))
land=lambda la,lo:L.get(c.get(f'{round(la,5)},{round(lo,5)}'),'Not checked')
LEG={'BLM':'BLM land: casual-use panning is generally allowed except on withdrawn lands or active claims. Check MLRS for claims. Placer work in streams must follow Oregon DSL/ODFW rules.',
'USFS':'National Forest: recreational panning is generally OK outside wilderness/withdrawn areas and active claims. Anything beyond casual use needs a Notice of Intent. Check MLRS claims.',
'State':'State land: permit needed. No digging in state parks.','Private/Unknown':'Private or unknown ownership: written landowner permission is required. No trespassing.'}
m=json.load(open('mines.json'));M=[]
for o in m:
    ld=land(o['lat'],o['lon']);prod=(o['status'] or '').find('Producer')>=0 or 'CommoditiesProduced' in o['notes']
    conf='high' if o['prec'] and prod else 'medium' if o['prec'] else 'low'
    M.append([o['id'],o['name'] or '(unnamed)',o['lat'],o['lon'],o['county'],o['commod'],o['status'] or '',o['district'] or '',o['notes'][:400],o['src'],o['links'],ld,conf,(o['ref'] or '')[:160]])
D=[]
for d in json.load(open('districts.json')):
    h=re.sub(r'==+[^=]+==+',' ',d['history']);s=[x.strip() for x in re.split(r'(?<=[.!?])\s+',h) if re.search(r'\b(gold|placer|hydraulic|mining|miners?|mines?)\b',re.sub(r'Gold (Hill|Beach)','',x),re.I)]
    hist=' '.join(x for x in s if not re.search(r'20[0-2][0-9]',x))[:500] or 'No sourced narrative found yet.'
    D.append(dict(d,history=hist,land=land(d['lat'],d['lon'])))
S=[]
for o in json.load(open('lidar_final.json')):
    ld=land(o['lat'],o['lon'])
    S.append(dict(id=o['id'],cat='swlidar',area='SW Oregon / '+o['aoi'].replace('_',' ').title(),name=f"{o['aoi'].replace('_',' ').title()} lidar {o['id'][-1]}: {o['type'].split('/')[1].strip() if '/' in o['type'] else o['type']}",
      lat=o['lat'],lon=o['lon'],conf=o['conf'],owner=ld+' (BLM SMA)',land=ld,img=o['img'],src=[['USGS 3DEP 1 m DEM','https://apps.nationalmap.gov/downloader/']],
      desc=f"Automated detection on USGS 3DEP 1 m DEM ({o['type']}; metric {o['metric']}, area {o['area']} m²). Nearest recorded site: {o['nearest']} ({o['nearest_m']} m). Not verified in the field. Many look-alikes are roads, skid trails or natural channels.",legal=LEG.get(ld,LEG['Private/Unknown'])))
open('/workspace/gold_app/sw_data.js','w').write('window.SWMINES='+json.dumps(M,separators=(',',':'))+';\nwindow.DISTRICTS='+json.dumps(D)+';\nwindow.SWLIDAR='+json.dumps(S)+';')
import collections;print(len(M),collections.Counter(x[11] for x in M),collections.Counter(x[12] for x in M),len(D),len(S),[ (d['name'],d['history'][:60]) for d in D])
