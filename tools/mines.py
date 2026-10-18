import csv,json,math,re
C=('Josephine','Jackson','Curry','Douglas','Coos')
mr=[x for x in csv.DictReader(open('mrds.csv',encoding='latin1')) if x['state']=='Oregon' and x['county'] in C and x['com_type'] in('M','B')]
mi=[x for x in json.load(open('milo.json')) if x['Type']=='metal' and x['Latitude']]
P=('gold','silver','platinum')
out=[]
def prec(c): return any(p in (c or '').lower() for p in P)
for x in mi:
    c=x['Commodity'] or ''
    prod=[f"{k}: {x[k]}" for k in('CommoditiesProduced','ProductSize','ProductInformation','WorkingsType','WorkingsDescription','YearOfDiscovery','YearProductionStarted') if x[k] and x[k] not in('no data','unnamed or NA')]
    out.append(dict(id='MILO-'+x['MILO_ID'],src='DOGAMI MILO-4',name=x['SiteName'],lat=round(x['Latitude'],5),lon=round(x['Longitude'],5),county=x['County'],
      commod=c,prec=prec(c),status=None,district=None if x['MiningDistrict']=='unnamed or NA' else x['MiningDistrict'],notes='; '.join(prod),
      ref=x['ShortReference1'],links=[['DOGAMI MILO-4','https://www.oregon.gov/dogami/pubs/Pages/dds/p-MILO-4.aspx']]))
# merge MRDS: if a MILO point within 150 m with same first name token, attach
def key(n): return re.sub('[^a-z]','',(n or '').lower().split(' ')[0]) if n else ''
def full(n): return re.sub('(placers?|mine|mines|group|claims?)','',re.sub('[^a-z]','',(n or '').lower()))
grid={}
for i,o in enumerate(out): grid.setdefault((round(o['lat'],2),round(o['lon'],2)),[]).append(i)
merged=0
for x in mr:
    la,lo=float(x['latitude']),float(x['longitude']);c=', '.join(v for v in(x['commod1'],x['commod2'],x['commod3']) if v)
    hit=None
    for dy in(-.01,0,.01):
        for dx in(-.01,0,.01):
            for i in grid.get((round(la+dy,2),round(lo+dx,2)),[]):
                o=out[i]
                dd=math.hypot((o['lat']-la)*111e3,(o['lon']-lo)*81e3)
                if 'mrds' not in o and ((dd<150 and key(o['name'])==key(x['site_name'])) or (dd<600 and full(o['name'])==full(x['site_name']))): hit=o
    prod=[f"{k}: {x[k]}" for k in('prod_size','prod_yrs','yr_fst_prd','yr_lst_prd','work_type','dep_type') if x[k]]
    if hit and 'mrds' not in hit:
        hit['mrds']=1;hit['status']=x['dev_stat'];hit['links'].append(['USGS MRDS '+x['dep_id'],x['url']]);hit['src']+=' + USGS MRDS'
        if prod: hit['notes']+=(' | MRDS: ' if hit['notes'] else 'MRDS: ')+'; '.join(prod)
        merged+=1;continue
    out.append(dict(id='MRDS-'+x['dep_id'],src='USGS MRDS',name=x['site_name'],lat=round(la,5),lon=round(lo,5),county=x['county'],commod=c,prec=prec(c),status=x['dev_stat'],
      district=None,notes='; '.join(prod),ref=x['ref'][:200],links=[['USGS MRDS '+x['dep_id'],x['url']]]))
for o in out: o.pop('mrds',None)
json.dump(out,open('mines.json','w'))
print(len(mr),len(mi),merged,len(out),sum(o['prec'] for o in out))
