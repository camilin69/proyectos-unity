"""Reusable original-asset delivery; run only within Blender through MCP."""
import bpy,os,json,shutil
from mathutils import Matrix
import esn_lib as L
ROOT='C:/Users/HP/Documents/GitHub/proyectos-unity'

class Batch:
    def __init__(self,series,assets):self.series=series;self.assets=assets;self.scenes={}
    def asset(self,id):return 'OBJ-'+id+'_'+self.assets[id]
    def folder(self,id):return ROOT+'/SourceArt/_evidence/'+self.series+'/'+self.asset(id)
    def save(self,b):
        geo=L.join(b.parts,'GEO-'+b.asset);L.apply_all(geo);L.smooth(geo,40);L.uv_project(geo)
        geo.data.calc_loop_triangles();out=self.folder(b.id);os.makedirs(out,exist_ok=True)
        report={'asset':b.asset,'features':b.features,'triangles':len(geo.data.loop_triangles),'vertices':len(geo.data.vertices),
            'dimensions_blender':list(geo.dimensions),'collision_boxes_blender':b.collision,'uv_layers':len(geo.data.uv_layers),'state':'En produccion'}
        with open(out+'/geometry.json','w') as f:json.dump(report,f,indent=2)
        bpy.data.libraries.write(ROOT+'/SourceArt/Blender/'+b.asset+'.blend',{b.scene},fake_user=True)
        self.scenes[b.id]=b.scene;return report
    def activate(self,id):
        s=self.scenes.get(id)
        if not s:
            with bpy.data.libraries.load(ROOT+'/SourceArt/Blender/'+self.asset(id)+'.blend',link=False) as (src,dst):dst.scenes=src.scenes
            s=dst.scenes[0];self.scenes[id]=s
        bpy.context.window.scene=s;return s
    def render(self,id):
        s=self.activate(id);old=L.EVIDENCE;L.EVIDENCE=self.folder(id)
        try:return L.sheet(self.asset(id),[o for o in s.objects if o.type=='MESH'],views=('iso',),res=640)
        finally:L.EVIDENCE=old
    def finish(self,id,only=None,size=1024,margin=8):
        s=self.activate(id);asset=self.asset(id);o=next(x for x in s.objects if x.type=='MESH')
        for m in o.data.materials:
            for n in m.node_tree.nodes:
                if n.type=='MATH' and n.operation=='MULTIPLY' and n.inputs[0].is_linked:
                    ramp=n.inputs[0].links[0].from_node
                    if ramp.type=='VALTORGB' and ramp.inputs['Fac'].is_linked and ramp.inputs['Fac'].links[0].from_node.type=='NEW_GEOMETRY':n.inputs[1].default_value=.025 if '_rubber' in m.name else .06
        samples=[dict(zip(('x','y','z'),o.matrix_world @ v.co)) for v in list(o.data.vertices)[::max(1,len(o.data.vertices)//64)]]
        with open(self.folder(id)+'/source_coordinates.json','w') as f:json.dump({'vertices':samples},f)
        stage=self.folder(id)+'/staging';os.makedirs(stage,exist_ok=True);old_dir=L.TEX_DIR;L.TEX_DIR=stage
        try:maps=L.bake_pbr([o],asset,size=size,samples=24,only=only,margin=margin)
        finally:L.TEX_DIR=old_dir
        mat=o.data.materials[0]
        for n in list(mat.node_tree.nodes):
            if n.type=='TEX_IMAGE' and n.label in ['Runtime baked '+name for name in maps]:mat.node_tree.nodes.remove(n)
        for name,path in maps.items():
            img=bpy.data.images.load(path,check_existing=False);img.pack()
            n=mat.node_tree.nodes.new('ShaderNodeTexImage');n.image=img;n.label='Runtime baked '+name
            shutil.copy2(path,ROOT+'/EsneiderProtocoloLazaro/Assets/_Game/Art/Textures/'+os.path.basename(path))
        bpy.data.libraries.write(ROOT+'/SourceArt/Blender/'+asset+'.blend',{s},fake_user=True)
        self.export(id)
        receipt=self.folder(id)+'/bake.json';all_maps=json.load(open(receipt)) if only and os.path.isfile(receipt) else {}
        all_maps.update(maps)
        with open(receipt,'w') as f:json.dump(all_maps,f,indent=2)
        return maps
    def export(self,id):
        s=self.activate(id);o=next(x for x in s.objects if x.type=='MESH');asset=self.asset(id)
        mat=o.data.materials[0];old=o.data;matrix=o.matrix_world.copy();o.data=old.copy()
        o.data.transform(matrix);o.matrix_world=Matrix.Identity(4);o.data.materials.clear();o.data.materials.append(mat)
        for p in o.data.polygons:p.material_index=0
        try:
            with L.ctx(o):bpy.ops.export_scene.fbx(filepath=ROOT+'/EsneiderProtocoloLazaro/Assets/_Game/Art/Models/'+asset+'.fbx',use_selection=True,apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Z',axis_up='Y',object_types={'MESH'},bake_space_transform=True,mesh_smooth_type='FACE',use_mesh_modifiers=True,bake_anim=False,path_mode='STRIP',embed_textures=False)
        finally:o.data=old;o.matrix_world=matrix
        return asset
