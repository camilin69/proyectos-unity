"""Original utility fixtures and 2/4 metre installation modules, via Blender MCP."""
import bpy,sys,math,os,json,shutil
ROOT='C:/Users/HP/Documents/GitHub/proyectos-unity'
sys.path.insert(0,ROOT+'/SourceArt/Scripts')
import esn_lib as L
from build_clinic_fixtures_ex23 import FixtureBuilder
from esn_delivery import Batch
ASSETS={'065':'AltavozMegafonia','066':'LuminariaTecnica','067':'LamparaEmergencia','068':'BandejaCables2m','068B':'BandejaCables4m','069':'Conducto2m','069B':'Conducto4m','069C':'RejillaTerminal'}
BATCH=Batch('EX-31',ASSETS)

def speaker(b):
    b.features=['weather housing','raised grille strips and dark acoustic backing','wall yoke and anchors','repaired cable loop']
    b.box('housing',(.36,.23,.25),(0,-.02,.125),'paint',.01)
    b.box('grille_backing',(.325,.004,.184),(0,-.137,.125),'dark',.001)
    for i in range(11):b.box('grille_slat',(.325,.008,.005),(0,-.146,.043+i*.0164),'steel',0)
    for x in (-.166,.166):b.box('grille_rim',(.008,.008,.195),(x,-.146,.125),'steel',.001)
    b.box('wall_mount',(.40,.020,.05),(0,.14,.125),'steel',.001,True)
    for x in (-.187,.187):
        b.box('yoke',(.026,.16,.09),(x,.05,.125),'steel',.001)
        b.cyl('pivot',.021,.018,(x,0,.125),'dark','X',12)
    b.tube('service_cable',[(.08,.095,.10),(.09,.12,.03),(.13,.139,.04),(.13,.14,.11)],.006,'dark')
    b.box('new_cable_tape',(.015,.018,.028),(.088,.12,.034),'ivory',.001)

def luminaire(b):
    b.features=['enclosed ceiling housing','underside diffuser','protective end rims','ceiling clips with screws','short supply lead']
    b.box('housing',(.80,.20,.075),(0,0,.0725),'paint',.008)
    b.box('diffuser',(.73,.163,.042),(0,0,.027),'glow',.008)
    for x in (-.385,.385):b.box('end_rim',(.03,.20,.045),(x,0,.0225),'steel',.002)
    for x in (-.25,.25):
        b.box('ceiling_clip',(.08,.13,.04),(x,0,.13),'steel',.001)
        for y in (-.045,.045):b.cyl('ceiling_screw',.008,.003,(x,y,.149),'steel','Z',10)
    b.tube('supply',[(.0,.025,.11),(.05,.045,.132),(.14,.045,.135),(.20,.025,.135)],.006,'dark')
    b.collision=[]

def emergency(b):
    b.features=['wall plate and sealed body','amber lens','raised directional arrow independent of colour','small service label']
    b.box('body',(.30,.065,.12),(0,.040,.06),'paint',.008)
    b.box('wall_bracket',(.24,.008,.085),(0,.071,.06),'steel',.001)
    b.box('seal',(.27,.017,.095),(0,-.003,.06),'dark',.009)
    b.box('amber_lens',(.26,.068,.084),(0,-.041,.06),'glow',.014)
    verts=[(-.09,-.0756,.05),(.03,-.0756,.05),(.03,-.0756,.037),(.09,-.0756,.06),(.03,-.0756,.083),(.03,-.0756,.07),(-.09,-.0756,.07)]
    mesh=bpy.data.meshes.new('directional arrow');mesh.from_pydata(verts,[],[tuple(range(7))]);mesh.update()
    obj=bpy.data.objects.new('GEO-067-direction',mesh);b.col.objects.link(obj);L.assign(obj,b.m['dark']);b.parts.append(obj)
    b.box('service_label',(.08,.001,.013),(-.082,-.004,.110),'label',0)
    b.collision=[]

def tray(b):
    length=4 if b.id.endswith('B') else 2
    b.features=['two continuous folded rails','cross rails','four insulated cable runs','ceiling suspension brackets','coupling plates and cable ties']
    for y in (-.215,.215):
        b.box('side_rail',(length,.020,.12),(0,y,.14),'steel',.001)
        b.box('rail_return',(length,.04,.01),(0,y*.94,.085),'steel',0)
    for i in range(length*3+1):b.box('cross_rail',(.025,.43,.018),(-length/2+.0125+i*(length-.025)/(length*3),0,.077),'steel',0)
    for i,y in enumerate((-.13,-.044,.044,.13)):b.cyl('insulated_cable',.020,length,(0,y,.126),'dark' if i%2==0 else 'cable','X',8)
    for x in ([-length/2+.25,0,length/2-.25] if length==4 else [-.75,.75]):
        b.box('ceiling_plate',(.075,.5,.018),(x,0,.341),'steel',0)
        for y in (-.23,.23):b.box('suspension',(.023,.023,.20),(x,y,.24),'steel',0)
        b.box('tie',(.018,.33,.012),(x,0,.147),'ivory',0)
    for x in (-length/2+.04,length/2-.04):
        for y in (-.228,.228):b.box('coupling_plate',(.08,.006,.07),(x,y,.145),'steel',0)
    for obj in b.parts:obj.location.z-=.068
    b.collision=[]

