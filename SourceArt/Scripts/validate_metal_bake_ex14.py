"""Blender MCP regression check for linked metallic albedo and shader restoration."""
import bpy,json,os
import esn_lib as L
ROOT='C:/Users/HP/Documents/GitHub/proyectos-unity'

def run():
    previous=bpy.context.window.scene;old_dir=L.TEX_DIR
    scene=bpy.data.scenes.new('QA_MetalAlbedo');bpy.context.window.scene=scene
    material=None
    try:
        col=bpy.data.collections.new('QA_MetalAlbedo');scene.collection.children.link(col)
        obj=L.box('QA_MetalAlbedo',(1,1,.1),(0,0,.05),col)
        material=L.material('QA_MetalAlbedo',(.25,.12,.03),.5,1,edge_wear=0,ao=0,bevel=0)
        L.assign(obj,material);L.uv_project(obj)
        nt=material.node_tree;p=L._principled(material)
        color=nt.nodes.new('ShaderNodeRGB');color.outputs[0].default_value=(.25,.12,.03,1);nt.links.new(color.outputs[0],p.inputs['Base Color'])
        emission=nt.nodes.new('ShaderNodeRGB');emission.outputs[0].default_value=(.01,.03,.06,1);nt.links.new(emission.outputs[0],p.inputs['Emission Color'])
        strength=nt.nodes.new('ShaderNodeValue');strength.outputs[0].default_value=.23;nt.links.new(strength.outputs[0],p.inputs['Emission Strength'])
        L.TEX_DIR=ROOT+'/SourceArt/_evidence/EX-14/qa-pbr';os.makedirs(L.TEX_DIR,exist_ok=True)
        path=L.bake_pbr([obj],'QA_MetalAlbedo',size=128,samples=1,only=('BaseColor',))['BaseColor']
        poly=max(obj.data.polygons,key=lambda face:face.area);uv=obj.data.uv_layers.active.data
        u=sum(uv[i].uv.x for i in poly.loop_indices)/len(poly.loop_indices);v=sum(uv[i].uv.y for i in poly.loop_indices)/len(poly.loop_indices)
        image=bpy.data.images.load(path,check_existing=False);index=(int(v*image.size[1])*image.size[0]+int(u*image.size[0]))*4
        rgba=list(image.pixels[index:index+4])
        links_restored=(p.inputs['Emission Color'].links[0].from_socket==emission.outputs[0] and p.inputs['Emission Strength'].links[0].from_socket==strength.outputs[0])
        report={'linked_base_color':[.25,.12,.03],'metallic':p.inputs['Metallic'].default_value,'baked_rgba':rgba,'emission_links_restored':links_restored,'temporary_state_empty':not L._bake_saved}
        assert rgba[0]>rgba[1]>rgba[2]>.05 and rgba[0]>.2,report
        assert links_restored and not L._bake_saved and report['metallic']==1,report
        report['passed']=True
        with open(L.TEX_DIR+'/regression.json','w') as f:json.dump(report,f,indent=2)
        return report
    finally:
        L.TEX_DIR=old_dir;bpy.context.window.scene=previous
        for obj in list(scene.objects):bpy.data.objects.remove(obj,do_unlink=True)
        bpy.data.scenes.remove(scene)
        if material:bpy.data.materials.remove(material)
