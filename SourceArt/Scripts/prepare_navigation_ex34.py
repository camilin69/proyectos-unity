"""Generate original wayfinding artwork and traceable circulation routes from the level plan."""
import json,heapq,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2]
PLAN=json.loads((ROOT/'EsneiderProtocoloLazaro/Assets/_Game/Data/LevelPlan/bunker_plan.json').read_text(encoding='utf-8-sig'))
OUT=ROOT/'SourceArt/Textures';OUT.mkdir(exist_ok=True)
FONT='C:/Windows/Fonts/arialbd.ttf'
NODES=[
 ('NAV-01','P01',16,16,0,[('PRESERVACIÓN','D03','capsule'),('PREPARACIÓN','D02','bed'),('ESCALERA B3','STA-01','stairs')]),
 ('NAV-02','P02',20,20,90,[('TABLERO LOCAL','D05','control'),('SERVICIO B3','D06','exit')]),
 ('NAV-03','P03',27,30,90,[('NAVE','D08','tools'),('TALLER','D09','tools'),('OFICINA','D10','paper'),('ESCALERA B2','STA-02','stairs')]),
 ('NAV-04','P04',22,26,90,[('ALMACÉN','D11','box'),('PATIO / AUTORIZACIÓN A','D12','control'),('PIEZAS','D13','tools'),('CONTENCIÓN','D14','shield')]),
 ('NAV-05','P05',20,28,90,[('ADMISIÓN','D19','paper'),('ALA A','D16','bed'),('ALA B','D17','bed')]),
 ('NAV-06','P05',46,28,90,[('CLÍNICA','D20','cross'),('OBSERVACIÓN','D21','eye'),('SEGURIDAD','D18','shield'),('SALIDA DE SERVICIO','D22','exit')]),
 ('NAV-07','P06',14,32,90,[('CONTROL','D24','control'),('REFUGIO','D25','bed'),('SEGURIDAD','D26','shield'),('SUPERVISIÓN','D27','eye')]),
]
def contains(r,x,z):return r['x']<=x<=r['x']+r['w'] and r['z']<=z<=r['z']+r['d']
def route(floor,start,target):
    rects=[r for r in PLAN['circulation'] if r['floor']==floor]
    def clear(p):
        x,z=p[0]/2,p[1]/2
        return all(any(contains(r,x+dx,z+dz) for r in rects) for dx,dz in [(0,0),(.12,0),(-.12,0),(0,.12),(0,-.12)])
    goal=(round(target[0]*2),round(target[1]*2));source=(round(start[0]*2),round(start[1]*2))
    assert clear(source),(floor,source,'start outside circulation')
    assert clear(goal),(floor,goal,'target outside circulation')
    delta=(goal[0]-source[0],goal[1]-source[1])
    preferred=(1 if delta[0]>0 else -1,0) if abs(delta[0])>=abs(delta[1]) else (0,1 if delta[1]>0 else -1)
    initial=(*source,0,0);todo=[(0,initial)];cost={initial:0};came={};end=None
    while todo:
        _,state=heapq.heappop(todo);p=state[:2];heading=state[2:]
        if p==goal:end=state;break
        for dx,dz in [(1,0),(-1,0),(0,1),(0,-1)]:
            q=(p[0]+dx,p[1]+dz);direction=(dx,dz);nxt=(*q,dx,dz)
            turn=0 if heading==(0,0) or heading==direction else .2
            first=1 if heading==(0,0) and direction!=preferred else 0
            g=cost[state]+1+turn+first
            if clear(q) and g<cost.get(nxt,10**9):
                cost[nxt]=g;came[nxt]=state;heapq.heappush(todo,(g+abs(q[0]-goal[0])+abs(q[1]-goal[1]),nxt))
    assert end is not None,(floor,source,goal,'no circulation route')
    states=[end]
    while states[-1]!=initial:states.append(came[states[-1]])
    path=[s[:2] for s in states]
    path.reverse();runs=[]
    for a,b in zip(path,path[1:]):
        direction=(b[0]-a[0],b[1]-a[1])
        if runs and runs[-1][0]==direction:runs[-1][1]+=.5
        else:runs.append([direction,.5])
    # Use the first substantial corridor segment, not short positioning within the junction.
    # Short local destinations retain their direct first segment; walking validation is separate.
    chosen=next((run for run in runs if run[1]>=4),runs[0])
    return [[x/2,z/2] for x,z in path],chosen[0]
