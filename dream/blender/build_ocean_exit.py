"""Run only inside live Blender MCP. Isolated, editable ocean-exit study."""
import json
import math
from pathlib import Path
from collections import Counter
import bpy
from mathutils import Vector, Quaternion
from bpy_extras.object_utils import world_to_camera_view

ROOT=Path(__file__).resolve().parents[1]
PLAN=json.loads((ROOT/'blender/ocean_exit_plan.json').read_text(encoding='utf8'))
MAPS=ROOT/'assets/textures/ocean_exit'
OUT=ROOT/'validation/ocean-exit'
TOKEN='DREAM-ocean-'

def build():
    assert bpy.data.scenes.get('DREAM_OceanExit') is None, 'Scene exists; inspect before replacing.'
    scene=bpy.data.scenes.new('DREAM_OceanExit')
    bpy.context.window.scene=scene
    scene['dream_asset']='v42_ocean_exit'
    scene['reference_accepted']=False
    scene.render.engine='BLENDER_EEVEE'
    scene.render.resolution_x=478;scene.render.resolution_y=850
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.view_settings.view_transform='Standard'
    scene.view_settings.exposure=0
    scene.eevee.taa_render_samples=64
    scene.eevee.use_raytracing=True
    images={}

    def image(name,noncolor=False):
        if name not in images:
            im=bpy.data.images.load(str(MAPS/name),check_existing=False)
            im.name=TOKEN+name
            if noncolor: im.colorspace_settings.name='Non-Color'
            im.pack();images[name]=im
        return images[name]

    def material(name,color,rough=.4,metal=0):
        m=bpy.data.materials.new('MAT-'+TOKEN+name);m.use_nodes=True
        b=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
        b.inputs['Base Color'].default_value=(*color,1)
        b.inputs['Roughness'].default_value=rough
        b.inputs['Metallic'].default_value=metal
        m.diffuse_color=(*color,1)
        return m,b

    def texture(m,name,noncolor=False):
        node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=image(name,noncolor)
        return node

    cream,_=material('cream_enamel',(.52,.49,.32),.32)
    grout,_=material('submerged_bed',(.18,.37,.32),.8)
    trim,_=material('frame',(.42,.38,.20),.22)
    steel,_=material('pushbar',(.48,.50,.47),.24,1)
    pink,b=material('pink_ceramic',(.6,.3,.45),.2)
    tex=texture(pink,'pink_tile_albedo.png');pink.node_tree.links.new(tex.outputs['Color'],b.inputs['Base Color'])
    tex=texture(pink,'pink_tile_roughness.png',True);pink.node_tree.links.new(tex.outputs['Color'],b.inputs['Roughness'])
    tex=texture(pink,'pink_tile_height.png',True)
    bump=pink.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.0015
    pink.node_tree.links.new(tex.outputs['Color'],bump.inputs['Height']);pink.node_tree.links.new(bump.outputs['Normal'],b.inputs['Normal'])
    b.inputs['Coat Weight'].default_value=.35

    def mesh(name,verts,faces,mat,uv_period=.16,smooth=False):
        me=bpy.data.meshes.new('MESH-'+TOKEN+name);me.from_pydata(verts,[],faces);me.update()
        ob=bpy.data.objects.new('GEO-'+TOKEN+name,me);scene.collection.objects.link(ob)
        me.materials.append(mat)
        uv=me.uv_layers.new(name='SurfaceMetres')
        for p in me.polygons:
            p.use_smooth=smooth
            axis=max(range(3),key=lambda k:abs(p.normal[k]));axes=[k for k in range(3) if k!=axis]
            for li in p.loop_indices:
                v=me.vertices[me.loops[li].vertex_index].co
                uv.data[li].uv=(v[axes[0]]/uv_period,v[axes[1]]/uv_period)
        return ob

    def box(name,lo,hi,mat,bevel=.0):
        x,y,z=lo;X,Y,Z=hi
        ob=mesh(name,[(x,y,z),(X,y,z),(X,Y,z),(x,Y,z),(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)],
            [(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],mat)
        if bevel:
            mod=ob.modifiers.new('Small edge rounding','BEVEL');mod.width=bevel;mod.segments=3;mod.limit_method='ANGLE'
        return ob

    l=PLAN['layout'];w=l['room_half_width_m'];front=l['front_y_m'];back=l['back_y_m'];top=l['ceiling_z_m'];th=l['wall_thickness_m'];d=l['door_half_width_m'];dh=l['door_top_z_m']
    box('bed',(-w-th,front,-.87),(w+th,back+.3,-.75),grout)
    box('ceiling',(-w-th,front,top),(w+th,back+th,top+.15),cream)
    for side in [-1,1]:
        a,bx=(-w-th,-w) if side<0 else (w,w+th)
        box(f'wall_{side}',(a,front,-.8),(bx,back+th,top),cream)
        for zi,(z0,z1) in enumerate([(-.05,.88),(1.23,2.68)]):
            aa,bb=(bx-.008,bx+.008) if side<0 else (a-.008,a+.008)
            box(f'tile_side_{side}_{zi}',(aa,front,z0),(bb,back,z1),pink)
        xa,xb=(-w-th,-d) if side<0 else (d,w+th)
        box(f'exit_pier_{side}',(xa,back,-.8),(xb,back+th,top),cream)
        for zi,(z0,z1) in enumerate([(-.05,.88),(1.23,2.68)]):
            box(f'tile_pier_{side}_{zi}',(xa,back-.013,z0),(xb,back+.005,z1),pink)
        box(f'jamb_{side}',(side*d-.024,back-.032,-.04),(side*d+.024,back+th+.01,dh+.024),trim,.005)
        px0=l['parapet_inner_x_m'];px1=px0+l['parapet_width_m']
        xa,xb=(-px1,-px0) if side<0 else (px0,px1)
        box(f'low_border_{side}',(xa,front,-.77),(xb,l['parapet_end_y_m'],.255),cream,.015)
        box(f'pink_cap_{side}',(xa-.012,front,.25),(xb+.012,l['parapet_end_y_m']+.01,.29),pink,.008)
    box('header',(-d,back,dh),(d,back+th,top),cream)
    box('head_frame',(-d-.024,back-.032,dh),(d+.024,back+th,dh+.048),trim,.005)
    # Left service door is a separate leaf and push bar, slightly inside its wall.
    box('service_door',(-w+.01,3.15,-.05),(-w+.042,4.35,2.25),cream,.008)
    box('service_pushbar',(-w+.04,3.28,.94),(-w+.11,4.22,1.005),steel,.015)

    def tube(name,points,radius,mat):
        verts=[];n=24
        for k,p in enumerate(points):
            tangent=Vector(points[min(k+1,len(points)-1)])-Vector(points[max(0,k-1)])
            tangent.normalize();a=Vector((0,1,0));bb=tangent.cross(a).normalized()
            verts.extend([tuple(Vector(p)+radius*(a*math.cos(2*math.pi*i/n)+bb*math.sin(2*math.pi*i/n))) for i in range(n)])
        faces=[tuple(reversed(range(n)))]
        for k in range(len(points)-1):
            faces.extend([(k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i) for i in range(n)])
        faces.append(tuple((len(points)-1)*n+i for i in range(n)))
        return mesh(name,verts,faces,mat,smooth=True)
    tube('bent_access_post',[(.88,3.35,-.3),(.88,3.35,.83),(.875,3.35,.93),(.84,3.35,1.01),(.77,3.35,1.04)],.045,cream)

    def sign(name,filename,x0,x1,z0,z1,emission=0):
        mat,b=material(name,(1,1,1),.55)
        tex=texture(mat,filename);mat.node_tree.links.new(tex.outputs['Color'],b.inputs['Base Color'])
        if emission:
            mat.node_tree.links.new(tex.outputs['Color'],b.inputs['Emission Color']);b.inputs['Emission Strength'].default_value=emission
        ob=box(name,(x0,back-.055,z0),(x1,back-.025,z1),mat)
        for p in ob.data.polygons:
            if p.normal.y<-.9:
                for li in p.loop_indices:
                    v=ob.data.vertices[ob.data.loops[li].vertex_index].co
                    ob.data.uv_layers.active.data[li].uv=((v.x-x0)/(x1-x0),(v.z-z0)/(z1-z0))
        return ob
    sign('exit_here','exit_here.png',.96,1.53,1.29,2.18)
    sign('exit_lamp','exit_lamp.png',-.30,.30,2.66,2.90,1.3)

    # Separate water bodies: reconstructed wave field, not a recovered fluid simulation.
    for name,x0,x1,y0,y1,nx,ny,col in [('interior_water',-w,w,front,back,90,170,(.07,.42,.38)),('ocean',-150,150,back,350,100,170,(.018,.06,.08))]:
        water,b=material(name,col,.12)
        b.inputs['IOR'].default_value=1.333;b.inputs['Transmission Weight'].default_value=.22
        bump=water.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.025
        tex=texture(water,'ripple_height.png',True)
        water.node_tree.links.new(tex.outputs['Color'],bump.inputs['Height']);water.node_tree.links.new(bump.outputs['Normal'],b.inputs['Normal'])
        if name=='interior_water':
            foam=texture(water,'foam_mask.png',True)
            ramp=water.node_tree.nodes.new('ShaderNodeValToRGB')
            ramp.color_ramp.elements[0].color=(*col,1);ramp.color_ramp.elements[1].color=(.65,.81,.75,1)
            water.node_tree.links.new(foam.outputs['Color'],ramp.inputs['Fac']);water.node_tree.links.new(ramp.outputs['Color'],b.inputs['Base Color'])
        verts=[]
        for j in range(ny+1):
            yy=y0+(y1-y0)*j/ny
            for i in range(nx+1):
                xx=x0+(x1-x0)*i/nx
                zz=.018*math.sin(yy*7+math.sin(xx*4))+.009*math.sin(xx*13+yy*3)
                verts.append((xx,yy,zz))
        faces=[(j*(nx+1)+i,j*(nx+1)+i+1,(j+1)*(nx+1)+i+1,(j+1)*(nx+1)+i) for j in range(ny) for i in range(nx)]
        mesh(name,verts,faces,water,uv_period=4,smooth=True)

    world=bpy.data.worlds.new(TOKEN+'world');world.use_nodes=True;scene.world=world
    bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND')
    tex=world.node_tree.nodes.new('ShaderNodeTexEnvironment');tex.image=image('sunset_stars.png')
    world.node_tree.links.new(tex.outputs['Color'],bg.inputs['Color']);bg.inputs['Strength'].default_value=.65

    def light(name,pos,target,color,power,size):
        data=bpy.data.lights.new(TOKEN+name,'AREA');data.energy=power;data.color=color;data.shape='DISK';data.size=size
        ob=bpy.data.objects.new('LIGHT-'+TOKEN+name,data);scene.collection.objects.link(ob);ob.location=pos
        ob.rotation_euler=(Vector(target)-Vector(pos)).to_track_quat('-Z','Y').to_euler()
    light('ceiling',(0,2.2,3.15),(0,2,0),(1,.88,.74),220,2.6)
    light('front_fill',(0,-1,2.6),(0,4,1),( .76,.86,1),130,2.5)
    light('magenta_exit',(-.4,6.5,1.8),(.2,2,0),(1,.025,.44),180,1.2)

    c=PLAN['primary_camera'];data=bpy.data.cameras.new('CAM-'+TOKEN+'7s')
    data.sensor_fit='HORIZONTAL';data.sensor_width=36
    data.lens=36/(2*c['tan_half_vertical_fov']*478/850)
    data.shift_y=c['shift_y'];data.clip_end=1000
    cam=bpy.data.objects.new(data.name,data);scene.collection.objects.link(cam);cam.location=c['position_m'];cam.rotation_mode='QUATERNION'
    yaw,pitch=c['yaw_rad'],c['pitch_rad']
    direction=Vector((math.cos(yaw)*math.cos(pitch),math.sin(yaw)*math.cos(pitch),math.sin(pitch)))
    cam.rotation_quaternion=direction.to_track_quat('-Z','Y') @ Quaternion((0,0,1),c['roll_rad'])
    scene.camera=cam;bpy.context.view_layer.update()
    points=[(-d,back,dh),(d,back,dh),(d,back,0),(-d,back,0)]
    projected=[]
    for p in points:
        uv=world_to_camera_view(scene,cam,Vector(p));projected.append([uv.x*478,(1-uv.y)*850])
    observed=PLAN['primary_door_observations_px']
    rms=math.sqrt(sum(sum((a-b)**2 for a,b in zip(p,q)) for p,q in zip(projected,observed))/4)
    audit={'scene':scene.name,'accepted':False,'runtime_promoted':False,'door_projection_px':projected,'door_corner_rms_px':rms,'objects':len(scene.objects),'mesh_objects':sum(o.type=='MESH' for o in scene.objects),'packed_images':list(images),'water_meshes_are_open_surfaces':True,'limitations':['Metric scale and unseen geometry inferred.','Water field is static proposal; no animation or runtime export.','Camera shift is a hypothesis fitted to door corners and horizon, not recovered lens metadata.']}
    (OUT/'build-audit.json').write_text(json.dumps(audit,indent=2)+'\n',encoding='utf8')
    assert rms<2, f'Camera projection mismatch {rms}'
    bpy.data.libraries.write(str(ROOT/'blender/ocean_exit.blend'),{scene},path_remap='RELATIVE_ALL',fake_user=True,compress=True)
    print(json.dumps(audit))

if __name__=='__main__':
    build()
