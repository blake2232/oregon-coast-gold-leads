import requests,json,re,collections
D={'Galice':'Galice, Oregon','Waldo':'Waldo, Oregon','Althouse':'Holland, Oregon','Jacksonville':'Jacksonville, Oregon','Gold Hill':'Gold Hill, Oregon',
'Upper Applegate':'Applegate River','Sixes River':'Sixes River','Gold Beach':'Gold Beach, Oregon','Myrtle Creek':'Myrtle Creek, Oregon','Greenback':'Greenback Mine',
'Illinois River':'Kerby, Oregon','Mule Creek':'Mule Creek (Oregon)','Takilma-Waldo':'Takilma, Oregon','Riddle':'Riddle, Oregon','Grants Pass':'Grants Pass, Oregon','Ashland':'Ashland, Oregon','Beach Area':'Whiskey Run'}
mi=json.load(open('milo.json'));g=collections.defaultdict(list)
for x in mi:
    if x['Type']=='metal' and x['Latitude']: g[x['MiningDistrict']].append(x)
out=[]
for d,t in D.items():
    pts=g.get(d,[])
    r=requests.get('https://en.wikipedia.org/w/api.php',params=dict(action='query',prop='extracts|coordinates',explaintext=1,titles=t,format='json',redirects=1),headers={'User-Agent':'gold-app/1.0'}).json()
    pg=list(r['query']['pages'].values())[0];txt=pg.get('extract','') or ''
    sents=[s.strip() for s in re.split(r'(?<=[.!?])\s+',txt.replace('\n',' ')) if re.search(r'\b(gold|placer|mining|miners?|hydraulic)\b',s,re.I)][:3]
    title=pg.get('title') if txt else None
    if pts: lat=sum(p['Latitude'] for p in pts)/len(pts);lon=sum(p['Longitude'] for p in pts)/len(pts);how=f'centroid of {len(pts)} DOGAMI MILO-4 metal sites in this district (approximate)'
    elif pg.get('coordinates'): lat,lon=pg['coordinates'][0]['lat'],pg['coordinates'][0]['lon'];how='Wikipedia coordinates of '+title+' (approximate district center)'
    else: print('skip',d);continue
    gold=sum('gold' in (p['Commodity'] or '').lower() for p in pts)
    out.append(dict(name=d,lat=round(lat,5),lon=round(lon,5),how=how,n=len(pts),ngold=gold,history=' '.join(sents)[:700],
      links=([['Wikipedia: '+title,'https://en.wikipedia.org/wiki/'+title.replace(' ','_')]] if title and sents else [])+[['DOGAMI MILO-4','https://www.oregon.gov/dogami/pubs/Pages/dds/p-MILO-4.aspx']]))
    print(d,len(pts),gold,title,bool(sents),out[-1]['history'][:150])
json.dump(out,open('districts.json','w'))
