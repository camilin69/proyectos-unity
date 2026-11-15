"""Open ammunition cases: persistent shell and separately hideable contents, Blender MCP."""
import bpy,sys,os,json,math,shutil
from mathutils import Vector,Matrix
ROOT='C:/Users/HP/Documents/GitHub/proyectos-unity'
sys.path.insert(0,ROOT+'/SourceArt/Scripts')
import esn_lib as L
from build_clinic_fixtures_ex23 import FixtureBuilder
ASSETS={'027':'CajaMunicionPistola','027B':'CajaMunicionEscopeta'}
SCENES={}
def asset(id):return 'OBJ-'+id+'_'+ASSETS[id]
def folder(id):return ROOT+'/SourceArt/_evidence/EX-33/'+asset(id)
def label_material(b,key,kind,x,z,w,h):
    mat=L.material(b.asset+'_'+key,(.5,.5,.4),.8,0,edge_wear=0)
    n=mat.node_tree.nodes;l=mat.node_tree.links
    tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(ROOT+'/SourceArt/Textures/EX33_'+kind+'.png',check_existing=True);tex.image.pack()
    geo=n.new('ShaderNodeNewGeometry');sep=n.new('ShaderNodeSeparateXYZ');l.new(geo.outputs['Position'],sep.inputs[0]);comb=n.new('ShaderNodeCombineXYZ')
    for coord,low,high,out in [('X',x-w/2,x+w/2,'X'),('Z',z-h/2,z+h/2,'Y')]:
        remap=n.new('ShaderNodeMapRange');remap.inputs['From Min'].default_value=low;remap.inputs['From Max'].default_value=high
        l.new(sep.outputs[coord],remap.inputs['Value']);l.new(remap.outputs[0],comb.inputs[out])
    l.new(comb.outputs[0],tex.inputs['Vector']);l.new(tex.outputs['Color'],next(t for t in n if t.type=='BSDF_PRINCIPLED').inputs['Base Color']);b.m[key]=mat

def build(id):
    b=FixtureBuilder(id,ASSETS[id],'EX33');groups=[];shot=id.endswith('B');kind='ESCOPETA' if shot else 'PISTOLA'
    b.m['brass']=L.material(b.asset+'_brass',(.36,.25,.095),.43,1,edge_wear=.03)
    b.m['shell']=L.material(b.asset+'_shell',(.28,.065,.045) if shot else (.16,.18,.16),.65,0,edge_wear=.02)
    def freeze(name):
        o=L.join(b.parts,'GEO-'+id+'-'+name);L.apply_all(o);o.data.transform(o.matrix_world);o.matrix_world=Matrix.Identity(4)
        L.smooth(o,40);groups.append(o);b.parts=[];return o
    b.box('bottom',(.30,.20,.012),(0,0,.006),'paint',0)
    for x in (-.146,.146):b.box('side',(.008,.20,.132),(x,0,.078),'paint',.001)
    for y in (-.096,.096):b.box('front_back',(.284,.008,.132),(0,y,.078),'paint',.001)
    # Top seal around the mouth; real opening remains visible when empty.
    for x in (-.145,.145):b.box('seal_side',(.010,.192,.004),(x,0,.145),'dark',0)
    for y in (-.095,.095):b.box('seal_cross',(.28,.010,.004),(0,y,.145),'dark',0)
    b.box('latch_plate',(.035,.006,.04),(0,-.103,.125),'steel',.001)
    b.box('latch_release',(.024,.008,.022),(0,-.109,.121),'steel',.001)
    for x in (-.084,.084):b.cyl('hinge',.008,.047,(x,.099,.143),'steel','X',8)
    # Lid assembled closed, then opened 110 degrees around its rear hinge.
    start=len(b.parts)
    b.box('lid',(.30,.20,.012),(0,0,.15),'paint',.001)
    b.box('lid_liner',(.272,.172,.004),(0,0,.142),'ivory',0)
    for x in (-.058,.058):b.box('handle_lug',(.015,.022,.010),(x,0,.161),'steel',0)
    for x in (-.058,.058):b.box('handle_end',(.010,.014,.026),(x,0,.176),'steel',0)
    b.box('handle_grip',(.126,.014,.012),(0,0,.191),'dark',.001)
    bpy.context.view_layer.update()
    hinge=Vector((0,.099,.15));turn=Matrix.Translation(hinge)@Matrix.Rotation(math.radians(-110),4,'X')@Matrix.Translation(-hinge)
    for o in b.parts[start:]:o.matrix_world=turn@o.matrix_world
    label_material(b,'case_label',kind,0,.057,.15,.045)
    b.box('printed_case_label',(.15,.001,.045),(0,-.1006,.057),'case_label',0)
    freeze('Case')
    # A carton with recessed tray and visible rounds; rendered contents are an inventory cue,
    # not a second source of authoritative ammunition quantities.
    b.box('carton',(.22,.13,.073),(0,0,.0485),'ivory',0)
    b.box('tray',(.204,.114,.008),(0,0,.089),'dark',0)
    b.box('carton_type_tab',(.10,.004,.050),(0,.055,.112),'ivory',0)
    label_material(b,'pack_label',kind,0,.115,.09,.027)
    b.box('printed_pack_label',(.09,.001,.027),(0,.0524,.115),'pack_label',0)
    if shot:
        for x in (-.072,-.024,.024,.072):
            b.cyl('shell_case',.012,.060,(x,0,.116),'shell','Z',8)
            b.cyl('brass_cap',.013,.010,(x,0,.091),'brass','Z',8)
    else:
        for y in (-.027,.027):
            for x in (-.074,-.037,0,.037,.074):
                b.cyl('cartridge_case',.006,.028,(x,y,.107),'brass','Z',6)
                b.cyl('projectile_tip',.0045,.010,(x,y,.126),'copper','Z',6)
    freeze('Contents');L.uv_project_all(groups,margin=.016)
    # Reserve readable UV rectangles for the type labels without increasing texture count.
    for o in groups:
        uv=o.data.uv_layers.active.data
        for loop in uv:loop.uv*=.71
        for face in o.data.polygons:
            name=o.data.materials[face.material_index].name
            if face.normal.y>-.99:continue
            if '_case_label' in name:low,high,z,w,h,u,v,du,dv=-.075,.075,.057,.15,.045,.02,.74,.60,.18
            elif '_pack_label' in name:low,high,z,w,h,u,v,du,dv=-.045,.045,.115,.09,.027,.66,.74,.30,.09
            else:continue
            for li in face.loop_indices:
                co=o.data.vertices[o.data.loops[li].vertex_index].co
                uv[li].uv=(u+(co.x-low)/w*du,v+(co.z-z+h/2)/h*dv)
    tris=0
    for o in groups:o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles)
    points=[o.matrix_world@v.co for o in groups for v in o.data.vertices]
    report={'asset':b.asset,'triangles':tris,'mesh_count':2,'texture_sets':1,'dimensions_blender':[max(v[i] for v in points)-min(v[i] for v in points) for i in range(3)],'closed_case_dimensions':[.3,.2,.15],'collision_boxes_blender':[],'features':['open lid at 110 degrees','carry handle','latch and rear hinges','mouth gasket','type labels on case and carton','separate hideable ammunition contents'],'state':'En produccion'}
    os.makedirs(folder(id),exist_ok=True)
    with open(folder(id)+'/geometry.json','w') as f:json.dump(report,f,indent=2)
    SCENES[id]=b.scene;bpy.data.libraries.write(ROOT+'/SourceArt/Blender/'+b.asset+'.blend',{b.scene},fake_user=True);return report