def duct(b):
    length=4 if b.id.endswith('B') else 2
    b.features=['hollow folded duct','end flange rings','mid seam','two supported ceiling straps','open ends intended for joined runs']
    for y in (-.294,.294):b.box('side_wall',(length,.012,.6),(0,y,.33),'steel',.001)
    for z in (.036,.624):b.box('horizontal_wall',(length,.576,.012),(0,0,z),'steel',.001)
    for x in (-length/2+.015,0,length/2-.015):
        for y in (-.315,.315):b.box('flange_side',(.030,.030,.66),(x,y,.33),'steel',.001)
        for z in (.015,.645):b.box('flange_cap',(.030,.60,.030),(x,0,z),'steel',.001)
    for x in ([-length/2+.3,0,length/2-.3] if length==4 else [-.7,.7]):
        for y in (-.313,.313):b.box('strap',(.032,.022,.69),(x,y,.425),'paint',0)
        b.box('ceiling_anchor',(.07,.74,.02),(x,0,.78),'steel',0)
        b.box('cradle',(.035,.648,.02),(x,0,.079),'paint',0)
    b.collision=[{'center':[0,0,.33],'size':[length,.66,.66]}]

def terminal(b):
    b.features=['closed grille terminal for duct ends','perimeter flange','angled overlapping louvres','dark mesh backing']
    for y in (-.315,.315):b.box('flange_side',(.10,.030,.66),(0,y,.33),'steel',.001)
    for z in (.015,.645):b.box('flange_cap',(.10,.60,.030),(0,0,z),'steel',.001)
    b.box('backing',(.006,.59,.59),(.041,0,.33),'dark',0)
    for i in range(9):b.box('louvre',(.074,.59,.019),(0,0,.07+i*.065),'paint',.001,rot=(0,.35,0))
    b.collision=[{'center':[0,0,.33],'size':[.10,.66,.66]}]

def build(id):
    b=FixtureBuilder(id,ASSETS[id],'EX31')
    b.m['glow']=L.material(b.asset+'_diffuser',(.80,.73,.54) if id=='066' else (.82,.32,.055),.3,0)
    b.m['cable']=L.material(b.asset+'_cable',(.055,.08,.09),.75,0)
    {'065':speaker,'066':luminaire,'067':emergency,'068':tray,'068B':tray,'069':duct,'069B':duct,'069C':terminal}[id](b)
    return BATCH.save(b)

def render(id):
    if id!='069C':return BATCH.render(id)
    obj=next(o for o in BATCH.activate(id).objects if o.type=='MESH');old=obj.rotation_euler.copy();obj.rotation_euler.z+=math.pi
    bpy.context.view_layer.update()
    try:return BATCH.render(id)
    finally:obj.rotation_euler=old;bpy.context.view_layer.update()

def finish(id):
    size=512 if id in ('065','066','067') else 1024
    maps=BATCH.finish(id,size=size)
    if id not in ('066','067'):return maps
    scene=BATCH.activate(id);obj=next(o for o in scene.objects if o.type=='MESH');original=list(obj.data.materials)
    white=L.material('EX31_mask_white',(1,1,1),1,0);black=L.material('EX31_mask_black',(0,0,0),1,0)
    old=L.TEX_DIR;L.TEX_DIR=BATCH.folder(id)+'/staging'
    try:
        for i,mat in enumerate(original):obj.data.materials[i]=white if '_diffuser' in mat.name else black
        mask=L.bake_pbr([obj],BATCH.asset(id)+'_Glow',size=size,samples=1,only=['BaseColor'])['BaseColor']
    finally:
        for i,mat in enumerate(original):obj.data.materials[i]=mat
        L.TEX_DIR=old
    path=ROOT+'/EsneiderProtocoloLazaro/Assets/_Game/Art/Textures/'+BATCH.asset(id)+'_Emission.png';shutil.copy2(mask,path)
    img=bpy.data.images.load(mask,check_existing=False);img.pack();node=original[0].node_tree.nodes.new('ShaderNodeTexImage');node.image=img;node.label='Runtime emission mask'
    bpy.data.libraries.write(ROOT+'/SourceArt/Blender/'+BATCH.asset(id)+'.blend',{scene},fake_user=True)
    maps['Emission']=mask
    with open(BATCH.folder(id)+'/bake.json','w') as f:json.dump(maps,f,indent=2)
    return maps
