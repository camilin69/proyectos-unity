"""EX-50: production models for the nine remaining EX-12 inventory entries."""
import bpy, importlib, json, math, os, sys
ROOT = r"C:/Users/HP/Documents/GitHub/proyectos-unity"
sys.path.insert(0, ROOT + "/SourceArt/Scripts")
import esn_lib as L
importlib.reload(L)

ASSETS = ["OBJ-015_PulseraLazaro", "OBJ-042_CierreContencion", "OBJ-071_EsclusaPresion",
          "OBJ-073_ConsolaPrincipal", "OBJ-075_BarandaPasarela", "OBJ-077_PanelEscape",
          "OBJ-078_CompuertaMonumental", "OBJ-080_ArchivoFisico", "ENV-EXIT_ExteriorEscape"]

def mats():
    return {
        "steel": L.material("M_Steel", (.14,.17,.18), .38, .78, wear=.22, bump=.16, scale=18),
        "dark": L.material("M_DarkPolymer", (.035,.045,.05), .58, .12, wear=.12, bump=.08),
        "rubber": L.material("M_Rubber", (.018,.022,.024), .86, 0, bump=.24, scale=30),
        "paper": L.material("M_Paper", (.58,.53,.42), .92, 0, wear=.18, bump=.08),
        "red": L.material("M_Emergency", (.34,.018,.012), .42, .18, wear=.28),
        "cyan": L.material("M_StatusCyan", (.01,.08,.10), .28, .18, emission=((.02,.72,1.0),4)),
        "amber": L.material("M_StatusAmber", (.18,.07,.006), .3, .12, emission=((1.0,.23,.015),3)),
        "concrete": L.material("M_ExteriorRock", (.11,.12,.115), .94, 0, wear=.2, bump=.5, scale=7),
    }

def add_box(n,s,p,m,bevel=.015,rot=(0,0,0)):
    o=L.box(n,s,p,bevel=bevel,segs=2,rot=rot); L.assign(o,m); return o
def add_cyl(n,r,d,p,m,axis='Z'):
    o=L.cyl(n,r,d,p,axis=axis,verts=20,bevel=.004); L.assign(o,m); return o

def bracelet(m):
    o=L.torus("wrist_band", .036, .010, (0,0,.04), axis='Z', segs=40, rings=10); L.assign(o,m["dark"])
    add_box("closure",(.026,.018,.014),(0,-.038,.04),m["steel"],.003)
    add_box("identity_plate",(.052,.004,.022),(0,.039,.04),m["paper"],.002)
    add_box("printed_name_ESNEIDER",(.038,.002,.003),(0,.042,.045),m["dark"],.0004)
    add_box("printed_date_2042_11_07",(.031,.002,.0025),(0,.042,.036),m["red"],.0004)

def latch(m):
    add_box("housing",(.30,.15,.20),(0,0,.10),m["steel"],.018)
    add_box("service_cover",(.22,.012,.13),(0,-.081,.11),m["dark"],.008)
    add_cyl("locking_pin",.026,.30,(.13,0,.10),m["steel"],axis='X')
    add_cyl("servo_actuator",.047,.16,(-.05,0,.10),m["dark"],axis='X')
    add_cyl("status_light",.018,.012,(-.10,-.084,.145),m["cyan"],axis='Y')
    add_box("control_cable",(.025,.035,.28),(-.11,.03,-.11),m["rubber"],.01)

def airlock(m):
    add_box("floor",(3.4,3.8,.16),(0,0,.08),m["steel"],.025)
    for y in (-1.82,1.82):
        add_box("frame_top",(3.4,.26,.28),(0,y,3.18),m["steel"],.035)
        for x in (-1.57,1.57): add_box("frame_side",(.26,.26,3.2),(x,y,1.6),m["steel"],.035)
        add_box("pressure_door",(3.0,.16,3.0),(0,y,1.58),m["dark"],.045)
        add_cyl("door_actuator",.10,1.15,(1.38,y-.14 if y>0 else y+.14,1.65),m["steel"],axis='Z')
        add_box("door_seal",(3.08,.035,3.08),(0,y-.10 if y>0 else y+.10,1.58),m["rubber"],.035)
    add_box("pressure_control",(.34,.18,.55),(1.2,-1.62,1.35),m["dark"],.025)
    add_box("pressure_display",(.23,.012,.16),(1.2,-1.72,1.42),m["cyan"],.004)
    for x in (-1.65,1.65): add_box("wall",(.12,3.4,3.35),(x,0,1.67),m["steel"],.02)

def console(m):
    add_box("console_body",(2.4,.9,.82),(0,0,.41),m["steel"],.045)
    add_box("sloped_dashboard",(2.22,.55,.18),(0,-.18,.91),m["dark"],.025,rot=(math.radians(-14),0,0))
    for i,x in enumerate((-.72,0,.72)):
        add_box("screen_%02d"%i,(.58,.018,.31),(x,-.445,1.10),m["cyan"],.012,rot=(math.radians(-8),0,0))
        for j in range(5): add_box("key_%02d_%02d"%(i,j),(.065,.05,.018),(x-.15+j*.075,-.47,.84),m["amber"],.005)
    for x in (-1.03,1.03): add_box("maintenance_hinge",(.08,.05,.36),(x,.46,.43),m["dark"],.01)
    add_box("cable_trunk",(.18,.20,.52),(0,.5,.24),m["rubber"],.035)

