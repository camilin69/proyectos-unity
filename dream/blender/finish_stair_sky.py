"""Material prototype after the stair geometry gate; run in live Blender.

Set DREAM_STAIR_CHECKER=True for the UV gate. Procedural maps are recreated
from reference appearance, not original extracted surface maps. No auto-export.
"""
import bpy, json, math, random
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
PLAN=json.loads((ROOT/'blender/stair_sky_plan.json').read_text(encoding='utf-8'))
scene=bpy.data.scenes['DREAM_StairSky'];bpy.context.window.scene=scene
CHECKER=globals().get('DREAM_STAIR_CHECKER',False)
PREFIX='GEO-DREAM-stair-'
for obj in list(scene.objects):
    if obj.name.startswith(PREFIX+'detail_'): bpy.data.objects.remove(obj,do_unlink=True)

def linear(c): return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
def color(hex): return tuple(linear(int(hex[i:i+2],16)/255) for i in (0,2,4))
def image(name,normal=False):
    im=bpy.data.images.load(str(ROOT/'assets/textures'/f'{name}.png'),check_existing=True)
    if im.packed_file: im.unpack(method='REMOVE')
    im.reload();im.colorspace_settings.name='Non-Color' if normal else 'sRGB'
    return im

settings={
    'plush':('FFFFFF',.93,0,12,0,'stair_plush'),
    'grass':('FFFFFF',.92,0,11,0,'stair_grass'),
    'mint':('94BDB1',.86,0,0,0,None),
    'frame':('E2AA9F',.52,0,0,0,None),
    # The video shows a warm opaque finish rather than a blue mirror return.
    # A coated pale rail is an inferred surface model, not recovered metallurgy.
    'rail':('F6DED1',.26,0,0,0,None),
    'blades':('FFFFFF',.92,0,11,1,'stair_grass'),
}
mats={}
for index,(role,(hex,rough,metal,kind,variant,maps)) in enumerate(settings.items()):
    name='DREAM_STAIR_MAT_'+role
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True
    m.node_tree.nodes.clear();nt=m.node_tree
    b=nt.nodes.new('ShaderNodeBsdfPrincipled');out=nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(b.outputs['BSDF'],out.inputs['Surface'])
    b.inputs['Base Color'].default_value=(*color(hex),1)
    b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal
    m.diffuse_color=(*color(hex),1)
    for key,val in dict(dream_id=index,kind=kind,roughness=rough,metallic=metal,albedo_variant=variant).items():m[key]=val
    if role=='plush': b.inputs['Sheen Weight'].default_value=.3
    if role=='rail': b.inputs['Coat Weight'].default_value=.35
    if maps:
        t=nt.nodes.new('ShaderNodeTexImage')
        t.image=image(('stair_checker_'+role) if CHECKER and role in ('plush','grass') else maps+'_albedo')
        nt.links.new(t.outputs['Color'],b.inputs['Base Color'])
        if not CHECKER and role!='blades':
            t=nt.nodes.new('ShaderNodeTexImage');t.image=image(maps+'_normal',True)
            normal=nt.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.42 if role=='plush' else .28
            nt.links.new(t.outputs['Color'],normal.inputs['Color']);nt.links.new(normal.outputs['Normal'],b.inputs['Normal'])
    mats[role]=m

def uv_world(obj,role):
    mesh=obj.data;uv=mesh.uv_layers.get('StairSurfaceUV') or mesh.uv_layers.new(name='StairSurfaceUV');mesh.uv_layers.active=uv;uv.active_render=True
    matrix=obj.matrix_world;normalmat=matrix.to_3x3().inverted().transposed()
    for poly in mesh.polygons:
        n=normalmat@poly.normal;a=[abs(x) for x in n]
        axis=2 if a[2]>=a[0] and a[2]>=a[1] else (1 if a[1]>=a[0] else 0)
        for li in poly.loop_indices:
            p=matrix@mesh.vertices[mesh.loops[li].vertex_index].co
            if role in ('grass','blades'):value=(p.x/4,p.y/4)
            else:value=(p.x/.28,p.y/.28) if axis==2 else ((p.x/.28,p.z/.28) if axis==1 else (p.y/.28,p.z/.28))
            uv.data[li].uv=value
    mesh.update()