def destination(target):
    if target.startswith('STA'):
        s=next(s for s in PLAN['stairs'] if s['id']==target)
        return [s['x']+s['w']/2,s['z']-.5 if s['startDir']>0 else s['z']+s['d']+.5]
    d=next(d for d in PLAN['doors'] if d['id']==target)
    # Room doors: approach from the corridor outside the room; envelope doors: inside floor.
    dx,dz={'N':(0,1),'S':(0,-1),'E':(1,0),'W':(-1,0)}[d['edge']]
    sign=1 if d['room'] else -1
    return [d['x']+dx*.5*sign,d['z']+dz*.5*sign]
def arrow(draw,cx,cy,direction,color):
    dx,dy=direction
    points=[(-30,-11),(6,-11),(6,-27),(36,0),(6,27),(6,11),(-30,11)]
    # Base arrow points right in image coordinates.
    draw.polygon([(cx+x*dx-y*dy,cy+x*dy+y*dx) for x,y in points],fill=color)
def icon(draw,kind,x,y,color):
    w=5
    if kind=='cross':draw.rectangle((x-8,y-28,x+8,y+28),fill=color);draw.rectangle((x-28,y-8,x+28,y+8),fill=color)
    elif kind=='stairs':draw.line([(x-30,y+25),(x-10,y+25),(x-10,y+5),(x+10,y+5),(x+10,y-15),(x+30,y-15)],fill=color,width=8)
    elif kind=='eye':draw.ellipse((x-34,y-20,x+34,y+20),outline=color,width=w);draw.ellipse((x-10,y-10,x+10,y+10),fill=color)
    elif kind=='bed':draw.line([(x-30,y-20),(x-30,y+27),(x-30,y+8),(x+30,y+8),(x+30,y+27)],fill=color,width=w);draw.rectangle((x-20,y-8,x+28,y+5),outline=color,width=w)
    elif kind=='shield':draw.polygon([(x-28,y-26),(x+28,y-26),(x+24,y+10),(x,y+30),(x-24,y+10)],outline=color,width=w)
    elif kind=='capsule':draw.rounded_rectangle((x-18,y-30,x+18,y+30),radius=16,outline=color,width=w);draw.line((x-16,y,x+16,y),fill=color,width=w)
    elif kind=='tools':draw.line((x-22,y+24,x+20,y-20),fill=color,width=10);draw.arc((x+3,y-34,x+36,y-1),-20,260,fill=color,width=7)
    elif kind=='control':draw.rectangle((x-30,y-23,x+30,y+15),outline=color,width=w);draw.line((x,y+15,x,y+28),fill=color,width=w);draw.line((x-17,y+28,x+17,y+28),fill=color,width=w)
    elif kind=='exit':
        # Door/person pictogram; only the dedicated direction column contains arrows.
        draw.rectangle((x-29,y-29,x+1,y+29),outline=color,width=w)
        draw.ellipse((x+9,y-25,x+23,y-11),fill=color)
        draw.line((x+16,y-8,x+16,y+10),fill=color,width=7)
        draw.line((x+16,y+8,x+7,y+29),fill=color,width=6)
        draw.line((x+16,y+8,x+28,y+29),fill=color,width=6)
    else:
        draw.rectangle((x-23,y-28,x+23,y+28),outline=color,width=w)
        for yy in (-12,0,12):draw.line((x-12,y+yy,x+12,y+yy),fill=color,width=3)
