"""Closed flexible pouch with crimped borders; execute inside Blender MCP."""
import bpy,sys,math,json
ROOT='C:/Users/HP/Documents/GitHub/proyectos-unity'
sys.path.insert(0,ROOT+'/SourceArt/Scripts')
import esn_lib as L
from esn_delivery import Batch
from build_clinic_fixtures_ex23 import FixtureBuilder
ASSETS={'057':'RacionSellada'}
BATCH=Batch('EX-35',ASSETS)

def material(b,side):
    m=L.material(b.asset+'_'+side,(.4,.45,.35),.55,.15,edge_wear=0,ao=0)
    n=m.node_tree.nodes;l=m.node_tree.links
    tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(ROOT+'/SourceArt/Textures/OBJ-057_'+side+'_EX35.png',check_existing=True);tex.image.pack()
    geo=n.new('ShaderNodeNewGeometry');sep=n.new('ShaderNodeSeparateXYZ');l.new(geo.outputs['Position'],sep.inputs[0]);vec=n.new('ShaderNodeCombineXYZ')
    for axis,width,out in [('X',.2,'X'),('Y',.12,'Y')]:
        r=n.new('ShaderNodeMapRange');r.inputs['From Min'].default_value=-width/2;r.inputs['From Max'].default_value=width/2
        if side=='Back' and axis=='X':r.inputs['From Min'].default_value=width/2;r.inputs['From Max'].default_value=-width/2
        l.new(sep.outputs[axis],r.inputs['Value']);l.new(r.outputs[0],vec.inputs[out])
    l.new(vec.outputs[0],tex.inputs['Vector']);l.new(tex.outputs['Color'],next(x for x in n if x.type=='BSDF_PRINCIPLED').inputs['Base Color'])
    return m

def build(id='057'):
    b=FixtureBuilder(id,ASSETS[id],'EX35')
    nx,ny=17,10;verts=[];faces=[];nside=(nx+1)*(ny+1)
    # Dense stations at the sealed ends; remaining stations describe the inflated body.
    xs=[-.1,-.098,-.096,-.094,-.092]+[-.08+i*.16/9 for i in range(10)]+[.092,.096,.1]
    for side in (1,-1):
        for j in range(ny+1):
            v=j/ny;y=(v-.5)*.12
            for i,x in enumerate(xs):
                u=(x+.1)/.2
                edge=min(1,max(0,(.092-abs(x))/.020))
                bulge=(max(0,math.sin(math.pi*v))**.65)*edge
                # Fold amplitude fades before the readable central information area.
                wrinkle=.0025*math.sin(7*math.pi*v+u*6)*math.exp(-((abs(x)-.073)/.019)**2)*math.sin(math.pi*v)
                h=min(.020,.001+.019*bulge+wrinkle)
                if abs(x)>.09:h=.0008+(.0005 if i%2 else 0)
                # A real notch in one sealed border, rather than a painted triangle.
                xx=x-(.0035 if i==nx and j==8 else 0)
                verts.append((xx,y,.02+side*h))
        off=0 if side==1 else nside
        for j in range(ny):
            for i in range(nx):
                a=off+j*(nx+1)+i;f=(a,a+1,a+nx+2,a+nx+1);faces.append(f if side==1 else f[::-1])
    border=list(range(nx+1))+[j*(nx+1)+nx for j in range(1,ny+1)]+[ny*(nx+1)+i for i in range(nx-1,-1,-1)]+[j*(nx+1) for j in range(ny-1,0,-1)]
    for k,a in enumerate(border):
        c=border[(k+1)%len(border)];faces.append((a,a+nside,c+nside,c))
    mesh=bpy.data.meshes.new('sealed flexible laminate');mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new('GEO-057-pouch',mesh);b.col.objects.link(obj);b.parts=[obj]
    for side in ('Front','Back'):mesh.materials.append(material(b,side))
    for f in mesh.polygons:f.material_index=0 if f.index<nx*ny or f.index>=nx*ny*2 else 1
    b.features=['closed inflated flexible laminate','crimped end seals','corner transport folds','physical tear notch','original current EVA production and expiry label','printed reverse panel']
    b.collision=[];report=BATCH.save(b)
    obj=next(o for o in b.scene.objects if o.type=='MESH');uv=obj.data.uv_layers.active.data
    # Reserve full broad-face atlas regions. The edge wall uses its own strip.
    for face in obj.data.polygons:
        top=face.index<nx*ny;bottom=nx*ny<=face.index<nx*ny*2
        for li in face.loop_indices:
            co=obj.matrix_world@obj.data.vertices[obj.data.loops[li].vertex_index].co
            if top or bottom:uv[li].uv=(.02+(.5+co.x/.2)*.96,(.02 if top else .51)+(.5+co.y/.12)*.46)
            else:uv[li].uv=(.02+uv[li].uv.x*.96,.982+uv[li].uv.y*.012)
    bpy.data.libraries.write(ROOT+'/SourceArt/Blender/'+b.asset+'.blend',{b.scene},fake_user=True)
    return report
def render(id='057'):return BATCH.render(id)
def finish(id='057'):return BATCH.finish(id,size=512,margin=2)
