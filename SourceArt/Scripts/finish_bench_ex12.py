"""Run after build_bench_ex12.py through Blender MCP. Bake, pack and export."""
import bpy,os,sys,json,shutil
ROOT='C:/Users/HP/Documents/GitHub/proyectos-unity'
sys.path.insert(0,ROOT+'/SourceArt/Scripts');import esn_lib as L
asset='OBJ-008_BancoIndustrial';s=bpy.context.scene
o=next(x for x in s.objects if x.type=='MESH');assert 'OBJ008' in o.name
stage=ROOT+'/SourceArt/_evidence/EX-12/bench/staging';os.makedirs(stage,exist_ok=True)
old_dir=L.TEX_DIR;L.TEX_DIR=stage
try: maps=L.bake_pbr([o],asset,size=1024,samples=24)
finally:L.TEX_DIR=old_dir
with open(ROOT+'/SourceArt/_evidence/EX-12/bench/bake.json','w') as f:json.dump(maps,f,indent=2)
mat=o.data.materials[0]
for name,path in maps.items():
    img=bpy.data.images.load(path,check_existing=True);img.pack()
    node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=img;node.label='Runtime baked '+name
    shutil.copy2(path,ROOT+'/EsneiderProtocoloLazaro/Assets/_Game/Art/Textures/'+os.path.basename(path))
bpy.data.libraries.write(ROOT+'/SourceArt/Blender/'+asset+'.blend',{s},fake_user=True)
old=o.data;o.data=old.copy();o.data.materials.clear();o.data.materials.append(mat)
for polygon in o.data.polygons:polygon.material_index=0
try:
    with L.ctx(o):
        bpy.ops.export_scene.fbx(filepath=ROOT+'/EsneiderProtocoloLazaro/Assets/_Game/Art/Models/'+asset+'.fbx',
            use_selection=True,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Z',axis_up='Y',
            object_types={'MESH'},bake_space_transform=True,mesh_smooth_type='FACE',use_mesh_modifiers=True,
            bake_anim=False,path_mode='STRIP',embed_textures=False)
finally:o.data=old
print(maps)
