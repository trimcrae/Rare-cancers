import zlib, struct, numpy as np
p='/home/user/Rare-cancers/research/manuscripts/figures/repurposing-fig1-design.png'
d=open(p,'rb').read(); assert d[:8]==b'\x89PNG\r\n\x1a\n'
i=8; idat=b''; 
while i<len(d):
    ln=struct.unpack('>I',d[i:i+4])[0]; typ=d[i+4:i+8]; data=d[i+8:i+8+ln]
    if typ==b'IHDR':
        w,h,bd,ct,cm,fl,il=struct.unpack('>IIBBBBB',data); print('IHDR',w,h,'bitdepth',bd,'colortype',ct,'interlace',il)
    elif typ==b'IDAT': idat+=data
    elif typ==b'tEXt': print('tEXt:',data[:200])
    i+=12+ln
raw=zlib.decompress(idat)
nc={0:1,2:3,3:1,4:2,6:4}[ct]; bpp=nc*bd//8; stride=w*bpp
img=np.zeros((h,stride),dtype=np.uint8); pos=0; prev=np.zeros(stride,dtype=np.uint8)
for y in range(h):
    f=raw[pos]; pos+=1
    line=np.frombuffer(raw[pos:pos+stride],dtype=np.uint8).copy(); pos+=stride
    if f==1:
        for x in range(bpp,stride): line[x]=(line[x]+line[x-bpp])&255
    elif f==2: line=(line+prev)&255
    elif f==3:
        for x in range(stride):
            a=int(line[x-bpp]) if x>=bpp else 0
            line[x]=(int(line[x])+((a+int(prev[x]))>>1))&255
    elif f==4:
        for x in range(stride):
            a=int(line[x-bpp]) if x>=bpp else 0
            c=int(prev[x-bpp]) if x>=bpp else 0
            b=int(prev[x]); pp=a+b-c
            pa,pb,pc=abs(pp-a),abs(pp-b),abs(pp-c)
            pr=a if (pa<=pb and pa<=pc) else (b if pb<=pc else c)
            line[x]=(int(line[x])+pr)&255
    img[y]=line; prev=line
arr=img.reshape(h,w,nc)
gray=arr[:,:,0] if nc<3 else arr[:,:,:3].mean(2).astype(np.uint8)
def save(name,x0,y0,x1,y1,scale):
    sub=gray[y0:y1,x0:x1]
    sub=np.repeat(np.repeat(sub,scale,0),scale,1)
    hh,ww=sub.shape
    rows=b''.join(b'\x00'+sub[y].tobytes() for y in range(hh))
    def chunk(t,dat): 
        return struct.pack('>I',len(dat))+t+dat+struct.pack('>I',zlib.crc32(t+dat)&0xffffffff)
    out=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',ww,hh,8,0,0,0,0))+chunk(b'IDAT',zlib.compress(rows))+chunk(b'IEND',b'')
    open(name,'wb').write(out); print('wrote',name,ww,hh)
save('/tmp/claude-0/u2-lane/crop-catalogue.png',1120,420,1880,560,2)
save('/tmp/claude-0/u2-lane/crop-firewall-edge.png',1650,780,2050,890,4)