def artwork(node,back=False):
    im=Image.new('RGB',(1728,480),(210,211,193));d=ImageDraw.Draw(im);ink=(26,49,48)
    d.rectangle((0,0,1727,479),outline=ink,width=8);d.rectangle((8,8,1719,72),fill=ink)
    d.text((30,15),'NÉMESIS  /  '+node['floor'],font=ImageFont.truetype(FONT,40),fill=(234,233,210))
    d.text((1500,20),node['id'],font=ImageFont.truetype(FONT,32),fill=(234,233,210))
    rows=node['destinations'];row_h=354/len(rows)
    for i,row in enumerate(rows):
        y=int(82+row_h*(i+.5));direction=row['back_arrow'] if back else row['front_arrow']
        arrow(d,63,y,direction,ink);icon(d,row['icon'],160,y,ink)
        font=ImageFont.truetype(FONT,54 if len(rows)==4 else 66)
        d.text((226,y-font.size*.64),row['text'],font=font,fill=ink)
        d.text((1500,y-19),row['target'],font=ImageFont.truetype(FONT,34),fill=ink)
        if i<len(rows)-1:d.line((25,int(82+row_h*(i+1)),1700,int(82+row_h*(i+1))),fill=(147,156,145),width=2)
    d.rectangle((8,443,1719,471),fill=ink);d.text((28,444),'EVA / CONTINUIDAD     •     DESTINOS Y ACCESOS',font=ImageFont.truetype(FONT,22),fill=(231,229,199))
    im.save(OUT/(node['id']+('_Back' if back else '_Front')+'_EX34.png'))
def main():
    nodes=[]
    for id,floor,x,z,yaw,rows in NODES:
        f=next(f for f in PLAN['floors'] if f['id']==floor)
        node={'id':id,'asset':id+'_Orientacion','floor':floor,'region':f['region'],'x':x,'z':z,'yaw':yaw,'destinations':[]}
        for text,target,pict in rows:
            goal=destination(target);path,heading=route(floor,(x,z),goal);dx,dz=heading
            # Panel front looks toward +Z at yaw 0, toward +X at yaw 90.
            front=[dx,-dz] if yaw==0 else [-dz,-dx]
            node['destinations'].append({'text':text,'target':target,'icon':pict,'approach':goal,'route':path,'front_arrow':front,'back_arrow':[-front[0],-front[1]]})
        artwork(node);artwork(node,True);nodes.append(node)
    path=ROOT/'EsneiderProtocoloLazaro/Assets/_Game/Data/LevelPlan/navigation_signs_ex34.json'
    path.write_text(json.dumps({'source':'GDD 87.2 + bunker_plan.json circulation/doors/stairs','grid_metres':.5,'nodes':nodes},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    im=Image.new('RGB',(900,600),(197,203,183));d=ImageDraw.Draw(im);ink=(27,49,46)
    d.rectangle((8,8,891,591),outline=ink,width=14)
    for y,text,size in [(38,'NÉMESIS BIODYNAMICS',52),(110,'LÁZARO',110),(240,'SERVICIO B3',65),(335,'AISLAMIENTO LOCAL',46),(400,'CONTACTO DE RED / D06',40)]:
        font=ImageFont.truetype(FONT,size);box=d.textbbox((0,0),text,font=font);d.text(((900-box[2])/2,y),text,font=font,fill=ink)
    im.save(OUT/'OBJ-016_Front_EX34.png')
    im=Image.new('RGB',(800,150),(33,53,48));d=ImageDraw.Draw(im);d.text((25,28),'EVA / ACCESO SUPERVISADO',font=ImageFont.truetype(FONT,47),fill=(226,218,168));im.save(OUT/'OBJ-016_Overlay_EX34.png')
    print(json.dumps({'nodes':len(nodes),'routes':sum(len(n['destinations']) for n in nodes),'manifest':str(path)}))
if __name__=='__main__':main()