base=[];coverage=[]
for obj in list(scene.objects):
    if obj.type!='MESH' or not obj.name.startswith(PREFIX):continue
    role=obj.get('dream_surface_role')
    if role is None:
        old=obj.data.materials[0].name
        role=next((r for token,r in [('future_pink_fibers','plush'),('future_grass','grass'),('future_mint_surround','mint'),('future_pink_frame','frame'),('future_metal_rails','rail')] if token in old),None)
    if role is None:raise ValueError('Unknown stair role: '+obj.name)
    obj['dream_surface_role']=role
    bpy.context.view_layer.objects.active=obj
    for modifier in list(obj.modifiers): bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.data.materials.clear();obj.data.materials.append(mats[role]);uv_world(obj,role)
    base.append(obj)
    coverage.append({'object':obj.name,'role':role,'faces':len(obj.data.polygons),'uv':'WorldXY/4' if role=='grass' else 'world dominant-axis / .28','surface_fill':'image' if role in ('grass','plush') else 'intentional plain PBR'})

def scatter(source,role,density,seed):
    rng=random.Random(seed);vertices=[];faces=[];count=0
    for obj in source:
        mesh=obj.data;mesh.calc_loop_triangles();matrix=obj.matrix_world
        for tri in mesh.loop_triangles:
            a,b,c=[matrix@mesh.vertices[i].co for i in tri.vertices]
            cross=(b-a).cross(c-a);area=cross.length/2
            if area<1e-9:continue
            n=cross.normalized()
            # Exposed top and outward front; never fill the underside/interior.
            if role=='plush':
                if n.z<.65 and not (n.y<-.85 and max(a.z,b.z,c.z)>.01):continue
                if n.y<-.85 and min(a.y,b.y,c.y)>3.61:continue
            elif n.z<.35:continue
            target=area*density;number=int(target)+(rng.random()<target%1)
            t=n.cross(Vector((0,1,0)) if abs(n.y)<.9 else Vector((1,0,0))).normalized();u=n.cross(t)
            for _ in range(number):
                r=math.sqrt(rng.random());s=rng.random();p=a*(1-r)+b*(r*(1-s))+c*(r*s)
                if role=='plush' and (p.y>3.61 or abs(p.x)>.941):continue
                # Closed stacked boxes have hidden front portions; only expose
                # each .16 m riser immediately below its own tread.
                if role=='plush' and n.y<-.85 and 'tread_' in obj.name:
                    top=obj.get('support_z_m',0)
                    if p.z<top-.162:continue
                angle=rng.random()*2*math.pi;direction=t*math.cos(angle)+u*math.sin(angle)
                height=rng.uniform(.014,.035) if role=='plush' else rng.uniform(.035,.075)
                width=rng.uniform(.0015,.0030) if role=='plush' else rng.uniform(.008,.014)
                lean=(t*rng.uniform(-1,1)+u*rng.uniform(-1,1))*height*.6
                p+=n*.0015
                q=p+n*(height*.6)+lean*.35;tip=p+n*height+lean
                index=len(vertices)
                vertices.extend([tuple(p-direction*width),tuple(p+direction*width),tuple(q+direction*width*.55),tuple(tip),tuple(q-direction*width*.55)])
                faces.extend([(index,index+1,index+2),(index,index+2,index+4),(index+4,index+2,index+3)])
                count+=1
    mesh=bpy.data.meshes.new('DREAM_Stair_'+role+'_detail_mesh');mesh.from_pydata(vertices,[],faces);mesh.update()
    obj=bpy.data.objects.new(PREFIX+'detail_'+role,mesh);scene.collection.objects.link(obj)
    obj['dream_owner']='DREAM_StairSky';obj['dream_skip_ao']=True;obj['dream_surface_role']='blades' if role=='grass' else 'plush'
    mesh.materials.append(mats['blades' if role=='grass' else 'plush']);uv_world(obj,obj['dream_surface_role'])
    return {'strands':count,'triangles':len(faces),'vertices':len(vertices)}

