"""Original admission and everyday props, including a texture-authored shift board."""
import bpy,sys,math
ROOT='C:/Users/HP/Documents/GitHub/proyectos-unity'
sys.path.insert(0,ROOT+'/SourceArt/Scripts')
import esn_lib as L
from build_clinic_fixtures_ex23 import FixtureBuilder
from esn_delivery import Batch
ASSETS={'040':'TazaTermo','040B':'TazaTermoRota','058':'AtrilAdmision','063':'PizarraTurnos','064':'ContenedorClinico'}
BATCH=Batch('EX-27',ASSETS)

def lathe(b,name,profile,center,mat,segments=32):
    verts=[];faces=[]
    for radius,z in profile:
        for j in range(segments):
            a=math.tau*j/segments
            notch=.019*max(0,1-abs(j-segments*.75)/2.5) if b.id=='040B' and name=='cup' and z>=.085 else 0
            verts.append((center[0]+radius*math.cos(a),center[1]+radius*math.sin(a),z-notch))
    for k in range(len(profile)-1):
        for j in range(segments):
            a=k*segments+j;nextj=k*segments+(j+1)%segments;faces.append((a,nextj,nextj+segments,a+segments))
    if profile[0][0]<=.001:faces.append(tuple(range(segments-1,-1,-1)))
    if profile[-1][0]<=.001:faces.append(tuple((len(profile)-1)*segments+j for j in range(segments)))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new('GEO-'+b.id+'-'+name,mesh);b.col.objects.link(obj);L.assign(obj,b.m[mat]);b.parts.append(obj)

def cups(b):
    b.features=['open cup with interior wall and thick base','connected loop handle','intact vacuum flask with neck and sealed cap','localized protected cup finish']
    lathe(b,'cup',[(.001,0),(.032,0),(.039,.005),(.041,.085),(.039,.09),(.035,.09),(.034,.012),(.001,.012)],(-.10,0),'ceramic',24)
    # Fixed radial frame avoids a tube-frame flip as the handle crosses vertical.
    hv=[];hf=[]
    for i in range(13):
        a=math.radians(70+i*220/12)
        for j in range(8):
            q=math.tau*j/8;r=.025+.006*math.cos(q)
            hv.append((-.145+r*math.cos(a),.006*math.sin(q),.049+r*math.sin(a)))
    for i in range(12):
        for j in range(8):hf.append((i*8+j,i*8+(j+1)%8,(i+1)*8+(j+1)%8,(i+1)*8+j))
    hf.extend([tuple(range(7,-1,-1)),tuple(96+j for j in range(8))])
    hm=bpy.data.meshes.new('rounded cup handle');hm.from_pydata(hv,[],hf);hm.update()
    handle=bpy.data.objects.new('GEO-'+b.id+'-cup_handle',hm);b.col.objects.link(handle);L.assign(handle,b.m['ceramic']);b.parts.append(handle)
    verts=[];faces=[]
    for k in range(2):
        for j in range(9):
            a=math.radians(60+j*15);z=.071+k*.006+.001*math.sin(j*2)
            radius=.034+(z-.012)/.078*.001-.0001
            verts.append((-.10+radius*math.cos(a),radius*math.sin(a),z))
    for j in range(8):faces.append((j,j+9,j+10,j+1))
    mesh=bpy.data.meshes.new('localized tea stain');mesh.from_pydata(verts,[],faces);mesh.update()
    stain=bpy.data.objects.new('GEO-'+b.id+'-interior_stain',mesh);b.col.objects.link(stain);L.assign(stain,b.m['stain']);b.parts.append(stain)
    lathe(b,'thermos_body',[(.001,0),(.038,0),(.043,.015),(.043,.201),(.034,.218),(.029,.222),(.001,.222)],(.075,0),'steel',24)
    b.cyl('thermal_base',.044,.012,(.075,0,.006),'dark','Z',24)
    b.cyl('sealed_lid',.033,.028,(.075,0,.236),'paint','Z',24)
    b.cyl('lid_seam',.034,.004,(.075,0,.224),'dark','Z',24)
    b.collision=[]

def lectern(b):
    b.features=['weighted pedestal','raked folder support','mounted folder and pages','spring clip and registration control','visible document lip']
    b.box('base',(.52,.44,.045),(0,0,.0225),'paint',.013,True)
    b.box('pedestal',(.10,.12,.98),(0,.04,.535),'steel',.008,True)
    b.box('support_brace',(.32,.20,.055),(0,.04,1.03),'paint',.008)
    slope=.25
    b.box('reading_support',(.60,.48,.035),(0,0,1.12),'ivory',.013,rot=(slope,0,0))
    b.box('folder_cover',(.40,.33,.009),(-.055,-.015,1.141),'paint',.004,rot=(slope,0,0))
    b.box('paper_stack',(.355,.288,.008),(-.055,-.015,1.15),'paper',.002,rot=(slope,0,0))
    b.box('spring_clip',(.125,.036,.014),(-.055,.114,1.19),'steel',.003,rot=(slope,0,0))
    b.box('lower_lip',(.55,.017,.030),(0,-.225,1.075),'steel',.003)
    b.box('registration_control',(.065,.083,.023),(.231,-.02,1.148),'dark',.007,rot=(slope,0,0))
    b.collision.append({'center':[0,0,1.12],'size':[.6,.49,.16]})

