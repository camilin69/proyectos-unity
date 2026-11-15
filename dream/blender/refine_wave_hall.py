"""Editable hall candidate derived from source observations; no auto export.

Run in Blender, then finish_wave_corridor.apply() for explicit UV/materials.
Preserves all corridor geometry and replaces only the owned hall components.
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKEN = '-DREAM-wavecorridor-'

def apply(scene):
    import bpy
    import bmesh
    plan = json.loads((ROOT/'blender/wave_corridor_plan.json').read_text(encoding='utf-8'))
    hall = json.loads((ROOT/'blender/wave_hall_plan.json').read_text(encoding='utf-8'))
    config = plan['constructor']
    corridor = config['corridor']
    low = config['floor']['base_z_m']-sum(f['riser_count']*f['riser_m'] for f in config['floor']['flights'])
    bottom,ceiling = corridor['solid_bottom_z_m'],corridor['ceiling_z_m']
    y0,y1,half = corridor['end_y_m'],hall['end_y_m'],hall['half_width_m']
    collection = bpy.data.collections['DREAM_WaveCorridor_Blockout']
    # Author-owned hall meshes only. Corridor fixtures/cameras remain intact.
    removed=[]
    for obj in list(scene.objects):
        if obj.name.startswith(('GEO'+TOKEN+'hall_', 'LGT'+TOKEN+'hall_')):
            removed.append(obj.name)
            bpy.data.objects.remove(obj,do_unlink=True)
    created=[]
    def own(obj,label,role):
        obj.name='GEO'+TOKEN+label
        for previous in list(obj.users_collection):
            if previous!=collection:
                previous.objects.unlink(obj)
        if obj.name not in collection.objects:
            collection.objects.link(obj)
        obj['dream_owner']=scene.name
        obj['dream_surface_role']=role
        obj['dream_hall_candidate']=1
        obj['dream_detail_source']='video-42 @14,15.5,17 s; dimensions and rear-bay interpretation provisional'
        created.append(obj.name)
        return obj
    def box(label,center,size,role):
        # Shared vertices and outward normals on all six sides. Subdivide
        # broad panels so corner AO does not shade an entire wall as one quad.
        vertices=[(center[0]+x*size[0]/2,center[1]+y*size[1]/2,center[2]+z*size[2]/2)
                  for x in (-1,1) for y in (-1,1) for z in (-1,1)]
        faces=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
        data=bpy.data.meshes.new('MESH'+TOKEN+label)
        data.from_pydata(vertices,[],faces);data.update()
        bm=bmesh.new();bm.from_mesh(data)
        cuts=min(20,int(max(size)/.8))
        if cuts>1:
            bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=cuts,use_grid_fill=True)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        assert all(e.is_manifold for e in bm.edges), label
        assert bm.calc_volume(signed=True)>0, label
        bm.to_mesh(data);bm.free()
        obj=bpy.data.objects.new('GEO'+TOKEN+label,data)
        return own(obj,label,role)
    def sphere(label,center,scale,role):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=10,radius=1,location=center)
        obj=own(bpy.context.object,label,role)
        obj.scale=scale
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        for face in obj.data.polygons:face.use_smooth=True
        return obj
    box('hall_floor',(0,(y0+y1)/2,(bottom+low)/2),(half*2,y1-y0,low-bottom),'floor')
    for side in (-1,1):
        box(f'hall_side_{side}',(side*(half+.09),(y0+y1)/2,(bottom+ceiling)/2),(.18,y1-y0,ceiling-bottom),'wall')
        # The wider room needs real return walls beside its entrance.
        x0=corridor['half_width_m']
        box(f'hall_entrance_return_{side}',(side*(x0+half)/2,y0-.06,(bottom+ceiling)/2),
            (half-x0,.12,ceiling-bottom),'wall')
    box('hall_ceiling',(0,(y0+y1)/2,ceiling+.08),(half*2+.36,y1-y0,.16),'ceiling')
    box('hall_back_wall',(0,y1+.09,(bottom+ceiling)/2),(half*2+.36,.18,ceiling-bottom),'wall')
    for i,column in enumerate(hall['columns']):
        box(f'hall_column_{i}',(column['x_m'],column['y_m'],(low+ceiling)/2),
            (column['width_m'],column['depth_m'],ceiling-low),'door_trim')
    panel=hall['accent_panel'];column=hall['columns'][panel['column_index']]
    box('hall_column_accent',(column['x_m']-.1,column['y_m']-column['depth_m']/2-.019,low+panel['height_m']/2),
        (panel['width_m'],.04,panel['height_m']),'hall_accent')
    panel_half=half-.18
    panel_bottom,panel_top=low+.12,ceiling-.25
    box('hall_dark_bays',(0,y1-.035,(panel_bottom+panel_top)/2),(panel_half*2,.055,panel_top-panel_bottom),'rear_panel')
    for i in range(hall['rear_grid_columns']+1):
        x=-panel_half+2*panel_half*i/hall['rear_grid_columns']
        box(f'hall_rear_mullion_{i}',(x,y1-.072,(panel_bottom+panel_top)/2),(.035,.025,panel_top-panel_bottom),'hall_metal')
    for i,z in enumerate(hall['rear_grid_levels_m_above_floor']):
        box(f'hall_rear_transom_{i}',(0,y1-.072,low+z),(panel_half*2,.025,.035),'hall_metal')
    bay=hall['rail_bay']
    for i,height in enumerate(bay['heights_m']):
        box(f'hall_horizontal_member_{i}',((bay['x_min_m']+bay['x_max_m'])/2,bay['y_m'],low+height),
            (bay['x_max_m']-bay['x_min_m'],.04,.045),'hall_metal')
    for i,x in enumerate((bay['x_min_m'],bay['x_max_m'])):
        box(f'hall_rail_post_{i}',(x,bay['y_m'],low+.67),(.045,.045,1.34),'hall_metal')
    for ix,x in enumerate(hall['side_fixture_x_m']):
        for iy,y in enumerate(hall['side_fixture_y_m']):
            sphere(f'hall_fixture_{ix}_{iy}',(x,y,ceiling-.0525),(.16,.16,.105),'diffuser')
            sphere(f'hall_fixture_base_{ix}_{iy}',(x,y,ceiling-.0175),(.174,.174,.0175),'door_trim')
            name='LGT'+TOKEN+f'hall_gray_light_{ix}_{iy}'
            data=bpy.data.lights.new(name+'_data','AREA')
            data.energy,data.size=40,.55
            data.color=(1,.93,.84)
            light=bpy.data.objects.new(name,data);collection.objects.link(light)
            light.location=(x,y,ceiling-.48)
    scene['dream_hall_candidate_plan']='blender/wave_hall_plan.json'
    scene['dream_hall_runtime_pending']=True
    return {'created_meshes':len(created),'removed_objects':len(removed),'hall_half_width_m':half,
            'hall_end_y_m':y1,'candidate_only':True,'strict_fidelity_accepted':False}

if __name__=='__main__':
    import bpy
    print(json.dumps(apply(bpy.data.scenes['DREAM_WaveCorridor'])))
