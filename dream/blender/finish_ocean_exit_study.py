"""Native study finishing and topology/material audit, run in live Blender MCP."""
from pathlib import Path
from collections import Counter
import hashlib,json,math
import bpy
ROOT=Path(__file__).resolve().parents[1]
s=bpy.data.scenes['DREAM_OceanExit']
for ob in s.objects:
    if ob.type=='MESH' and any(k in ob.name for k in ['low_border','pink_cap']):
        for poly in ob.data.polygons:
            axis=max(range(3),key=lambda k:abs(poly.normal[k]));axes=[k for k in range(3) if k!=axis]
            for li in poly.loop_indices:
                v=ob.data.vertices[ob.data.loops[li].vertex_index].co
                uv=(v[axes[0]]/.16,v[axes[1]]/.16)
                if 'pink_cap' in ob.name and abs(poly.normal.z)<.5:uv=(uv[0],uv[1]*.58)
                ob.data.uv_layers.active.data[li].uv=uv
worldtex=next(n for n in s.world.node_tree.nodes if n.type=='TEX_ENVIRONMENT')
im=bpy.data.images.load(str(ROOT/'assets/textures/ocean_exit/sunset_stars_v2.png'),check_existing=False)
im.name='DREAM-ocean-sunset_stars_v2.png';im.pack();worldtex.image=im
frame=bpy.data.materials['MAT-DREAM-ocean-frame']
next(n for n in frame.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Roughness'].default_value=.4

rows=[]
for ob in s.objects:
    if ob.type!='MESH':continue
    edges=Counter()
    for p in ob.data.polygons:
        v=list(p.vertices)
        for a,b in zip(v,v[1:]+v[:1]):edges[tuple(sorted((a,b)))]+=1
    boundary=sum(n==1 for n in edges.values());nonmanifold=sum(n>2 for n in edges.values())
    uv=ob.data.uv_layers.active;areas=[]
    for poly in ob.data.polygons:
        pts=[uv.data[i].uv for i in poly.loop_indices]
        areas.append(abs(sum(a.x*b.y-a.y*b.x for a,b in zip(pts,pts[1:]+pts[:1])))/2)
    water=ob.name.endswith(('interior_water','ocean'))
    assert nonmanifold==0
    assert water or boundary==0,ob.name
    assert min(areas)>1e-10,(ob.name,min(areas))
    rows.append({'object':ob.name,'vertices':len(ob.data.vertices),'polygons':len(ob.data.polygons),
                 'boundary_edges':boundary,'intentional_water_surface':water,'uv_min_face_area':min(areas)})
images=set()
for mat in {m for ob in s.objects if ob.type=='MESH' for m in ob.data.materials}:
    for n in mat.node_tree.nodes:
        if n.type=='TEX_IMAGE' and n.image:images.add(n.image)
images.add(im)
packed={image.name:hashlib.sha256(bytes(image.packed_file.data)).hexdigest() for image in images}
report={'schema':'dream.ocean_exit_native_audit.v1','scene':s.name,'objects':len(s.objects),
        'meshes':rows,'closed_meshes':sum(not r['intentional_water_surface'] for r in rows),
        'intentional_open_water_surfaces':2,'packed_images':packed,'accepted':False,'runtime_promoted':False,
        'rebuild_order':['blender/make_ocean_exit_maps.py (standalone)','validation/fit_ocean_exit_camera.py (standalone)',
                         'blender/build_ocean_exit.py (MCP)','blender/refine_ocean_exit.py (MCP)',
                         'blender/make_ocean_sky_refinement.py (standalone)','blender/finish_ocean_exit_study.py (MCP)']}
s.camera=s.objects['CAM-DREAM-ocean-7s']
bpy.data.libraries.write(str(ROOT/'blender/ocean_exit.blend'),{s},path_remap='RELATIVE_ALL',fake_user=True,compress=True)
(ROOT/'validation/ocean-exit/native-audit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print(json.dumps({'objects':len(s.objects),'closed_meshes':report['closed_meshes'],'open_water_surfaces':2,'packed_images':len(packed)}))