def catwalk(m):
    add_box("walkway_deck",(7.5,2.75,.16),(0,0,2.5),m["steel"],.018)
    for x in (-3.55,-1.2,1.2,3.55):
        for y in (-1.18,1.18): add_box("support",(.18,.18,2.5),(x,y,1.25),m["steel"],.015)
    for y in (-1.32,1.32):
        add_cyl("handrail",.045,7.4,(0,y,3.58),m["steel"],axis='X')
        for x in (-3.6,-2.4,-1.2,0,1.2,2.4,3.6): add_cyl("rail_post",.035,1.05,(x,y,3.03),m["steel"],axis='Z')
    for x in range(-7,8): add_box("grating_%02d"%x,(.035,2.55,.025),(x*.48,0,2.595),m["dark"],.002)

def escape_panel(m):
    add_box("panel_housing",(.35,.15,.50),(0,0,.25),m["steel"],.025)
    add_box("instruction_plate",(.26,.012,.15),(0,-.081,.37),m["paper"],.005)
    add_cyl("release_button",.055,.035,(0,-.105,.23),m["red"],axis='Y')
    add_cyl("permission_light",.022,.018,(.105,-.10,.39),m["cyan"],axis='Y')
    add_box("pull_handle",(.16,.045,.035),(0,-.13,.105),m["dark"],.012)

def monumental(m):
    for x in (-1.48,1.48): add_box("gate_leaf_L" if x<0 else "gate_leaf_R",(2.92,.42,5.4),(x,0,2.7),m["steel"],.07)
    for x in (-2.72,2.72):
        add_box("guide_column",(.42,.75,5.9),(x,.08,2.95),m["dark"],.035)
        add_cyl("hydraulic_piston",.14,3.9,(x,-.46,2.1),m["steel"],axis='Z')
    add_box("top_lock",(2.0,.62,.42),(0,0,5.62),m["dark"],.04)
    add_box("central_seal",(.16,.48,5.25),(0,-.05,2.68),m["rubber"],.025)
    for z in (.6,1.8,3.0,4.2): add_box("reinforcement",(5.72,.10,.18),(0,-.26,z),m["dark"],.018)

def archive(m):
    add_box("document_tray",(.72,.48,.055),(0,0,.028),m["steel"],.012)
    for i in range(5):
        add_box("folder_%02d"%i,(.59,.39,.012),(-.025+i*.011,.01-i*.008,.07+i*.014),m["paper"],.003,rot=(0,0,math.radians(-3+i*1.4)))
    for i in range(12):
        x=-.22+(i%4)*.145; y=-.13+(i//4)*.13
        add_box("DOC-%02d"%(i+1),(.12,.095,.004),(x,y,.16+i*.0005),m["paper"],.001,rot=(0,0,math.radians((i%3-1)*4)))
        add_box("photo_ink_%02d"%(i+1),(.085,.055,.001),(x,y-.008,.163+i*.0005),m["dark"],.0003)

def exterior(m):
    add_box("escape_platform",(8,6,.30),(0,0,.15),m["steel"],.04)
    add_box("safe_path",(4,18,.20),(0,8,.10),m["concrete"],.08)
    for x in (-7.0,7.0): add_box("cliff_wall",(5.0,24,8),(x,6,2.0),m["concrete"],.18,rot=(0,math.radians(7 if x<0 else -7),0))
    for i in range(7):
        x=(-1 if i%2 else 1)*(2.8+(i%3)*.7); y=2+i*2.1
        o=L.sphere("rock_%02d"%i,1,(x,y,.55),segs=16,rings=8,scale=(1.4,.9,.7)); L.assign(o,m["concrete"])
    for x in (-1.8,1.8):
        add_cyl("path_light_post",.05,1.0,(x,2,.65),m["steel"])
        add_cyl("path_light",.12,.10,(x,2,1.18),m["amber"])
    add_box("horizon_occluder",(30,2,7),(0,18,2.0),m["concrete"],.1)

BUILDERS=[bracelet,latch,airlock,console,catwalk,escape_panel,monumental,archive,exterior]

def build_all():
    results=[]
    for asset,builder in zip(ASSETS,BUILDERS):
        L.reset_scene(); materials=mats(); builder(materials)
        objs=[o for o in bpy.context.scene.objects if o.type=='MESH']
        L.uv_project_all(objs)
        blend=L.save_blend(asset); fbx,size=L.export_fbx(objs,asset,bake_anim=False)
        folder=ROOT+"/SourceArt/_evidence/EX-50/"+asset; os.makedirs(folder,exist_ok=True)
        old=L.EVIDENCE; L.EVIDENCE=folder
        try: sheets=L.sheet(asset,objs,res=640)
        finally: L.EVIDENCE=old
        rep=L.report(asset,objs,{"series":"EX-50","blend":blend,"fbx":fbx,"fbx_bytes":size,"texture_sets":1,"sheets":sheets,"state":"En produccion"})
        with open(folder+"/delivery.json","w",encoding="utf-8") as f: json.dump(rep,f,indent=2)
        results.append({"asset":asset,"triangles":rep["tris"],"parts":rep["parts"],"fbx_bytes":size})
    return results

if __name__ == "__main__": print(json.dumps(build_all(),indent=2))
