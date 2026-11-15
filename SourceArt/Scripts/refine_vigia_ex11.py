"""EX11: rest-shape refinement, shared-atlas batching and an animated LOD.
Run inside Blender MCP. Input is the archived EX10 source, never the output.
Does not replace open scenes or modify the input rig/actions/UV layout.
"""
import bpy, json, math, sys, os
from mathutils import Vector
ROOT = 'C:/Users/HP/Documents/GitHub/proyectos-unity'
sys.path.insert(0, ROOT + '/SourceArt/Scripts')
import esn_lib as L

def build():
    with bpy.data.libraries.load(ROOT+'/SourceArt/Blender/Archive/BOT-01_Vigia_EX10.blend', link=False) as (src,dst):
        dst.scenes = src.scenes
    scene = dst.scenes[0]; scene.name = 'EX11_Vigia_Production'
    bpy.context.window.scene = scene
    arm = next(o for o in scene.objects if o.type=='ARMATURE')
    meshes = [o for o in scene.objects if o.type=='MESH']
    arm.data.pose_position = 'REST'; bpy.context.view_layer.update()
    before = sum(len(o.data.polygons) for o in meshes)
    # One smooth coordinate map per rigid joint group keeps adjoining covers,
    # bolts and ventilation aligned. No rig proportions or contact meshes change.
    for o in meshes:
        bone = o.vertex_groups[0].name
        inv = o.matrix_world.inverted()
        for v in o.data.vertices:
            p = o.matrix_world @ v.co
            if bone == 'spine':
                t = min(1,max(0,(p.z-.72)/.28))
                p.x *= .77 + .23*math.sin(t*math.pi/2)
                p.y *= .82 + .18*math.sin(t*math.pi)
                p.y += .014 * t*t
            elif bone == 'pelvis':
                t = min(1,max(0,(p.z-.60)/.12))
                p.x *= 1-.14*t
            elif bone == 'head':
                # Chin narrows below the optical sockets; crown remains broad.
                t = min(1,max(0,(p.z-1.075)/.105))
                p.x *= .66+.34*(t*t*(3-2*t))
                if p.y < 0 and p.z < 1.17:
                    p.y *= .82+.18*min(1,max(0,(p.z-1.075)/.095))
            v.co = inv @ p
        o.data.update()
    low = bpy.data.collections.new('EX11_LOW'); scene.collection.children.link(low)
    rig = bpy.data.collections.new('EX11_RIG'); scene.collection.children.link(rig)
    export = bpy.data.collections.new('EX11_EXPORT'); scene.collection.children.link(export)
    for o in meshes: L.link(o,low)
    L.link(arm,rig)
    # Joined exports use the existing shared atlas. All material slots in Unity
    # already refer to that atlas, so they can be collapsed to one draw submesh.
    copies=[]
    for o in meshes:
        cp=o.copy(); cp.data=o.data.copy(); export.objects.link(cp)
        for mod in list(cp.modifiers): cp.modifiers.remove(mod)
        copies.append(cp)
    with L.ctx(copies[0],copies): bpy.ops.object.join()
    geo=copies[0]; geo.name='GEO_Vigia_LOD0'
    atlas=bpy.data.materials.new('EX11_VigiaAtlas'); atlas.use_nodes=True
    p=atlas.node_tree.nodes.get('Principled BSDF')
    for suffix,socket,color in [('BaseColor','Base Color',True),('Roughness','Roughness',False),('Metallic','Metallic',False)]:
        tex=bpy.data.images.load(ROOT+'/EsneiderProtocoloLazaro/Assets/_Game/Art/Textures/BOT-01_Vigia_'+suffix+'.png',check_existing=False)
        if not color: tex.colorspace_settings.name='Non-Color'
        tex.pack(); n=atlas.node_tree.nodes.new('ShaderNodeTexImage'); n.image=tex
        atlas.node_tree.links.new(n.outputs['Color'],p.inputs[socket])
    geo.data.materials.clear(); geo.data.materials.append(atlas)
    for f in geo.data.polygons: f.material_index=0
    geo.parent=arm
    mod=geo.modifiers.new('Rig','ARMATURE'); mod.object=arm
    lod=geo.copy(); lod.data=geo.data.copy(); lod.name='GEO_Vigia_LOD1'; export.objects.link(lod)
    for mod in list(lod.modifiers): lod.modifiers.remove(mod)
    dec=lod.modifiers.new('LOD_reduction','DECIMATE'); dec.ratio=.46; dec.use_collapse_triangulate=True
    with L.ctx(lod): bpy.ops.object.modifier_apply(modifier=dec.name)
    mod=lod.modifiers.new('Rig','ARMATURE'); mod.object=arm
    for o in meshes: o.hide_render=True; o.hide_set(True)
    lod.hide_render=True; lod.hide_set(True)
    arm.data.pose_position='POSE'; L.enable_nla(arm)
    # Preserve the original root name so existing Unity clip paths still bind.
    displaced=[]
    for target,name in ((arm,'Armature_Vigia'),(geo,'GEO_Vigia_LOD0'),(lod,'GEO_Vigia_LOD1')):
        for ob in list(bpy.data.objects):
            if ob!=target and ob.name==name:
                displaced.append((ob,ob.name)); ob.name='EX11_TEMP_'+name
        target.name=name
    scene['EX11_notes']='LOW: editable pieces; EXPORT: shared-atlas LOD0/LOD1; RIG: unchanged 17-bone rig. No high-to-low bake claimed.'
    out=ROOT+'/SourceArt/_evidence/EX-11'; os.makedirs(out,exist_ok=True)
    report={'asset':'BOT-01_Vigia','bones':len(arm.data.bones),'clips':[s.action.name for t in arm.animation_data.nla_tracks for s in t.strips], 'lods':[],'uv_layout':'preserved EX10 atlas','high_low_bake':False}
    for o in (geo,lod):
        o.data.calc_loop_triangles()
        report['lods'].append({'name':o.name,'triangles':len(o.data.loop_triangles),'vertices':len(o.data.vertices),'submeshes':len(o.data.materials),'uv_layers':len(o.data.uv_layers),'unweighted_vertices':sum(not v.groups for v in o.data.vertices)})
    with open(out+'/geometry_report.json','w') as f: json.dump(report,f,indent=2)
    # Save only the production scene and its dependencies, not other open work.
    bpy.data.libraries.write(ROOT+'/SourceArt/Blender/BOT-01_Vigia.blend',{scene},fake_user=True)
    lod.hide_set(False); lod.hide_render=False
    with L.ctx(geo,[geo,lod,arm]):
        bpy.ops.export_scene.fbx(filepath=ROOT+'/EsneiderProtocoloLazaro/Assets/_Game/Art/Models/BOT-01_Vigia.fbx',
            use_selection=True,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Z',axis_up='Y',
            object_types={'MESH','ARMATURE'},add_leaf_bones=False,bake_space_transform=True,mesh_smooth_type='FACE',
            use_mesh_modifiers=True,bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=True,
            bake_anim_use_all_bones=True,bake_anim_simplify_factor=0.0,path_mode='STRIP',embed_textures=False)
    lod.hide_render=True; lod.hide_set(True)
    arm.name='EX11_Armature_Vigia'; geo.name='EX11_preview_LOD0'; lod.name='EX11_preview_LOD1'
    for ob,name in displaced: ob.name=name
    print(json.dumps(report))

build()
