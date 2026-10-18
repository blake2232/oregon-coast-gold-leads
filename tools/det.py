import rasterio,numpy as np,json,math
from scipy import ndimage as nd
from skimage import morphology,measure
from pyproj import Transformer
from PIL import Image,ImageDraw
tr=Transformer.from_crs(26910,4326,always_xy=True)
mines=json.load(open('mines.json'))
def hs(z,az,alt=45):
    gy,gx=np.gradient(z);s=np.arctan(np.hypot(gx,gy));a=np.arctan2(-gx,gy)
    az,alt=np.radians(az),np.radians(alt)
    return np.clip(np.sin(alt)*np.cos(s)+np.cos(alt)*np.sin(s)*np.cos(az-a),0,1)
out=[]
for k in ['mulecreek','josephine','sucker','upper_applegate']:
    d=rasterio.open(f'lidar/{k}.tif');z=d.read(1).astype('f8');T=d.transform
    bad=z<-100;z[bad]=np.nan;z=np.where(np.isnan(z),np.nanmean(z),z);badb=nd.binary_dilation(bad,iterations=60)
    # resolution sanity: fraction of 1m-scale variation
    sl=np.degrees(np.arctan(np.hypot(*np.gradient(z))))
    lrm=z-nd.gaussian_filter(z,15)
    rough=nd.generic_filter(lrm[::2,::2],np.std,size=7);rough=np.kron(rough,np.ones((2,2)))[:z.shape[0],:z.shape[1]]
    regsl=nd.uniform_filter(sl,61)
    # depressions
    seed=z.copy();seed[1:-1,1:-1]=z.max()
    filled=morphology.reconstruction(seed,z,method='erosion');dep=filled-z
    H=(hs(z,315)+hs(z,45)+hs(z,135))/3
    np.save(f'lidar/{k}_hs.npy',H.astype('f2'))
    cands=[]
    lab=measure.label((dep>1.0)&~badb)
    for r in measure.regionprops(lab,intensity_image=dep):
        if 150<r.area<30000: cands.append(('closed depression / possible hydraulic pit or pond',r.centroid,float(r.intensity_max),r.area,r.intensity_max*min(r.area,3000)**.5/10))
    t=np.percentile(rough,97);lab=measure.label(morphology.remove_small_objects((rough>t)&(regsl<15)&~badb,400))
    for r in measure.regionprops(lab):
        if r.area<60000 and r.eccentricity<0.93: cands.append(('hummocky high-roughness ground on low slope / possible tailings piles',r.centroid,float(rough[lab==r.label].mean()),r.area,float(rough[lab==r.label].mean())*math.sqrt(r.area)/3))
    neg=morphology.remove_small_objects((lrm<-0.35)&(sl>12)&(sl<40)&~badb,80);lab=measure.label(neg)
    for r in measure.regionprops(lab):
        if r.axis_major_length>100 and r.axis_minor_length<15: cands.append(('long narrow contour-following trench / possible ditch (or road/skid trail)',r.centroid,float(r.axis_major_length),r.area,r.axis_major_length/60))
    cands.sort(key=lambda c:-c[4]);sel=[]
    for c in cands:
        if all(math.hypot(c[1][0]-s[1][0],c[1][1]-s[1][1])>250 for s in sel) and 150<c[1][0]<1850 and 150<c[1][1]<1850: sel.append(c)
        if len(sel)==8: break
    # best type diversity: ensure at least one of each type if available
    print(k,len(cands),'fine-scale sd',float(np.std(lrm)))
    for i,(typ,(r,c),m,a,sc) in enumerate(sel,1):
        x,y=T*(c,r);lon,lat=tr.transform(x,y)
        nm=min(mines,key=lambda o:(o['lat']-lat)**2+((o['lon']-lon)*.74)**2);dist=math.hypot((nm['lat']-lat)*111e3,(nm['lon']-lon)*82e3)
        r0,c0=int(r),int(c);w=200
        crop=H[max(r0-w,0):r0+w,max(c0-w,0):c0+w];im=Image.fromarray((crop*255).astype('u1')).convert('RGB').resize((600,600))
        dr=ImageDraw.Draw(im);dr.ellipse([270,270,330,330],outline=(255,60,0),width=3);dr.text((8,8),f'{k} S{i} 400x400 m hillshade, 3DEP 1 m',fill=(255,255,0))
        fn=f'sw_{k}_{i}';im.save(f'/workspace/gold_app/img/{fn}.jpg',quality=80)
        out.append(dict(id=f'SW-{k}-{i}',aoi=k,type=typ,lat=round(lat,5),lon=round(lon,5),metric=round(m,2),area=int(a),score=round(float(sc),2),img=f'img/{fn}.jpg',nearest=nm['name'],nearest_m=int(dist)))
        print(' ',out[-1])
json.dump(out,open('lidar_cands.json','w'))