def activate(id):
    if id not in SCENES:
        with bpy.data.libraries.load(ROOT+'/SourceArt/Blender/'+asset(id)+'.blend',link=False) as (src,dst):dst.scenes=src.scenes
        SCENES[id]=dst.scenes[0]
    bpy.context.window.scene=SCENES[id];return SCENES[id]
def render(id):
    s=activate(id);old=L.EVIDENCE;L.EVIDENCE=folder(id)
    try:return L.sheet(asset(id),[o for o in s.objects if o.type=='MESH'],views=('iso',),res=640)
    finally:L.EVIDENCE=old
def finish(id):
    s=activate(id);objs=[o for o in s.objects if o.type=='MESH'];name=asset(id)
    for mat in {m for o in objs for m in o.data.materials}:
        for n in mat.node_tree.nodes:
            if n.type=='MATH' and n.operation=='MULTIPLY' and n.inputs[0].is_linked:
                ramp=n.inputs[0].links[0].from_node
                if ramp.type=='VALTORGB' and ramp.inputs['Fac'].is_linked and ramp.inputs['Fac'].links[0].from_node.type=='NEW_GEOMETRY':n.inputs[1].default_value=.04
    samples=[dict(zip(('x','y','z'),o.matrix_world@v.co)) for o in objs for v in list(o.data.vertices)[::max(1,len(o.data.vertices)//32)]]
    with open(folder(id)+'/source_coordinates.json','w') as f:json.dump({'vertices':samples},f)
    old=L.TEX_DIR;L.TEX_DIR=folder(id)
    try:maps=L.bake_pbr(objs,name,size=512,samples=24,margin=2)
    finally:L.TEX_DIR=old
    for suffix,path in maps.items():
        img=bpy.data.images.load(path,check_existing=False);img.pack();n=objs[0].data.materials[0].node_tree.nodes.new('ShaderNodeTexImage');n.image=img;n.label='Runtime baked '+suffix
        shutil.copy2(path,ROOT+'/EsneiderProtocoloLazaro/Assets/_Game/Art/Textures/'+os.path.basename(path))
    bpy.data.libraries.write(ROOT+'/SourceArt/Blender/'+name+'.blend',{s},fake_user=True)
    backups=[(o,o.data) for o in objs];mat=objs[0].data.materials[0]
    try:
        for o,mesh in backups:
            o.data=mesh.copy();o.data.materials.clear();o.data.materials.append(mat)
            for f in o.data.polygons:f.material_index=0
        with L.ctx(objs[0],objs):bpy.ops.export_scene.fbx(filepath=ROOT+'/EsneiderProtocoloLazaro/Assets/_Game/Art/Models/'+name+'.fbx',use_selection=True,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Z',axis_up='Y',object_types={'MESH'},bake_space_transform=True,mesh_smooth_type='FACE',use_mesh_modifiers=True,bake_anim=False,path_mode='STRIP',embed_textures=False)
    finally:
        for o,mesh in backups:o.data=mesh
    with open(folder(id)+'/bake.json','w') as f:json.dump(maps,f,indent=2)
    return maps