def board(b):
    b.features=['framed whiteboard','original readable shift annotations','overwritten indefinite extension notice','marker tray and two pens','wall backing plate']
    b.box('backing',(1.2,.035,.8),(0,0,.4),'paint',.006)
    b.box('writing_surface',(1.12,.005,.72),(0,-.02,.4),'writing',.001)
    for x in (-.585,.585):b.box('frame_side',(.03,.036,.8),(x,-.012,.4),'steel',.003)
    for z in (.015,.785):b.box('frame_end',(1.14,.036,.03),(0,-.012,z),'steel',.003)
    b.box('pen_tray',(.55,.072,.018),(0,-.04,.026),'ivory',.004)
    for x in (-.12,.08):b.cyl('marker',.006,.12,(x,-.059,.043),'dark','X',10)
    b.collision=[]

def waste(b):
    b.features=['rounded polymer shell','opaque bag liner folds beneath lid','closed lid with hinge and latch','recessed carry handles and sanitary label']
    b.box('shell',(.38,.28,.53),(0,0,.285),'ivory',.04,True)
    b.box('floor_rim',(.39,.29,.025),(0,0,.0125),'dark',.012)
    # Loose opaque liner edge folds between shell and lid, not a painted box.
    lathe(b,'bag_liner',[(.12,.49),(.155,.535),(.153,.56),(.135,.548)],(0,0),'dark',24)
    for j in range(9):
        a=math.tau*j/9;b.tube('liner_crease',[(.13*math.cos(a),.12*math.sin(a),.505),(.175*math.cos(a),.126*math.sin(a),.54),(.16*math.cos(a),.12*math.sin(a),.555)],.004,'dark')
    b.box('lid',(.40,.30,.041),(0,0,.5795),'paint',.015)
    b.box('sealed_liner_rim',(.391,.291,.022),(0,0,.549),'dark',.008)
    b.cyl('rear_hinge',.014,.23,(0,.14,.548),'steel','X',16)
    b.box('front_latch',(.085,.025,.058),(0,-.148,.548),'steel',.006)
    for x in (-.191,.191):b.box('recessed_grip',(.005,.11,.032),(x,0,.43),'dark',.005)
    b.box('sanitary_plate',(.20,.003,.15),(0,-.141,.32),'label',.004)
    b.box('cross_vertical',(.014,.002,.062),(0,-.144,.335),'paint',.001)
    b.box('cross_horizontal',(.060,.002,.015),(0,-.144,.335),'paint',.001)
    b.collision=[{'center':[0,0,.30],'size':[.40,.30,.60]}]

def build(id):
    b=FixtureBuilder(id,ASSETS[id],'EX27')
    b.m['ceramic']=L.material(b.asset+'_ceramic',(.52,.55,.47),.25,0)
    b.m['paper']=L.material(b.asset+'_paper',(.68,.65,.53),.9,0)
    b.m['stain']=L.material(b.asset+'_stain',(.12,.073,.035),.68,0)
    b.m['writing']=L.material(b.asset+'_writing',(.6,.63,.55),.72,0)
    if id in ('063','058'):
        mat=b.m['writing' if id=='063' else 'paper'];nodes=mat.node_tree.nodes;links=mat.node_tree.links
        filename='EX27_ShiftBoard.png' if id=='063' else 'EX27_AdmissionRecord.png'
        tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(ROOT+'/SourceArt/Textures/'+filename,check_existing=True);tex.image.pack()
        geo=nodes.new('ShaderNodeNewGeometry');sep=nodes.new('ShaderNodeSeparateXYZ');links.new(geo.outputs['Position'],sep.inputs[0])
        combine=nodes.new('ShaderNodeCombineXYZ')
        projection=[('X',-.56,.56,'X'),('Z',.04,.76,'Y')] if id=='063' else [('X',-.2325,.1225,'X'),('Y',-.1545,.1245,'Y')]
        for coord,low,high,out in projection:
            remap=nodes.new('ShaderNodeMapRange');remap.inputs['From Min'].default_value=low;remap.inputs['From Max'].default_value=high
            links.new(sep.outputs[coord],remap.inputs['Value']);links.new(remap.outputs[0],combine.inputs[out])
        links.new(combine.outputs[0],tex.inputs['Vector']);shader=next(n for n in nodes if n.type=='BSDF_PRINCIPLED');links.new(tex.outputs['Color'],shader.inputs['Base Color'])
    {'040':cups,'040B':cups,'058':lectern,'063':board,'064':waste}[id](b)
    return BATCH.save(b)
def render(id):return BATCH.render(id)
def finish(id):return BATCH.finish(id,size=512 if id.startswith('040') else 1024)
