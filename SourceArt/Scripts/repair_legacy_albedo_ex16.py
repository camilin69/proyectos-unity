"""Repair only legacy albedo using existing source UVs. Run inside Blender MCP."""
import bpy,json,hashlib,struct,os,shutil
from pathlib import Path
import esn_lib as L
ROOT=Path('C:/Users/HP/Documents/GitHub/proyectos-unity')
EVIDENCE=ROOT/'SourceArt/_evidence/EX-16'
SCENES={}

def targets():
    report=json.loads((ROOT/'SourceArt/_evidence/EX-16/audit-before.json').read_text())
    return [r['asset'] for r in report['assets'] if r['status']=='review metallic albedo']

def load(asset):
    if asset not in SCENES:
        with bpy.data.libraries.load(str(ROOT/'SourceArt/Blender'/f'{asset}.blend'),link=False) as (src,dst):
            dst.scenes=src.scenes
        if len(dst.scenes)!=1:raise RuntimeError(f'{asset}: expected isolated source, found {len(dst.scenes)} scenes')
        SCENES[asset]=dst.scenes[0]
    return SCENES[asset]

def meshes(asset,s):
    if asset=='BOT-01_Vigia':
        low=next(c for c in s.collection.children if c.name.startswith('EX11_LOW'))
        return [o for o in low.objects if o.type=='MESH']
    return [o for o in s.objects if o.type=='MESH']

def fingerprint(s):
    h=hashlib.sha256()
    for o in sorted(s.objects,key=lambda o:o.name):
        h.update(o.name.encode());h.update(str(tuple(tuple(row) for row in o.matrix_world)).encode())
        if o.type=='MESH':
            for v in o.data.vertices:h.update(struct.pack('fff',*v.co))
            for p in o.data.polygons:h.update(str(tuple(p.vertices)).encode())
            for uv in o.data.uv_layers:
                for d in uv.data:h.update(struct.pack('ff',*d.uv))
        elif o.type=='ARMATURE':
            for b in o.data.bones:h.update((b.name+str(tuple(b.head_local))+str(tuple(b.tail_local))).encode())
            ad=o.animation_data
            if ad:
                h.update(str(ad.use_nla).encode())
                for tr in ad.nla_tracks:
                    for st in tr.strips:h.update(str((st.name,st.frame_start,st.frame_end,st.action.name if st.action else None)).encode())
    return h.hexdigest()

def inspect_all():
    EVIDENCE.mkdir(parents=True,exist_ok=True);rows=[]
    for asset in targets():
        s=load(asset);objs=meshes(asset,s)
        rows.append({'asset':asset,'scene':s.name,'meshes_to_bake':len(objs),'total_meshes':sum(o.type=='MESH' for o in s.objects),
            'missing_uv':[o.name for o in objs if not o.data.uv_layers],
            'principled_missing':[m.name for o in objs for m in o.data.materials if m and (not m.node_tree or not any(n.type=='BSDF_PRINCIPLED' for n in m.node_tree.nodes))],
            'unassigned_faces':sum(1 for o in objs for p in o.data.polygons if p.material_index>=len(o.data.materials) or not o.data.materials[p.material_index]),
            'fingerprint':fingerprint(s)})
    (EVIDENCE/'source-inspection.json').write_text(json.dumps(rows,indent=2));return rows

def repair(asset):
    s=load(asset);objs=meshes(asset,s);previous=bpy.context.window.scene
    if not objs or any(not o.data.uv_layers for o in objs):raise RuntimeError('Missing source UVs')
    folder=EVIDENCE/asset;folder.mkdir(parents=True,exist_ok=True)
    model=ROOT/'EsneiderProtocoloLazaro/Assets/_Game/Art/Models'/f'{asset}.fbx'
    texdir=ROOT/'EsneiderProtocoloLazaro/Assets/_Game/Art/Textures'
    base=texdir/f'{asset}_BaseColor.png'
    oldimage=bpy.data.images.load(str(base),check_existing=False);size=oldimage.size[0]
    if oldimage.size[1]!=size:raise RuntimeError('Non-square atlas requires explicit handling')
    bpy.data.images.remove(oldimage)
    files=[model]+[texdir/f'{asset}_{suffix}.png' for suffix in ('Normal','Roughness','Metallic')]
    hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    bpy.context.window.scene=s;bpy.context.view_layer.update()
    before=fingerprint(s)
    backup=folder/(asset+'_before.blend')
    if not backup.exists():shutil.copy2(ROOT/'SourceArt/Blender'/f'{asset}.blend',backup)
    if not (folder/'BaseColor_before.png').exists():shutil.copy2(base,folder/'BaseColor_before.png')
    states=[(o,o.hide_get(),o.hide_render) for o in s.objects]
    arms=[(o,o.data.pose_position) for o in s.objects if o.type=='ARMATURE']
    olddir=L.TEX_DIR
    try:
        bpy.context.window.scene=s
        for o in s.objects:
            if o.type=='MESH':o.hide_render=o not in objs;o.hide_set(o not in objs)
        for arm,_ in arms:arm.data.pose_position='REST'
        bpy.context.view_layer.update();L.TEX_DIR=str(folder)
        paths=L.bake_pbr(objs,asset,size=size,samples=48,only=('BaseColor',))
        fresh=bpy.data.images.load(paths['BaseColor'],check_existing=False);fresh.pack()
        # Update existing packed runtime atlas nodes, especially Vigia's two export LODs.
        changed=0
        for mat in {m for o in s.objects if o.type=='MESH' for m in o.data.materials if m}:
            for node in mat.node_tree.nodes:
                if node.type=='TEX_IMAGE' and node.image and Path(node.image.filepath).name==base.name:
                    node.image=fresh;changed+=1
        if changed==0:
            node=objs[0].data.materials[0].node_tree.nodes.new('ShaderNodeTexImage')
            node.image=fresh;node.label='Runtime baked BaseColor'
    finally:
        L.TEX_DIR=olddir
        for o,hidden,render in states:o.hide_set(hidden);o.hide_render=render
        for arm,pose in arms:arm.data.pose_position=pose
        bpy.context.view_layer.update();bpy.context.window.scene=previous
    after=fingerprint(s)
    if before!=after:raise RuntimeError('Geometry, UV, rig or NLA changed during albedo repair')
    for p,digest in hashes.items():
        if hashlib.sha256(Path(p).read_bytes()).hexdigest()!=digest:raise RuntimeError('Protected runtime file changed: '+p)
    bpy.data.libraries.write(str(ROOT/'SourceArt/Blender'/f'{asset}.blend'),{s},fake_user=True)
    shutil.copy2(paths['BaseColor'],base)
    receipt={'asset':asset,'source_meshes_baked':len(objs),'resolution':size,'fingerprint_before':before,'fingerprint_after':after,
        'unchanged_runtime_files_sha256':hashes,'replaced_atlas_nodes':changed,'geometry_uv_rig_preserved':True,'fbx_reexported':False}
    (folder/'repair.json').write_text(json.dumps(receipt,indent=2));return receipt