detail={}
if not CHECKER:
    detail['plush']=scatter([o for o in base if o['dream_surface_role']=='plush'],'plush',3400,35091)
    detail['grass']=scatter([o for o in base if o['dream_surface_role']=='grass'],'grass',620,35092)
    world=bpy.data.worlds.get('DREAM_StairSky_World') or bpy.data.worlds.new('DREAM_StairSky_World');world.use_nodes=True
    nt=world.node_tree;nt.nodes.clear()
    coordinate=nt.nodes.new('ShaderNodeTexCoord');mapping=nt.nodes.new('ShaderNodeMapping');mapping.inputs['Scale'].default_value=(1,-1,1)
    texture=nt.nodes.new('ShaderNodeTexEnvironment');texture.image=image('stair_sky');texture.projection='EQUIRECTANGULAR'
    background=nt.nodes.new('ShaderNodeBackground');background.inputs['Strength'].default_value=1.0
    out=nt.nodes.new('ShaderNodeOutputWorld');nt.links.new(coordinate.outputs['Generated'],mapping.inputs['Vector']);nt.links.new(mapping.outputs['Vector'],texture.inputs['Vector']);nt.links.new(texture.outputs['Color'],background.inputs['Color']);nt.links.new(background.outputs['Background'],out.inputs['Surface'])
    scene.world=world
    for obj in scene.objects:
        if obj.type=='LIGHT':
            obj.data.energy=400 if 'key' in obj.name else 180
            obj.data.color=(1,.87,.75) if 'key' in obj.name else (1,.9,.9)
            obj.data.size=6
    name='LGT-DREAM-stair-camera_fill'
    lamp=bpy.data.objects.get(name)
    if lamp is None:
        data=bpy.data.lights.new('DREAM_StairCameraFill','AREA');lamp=bpy.data.objects.new(name,data);scene.collection.objects.link(lamp)
    lamp.location=(0,-4.5,3.4);lamp.rotation_euler=(Vector((0,1.2,1.4))-lamp.location).to_track_quat('-Z','Y').to_euler()
    lamp.data.shape='DISK';lamp.data.size=4;lamp.data.energy=180;lamp.data.color=(1,.82,.78)

nav=json.loads(scene['dream_navigation']);nav['status']='configured_for_height_support_runtime_validation_pending'
nav['runtime_note']='SceneSettings consumes 14 support surfaces and enforces .18 m step limits.'
scene['dream_navigation']=json.dumps(nav)
cam=PLAN['constructor']['camera_seed'];corridor=nav['center_corridor_xyxy_m']
config=['camera '+' '.join(map(str,[*cam['position_m'],cam['yaw_rad'],cam['pitch_rad']])),f"fov {cam['tan_half_vertical_fov']}",'environment 3','far_clip 200','reflection 0','exposure 0',f'bounds {corridor[0]} {corridor[2]} {corridor[1]} {corridor[3]}',f"eye_height {nav['eye_height_m']}",f"step_limits {nav['max_step_up_m']} {nav['max_step_down_m']}"]
config+=['surface '+' '.join(map(str,[*s['xyxy_m'],s['support_z_m']])) for s in nav['support_surfaces']]
scene['dream_runtime_config']=json.dumps(config)
scene['dream_stage']='uv_checker_pending_review' if CHECKER else 'material_prototype_pending_review'
scene['dream_detail_report']=json.dumps(detail)
scene.render.resolution_x,scene.render.resolution_y=cam['render_px'];scene.render.resolution_percentage=100
scene.eevee.taa_render_samples=96
report={'schema':'dream.stair_surface_coverage.v1','stage':scene['dream_stage'],'geometry_review':'validation/stair-sky-geometry-review.json','final_accepted':False,'all_base_surfaces_mapped':True,'coverage':coverage,'detail':detail,'limits':['Grass uses planar world XY color on closed terrain; vertical green risers have degenerate UV and rely on color/geometric normal.','Plush is mapped per dominant face including backs and sides. Small normal differences at projection boundaries remain possible.','Sky is a distant panorama without moving volume.']}
(ROOT/'validation'/('stair-uv-coverage.json' if CHECKER else 'stair-material-prototype.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'scene':scene.name,'objects':len(scene.objects),'checker':CHECKER,'detail':detail,'navigation_surfaces':len(nav['support_surfaces'])}))
