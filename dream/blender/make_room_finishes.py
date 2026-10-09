"""Author the continuous, shallow-water-like pastel floor in both renderers.

The albedo includes a 0.6 m checker underneath irregular interference patches.
It is an artistic approximation, not texture recovered from the reference.
Global UV: X [-2.4,.45], Y [-2.7,2.7]. PNG top is positive world Y; BMP and
Blender/OpenGL therefore read the same world-aligned surface without flipping.
By default the production map set is regenerated in assets/textures. Use
--output-dir for a variant; only variants produce comparison images/reports.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import numpy as np
from scipy.ndimage import gaussian_filter, zoom, map_coordinates
from PIL import Image, ImageDraw
from floor_ripple import generate_floor_ripple

ASSET_TEXTURES=Path(__file__).resolve().parents[1]/'assets/textures'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output-dir',type=Path,default=ASSET_TEXTURES,
                    help='Destination for the full map set. Default: active assets/textures; another directory also produces comparison evidence.')
args=parser.parse_args()
root=args.output_dir.resolve()
active_output=root==ASSET_TEXTURES.resolve()
root.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(1431);h,w=1536,1024
y,x=np.meshgrid(np.linspace(2.7,-2.7,h),np.linspace(-2.4,.45,w),indexing='ij')
def noise(cells):
    small=rng.random((round(cells*5.4/2.85),cells))
    return zoom(small,(h/small.shape[0],w/small.shape[1]),order=3)[:h,:w]
def smoothstep(a,b,value):
    t=np.clip((value-a)/(b-a),0,1)
    return t*t*(3-2*t)

large=noise(4);medium=noise(12);small=noise(32);fine=noise(68)
# Place the isolated pools from actual rays through the current portrait
# camera, instead of relying on the global percentage of coloured texels.
camera_values=None;tan_half_fov=None
for line in (ASSET_TEXTURES.parent/'pastel_room.scene').read_text(encoding='utf-8').splitlines():
    parts=line.split()
    if parts and parts[0]=='camera':camera_values=list(map(float,parts[1:]))
    elif parts and parts[0]=='fov':tan_half_fov=float(parts[1])
assert camera_values is not None and tan_half_fov is not None
eye=np.array(camera_values[:3]);yaw,pitch=camera_values[3:]
forward=np.array([math.cos(yaw)*math.cos(pitch),math.sin(yaw)*math.cos(pitch),math.sin(pitch)])
right=np.cross(forward,[0,0,1]);right/=np.linalg.norm(right);up=np.cross(right,forward)
aspect=9/16;floor_z=.016
def floor_hit(screen_u,screen_v):
    direction=forward+right*((2*screen_u-1)*aspect*tan_half_fov)+up*((1-2*screen_v)*tan_half_fov)
    return eye+direction*((floor_z-eye[2])/direction[2])

relative=np.stack([x-eye[0],y-eye[1],np.full_like(x,floor_z-eye[2])],axis=-1)
depth=relative@forward
safe_depth=np.where(np.abs(depth)>.01,depth,.01)
screen_x=.5+.5*(relative@right)/(safe_depth*aspect*tan_half_fov)
screen_y=.5-.5*(relative@up)/(safe_depth*tan_half_fov)
# Reference-relative image coordinates. Main coral/lime pool, far-right pool,
# smaller left pool and faint distant central pool. The foreground stays calm.
patches=[{'name':'main','screen':[.52,.77],'radii':[.125,.044],'gain':1.0},
         {'name':'right','screen':[.87,.68],'radii':[.105,.026],'gain':.72},
         {'name':'left','screen':[.18,.70],'radii':[.105,.031],'gain':.54},
         {'name':'distant','screen':[.57,.645],'radii':[.075,.026],'gain':.38}]
mask=np.zeros((h,w));patch_fields=[]
for i,patch in enumerate(patches):
    u,v=patch['screen'];rx,ry=patch['radii']
    xp=(screen_x-u)/rx;yp=(screen_y-v)/ry
    angle=np.arctan2(yp,xp)
    edge=np.sqrt(xp*xp+yp*yp)
    edge+=.16*np.sin(angle*3+i*1.7)+.10*np.sin(angle*7+i*.6)
    edge+=(small-.5)*.20
    field=(1-smoothstep(.83,1.08,edge))*patch['gain']*(depth>.15)
    # Small bites and inlets break up the edge without filling adjacent tiles.
    field*=1-.65*smoothstep(.65,.78,medium)
    if i==0:
        # Cut asymmetric inlets into the existing footprint. The original mask
        # remains an upper bound, so no bright paint spreads into neutral tiles.
        wx=xp+.15*(medium-.5)+.09*np.sin(yp*8+i)
        wy=yp+.22*(small-.5)+.12*np.sin(xp*9+i*.7)
        warped_angle=np.arctan2(wy,wx)
        irregular=np.sqrt(wx*wx+wy*wy)+.08*np.sin(warped_angle*5)+.07*np.sin(warped_angle*11)
        irregular+=(fine-.5)*.20
        field=np.minimum(field,(1-smoothstep(.78,1.05,irregular))*patch['gain']*(depth>.15))
    patch_fields.append(field);mask=np.maximum(mask,field)
    point=floor_hit(u,v)
    patch['world_center']=point.tolist()
    patch['uv_center']=[float((point[0]+2.4)/2.85),float((point[1]+2.7)/5.4)]
# Raise the existing translucent core, without activating untouched texels.
# This keeps the broad neutral areas while preventing a muddy centre.
hero_coverage=gaussian_filter(smoothstep(.18,.86,patch_fields[0]),6)
mask=gaussian_filter(np.maximum(mask,hero_coverage),3.5)
# Keep the checker visible through the colored film, including its vivid core.
strength=np.minimum(.88,.74*mask+.14*hero_coverage)

# Coral fields with a few lime islands, plus cyan at the low edge of the main
# pool. No repeating hue cycle: that produced the previous long zigzag bands.
island_noise=noise(23)*.75+medium*.25
islands=smoothstep(.42,.60,island_noise)
coral=np.array([238,134,150],dtype=float)/255
lime=np.array([191,206,109],dtype=float)/255
cyan=np.array([114,199,209],dtype=float)/255
film=coral*(1-islands[:,:,None])+lime*islands[:,:,None]
cyan_weight=.58*smoothstep(.788,.82,screen_y)*(patch_fields[0]>.03)
cyan_weight+=.12*(1-smoothstep(.15,.45,medium))
film=film*(1-cyan_weight[:,:,None])+cyan*cyan_weight[:,:,None]
# Within the main focus only, separate coral and lime with a narrower soft
# transition. This avoids their broad desaturated mixture in the old map.
hero_islands=smoothstep(.44,.55,island_noise+.12*(small-.5)+.055*(fine-.5))
hero_coral=np.array([249,102,117],dtype=float)/255
hero_lime=np.array([184,221,59],dtype=float)/255
hero_cyan=np.array([54,216,230],dtype=float)/255
hero_film=hero_coral*(1-hero_islands[:,:,None])+hero_lime*hero_islands[:,:,None]
cyan_focus=.96*np.exp(-((screen_x-.57)/.066)**2-((screen_y-.800)/.019)**2)
hero_film=hero_film*(1-cyan_focus[:,:,None])+hero_cyan*cyan_focus[:,:,None]
hero_weight=hero_coverage
film=film*(1-hero_weight[:,:,None])+hero_film*hero_weight[:,:,None]
linear=lambda c:np.where(c>.04045,((c+.055)/1.055)**2.4,c/12.92)
srgb=lambda c:np.where(c>.0031308,1.055*np.maximum(c,0)**(1/2.4)-.055,c*12.92)
def save(name,rgb):
    im=Image.fromarray(np.uint8(np.rint(np.clip(rgb*255,0,255))))
    im.save(root/f'{name}.png');im.save(root/f'{name}.bmp')

base_colors={'pink':'BEA2AB','mint':'93B3A3'}
colors={}
for name,hexcolor in base_colors.items():
    color=np.array([int(hexcolor[i:i+2],16)/255 for i in (0,2,4)])
    colors[name]=linear(color)
    blend=linear(color)*(1-strength[:,:,None])+linear(film)*strength[:,:,None]
    save(f'floor_{name}_albedo',srgb(blend))

# This is the final slab albedo. Checker borders are gently refracted and
# softened under the clear layer; there are deliberately no dark grout lines.
distort_x=.028*np.sin(y*3.9+x*1.6)+.028*(medium-.5)
distort_y=.022*np.sin(x*4.5-y*2.1)+.023*(small-.5)
checker=np.sin(np.pi*(x+2.4+distort_x)/.6)*np.sin(np.pi*(y+2.7+distort_y)/.6)
pink_weight=.5+.5*np.tanh(checker*13)
base=colors['mint']*(1-pink_weight[:,:,None])+colors['pink']*pink_weight[:,:,None]
# Small low-frequency value variation keeps the neutral regions continuous.
base*=1+(large[:,:,None]-.5)*.06
surface=base*(1-strength[:,:,None])+linear(film)*strength[:,:,None]
# The interior reflection probe replaces the old blue-only sky contribution;
# retain the authored rose/mint substrate instead of pre-absorbing its blue.
neutral_absorption=np.ones(3)
surface*=neutral_absorption*(1-mask[:,:,None])+mask[:,:,None]
save('floor_surface_albedo',srgb(surface))

# The helper owns an independent RNG: accepted albedos and the film mask
# above remain byte-identical. Optional roughness is not integrated.
ripple=generate_floor_ripple(np.uint8(np.rint(np.clip(mask*255,0,255))))
nx,ny,nz=np.moveaxis(ripple['normal'],-1,0)
for name,pixels in [('floor_flow',ripple['flow_rgb']),('floor_normal',ripple['normal_rgb'])]:
    image=Image.fromarray(pixels,'RGB')
    image.save(root/(name+'.png'));image.save(root/(name+'.bmp'))
screen_rows,screen_cols=np.indices((640,360),dtype=float)
screen_u=(screen_cols+.5)/360;screen_v=(screen_rows+.5)/640
rays=forward+right[None,None,:]*((2*screen_u-1)*aspect*tan_half_fov)[:,:,None]+up[None,None,:]*((1-2*screen_v)*tan_half_fov)[:,:,None]
distance=(floor_z-eye[2])/rays[:,:,2]
hits=eye+rays*distance[:,:,None]
visible_floor=(distance>0)&(hits[:,:,0]>=-2.4)&(hits[:,:,0]<=.45)&(hits[:,:,1]>=-2.7)&(hits[:,:,1]<=2.7)
projected_mask=map_coordinates(mask,[(2.7-hits[:,:,1])/5.4*(h-1),(hits[:,:,0]+2.4)/2.85*(w-1)],order=1,mode='constant',cval=0)
manifest={'source':'continuous slab v6 organic ripples with calibrated rose/mint substrate and v5 softened iridescence',
    'output_role':'active' if active_output else 'variant',
    'base_colors_srgb':base_colors,'color_space':'albedo sRGB; flow and normal linear',
    'blend':'linear-light RGB','room_uv_extent_m':[2.85,5.4],
    'world_uv_bounds':{'x':[-2.4,.45],'y':[-2.7,2.7]},'image_top_world_y':2.7,
    'tile_period_m':.6,'joint_style':'soft refracted colour transition, no dark grout',
    'primary_albedo':'floor_surface_albedo.png','seed':1431,
    'ripple_parameters':ripple['parameters'],
    'roughness_policy':'Existing constant material roughness retained; experimental roughness map is not integrated.',
    'neutral_absorption_linear':neutral_absorption.tolist(),
    'hero_palette_srgb':{'coral':np.rint(hero_coral*255).astype(int).tolist(),
                         'lime':np.rint(hero_lime*255).astype(int).tolist(),
                         'cyan':np.rint(hero_cyan*255).astype(int).tolist()},
    'hero_color_policy':'Original pool footprint and film palette retained; neutral checker calibrated against rose/mint floor samples.',
    'placement':{'method':'reference image coordinates raycast onto the current camera floor plane',
                 'camera':camera_values,'tan_half_fov':tan_half_fov,'aspect':aspect,
                 'floor_z':floor_z,'patches':patches},
    'statistics':{'strong_patch_fraction':float(np.mean(mask>.5)),
                  'neutral_fraction':float(np.mean(mask<.1)),
                  'projected_floor_neutral_fraction':float(np.mean(projected_mask[visible_floor]<.1)),
                  'projected_floor_strong_fraction':float(np.mean(projected_mask[visible_floor]>.5)),
                  'projection_scope':'camera rays hitting the slab; excludes no occluding geometry',
                  'normal_xy_rms':float(np.sqrt(np.mean(nx*nx+ny*ny))),
                  'normal_xy_p95':float(np.percentile(np.sqrt(nx*nx+ny*ny),95)),
                  'normal_statistics_source':'analytic scalar-height field from floor_ripple.generate_floor_ripple/v6'},
    'limitation':'Artistic approximation with fixed albedo colors. Reflections respond to view angle; this is not a physical thin-film simulation.'}
(root/'floor_finish.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')

# Production regenerates only the five PNG/BMP pairs and their manifest. A
# variant never writes the active set, so its baseline remains valid for the
# comparisons below. This also avoids comparing active output with itself.
if active_output:
    print('Regenerated active continuous floor albedo, normal and flow maps in',root)
    raise SystemExit(0)

# Projection of texture values only: this intentionally excludes lighting and
# reflections, which the renderers add independently. Camera comes from the
# same scene manifest used above, including the real floor plane and bounds.
def project_map(path):
    data=np.asarray(Image.open(path).convert('RGB'),dtype=np.float32)
    coordinates=[(2.7-hits[:,:,1])/5.4*(data.shape[0]-1),(hits[:,:,0]+2.4)/2.85*(data.shape[1]-1)]
    projected=np.stack([map_coordinates(data[:,:,channel],coordinates,order=1,mode='constant',cval=0) for channel in range(3)],axis=-1)
    projected[~visible_floor]=[37,40,48]
    return Image.fromarray(np.uint8(np.clip(projected,0,255)))

candidate_projection=project_map(root/'floor_surface_albedo.png')
candidate_projection.save(root/'floor_projection.png')
reference_path=ASSET_TEXTURES.parents[1]/'referencias/estetica/evidencias/video-35/11s.png'
reference=Image.open(reference_path).convert('RGB').resize((360,640),Image.Resampling.LANCZOS)
baseline_projection=project_map(ASSET_TEXTURES/'floor_surface_albedo.png')
contact=Image.new('RGB',(1080,370),(37,40,48));draw=ImageDraw.Draw(contact)
for col,(label,im) in enumerate([('REFERENCE / VIDEO 35 / 11s',reference),
                                 ('ACTIVE ALBEDO / CAMERA PROJECTION',baseline_projection),
                                 ('CANDIDATE ALBEDO / CAMERA PROJECTION',candidate_projection)]):
    draw.text((col*360+10,12),label,fill=(242,242,242))
    contact.paste(im.crop((0,310,360,640)),(col*360,34))
contact.save(root/'floor_projection_contact.png')

verification={'png_bmp_identical':True,'active_textures_modified':False,
              'projection_note':'Texture color only; same camera rays, no illumination, reflection or occluder simulation.',
              'candidate_files':{},'normal_flow_rg_identical':False}
for stem in ['floor_pink_albedo','floor_mint_albedo','floor_surface_albedo','floor_flow','floor_normal']:
    p=root/(stem+'.png');b=root/(stem+'.bmp')
    assert np.array_equal(np.asarray(Image.open(p)),np.asarray(Image.open(b))),stem+' PNG/BMP mismatch'
    verification['candidate_files'][stem]={'png_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                                         'bmp_sha256':hashlib.sha256(b.read_bytes()).hexdigest()}
flow=np.asarray(Image.open(root/'floor_flow.png'));normal=np.asarray(Image.open(root/'floor_normal.png'))
assert np.array_equal(flow[:,:,:2],normal[:,:,:2])
verification['normal_flow_rg_identical']=True
active_normal=np.asarray(Image.open(ASSET_TEXTURES/'floor_normal.png'))
verification['normal_unchanged_from_active']=bool(np.array_equal(normal,active_normal))
active_flow=np.asarray(Image.open(ASSET_TEXTURES/'floor_flow.png'))
old_neutral=active_flow[:,:,2]<=2
active_albedo=np.asarray(Image.open(ASSET_TEXTURES/'floor_surface_albedo.png'))
new_albedo=np.asarray(Image.open(root/'floor_surface_albedo.png'))
verification['neutral_pixel_max_delta_rgb']=int(np.abs(new_albedo[old_neutral].astype(int)-active_albedo[old_neutral].astype(int)).max())
verification['neutral_pixel_mean_delta_rgb']=float(np.abs(new_albedo[old_neutral].astype(int)-active_albedo[old_neutral].astype(int)).mean())
(root/'floor_candidate_validation.json').write_text(json.dumps(verification,indent=2)+'\n',encoding='utf-8')
print('Saved candidate maps and camera projection contact in',root)
print(json.dumps({key:value for key,value in verification.items() if key!='candidate_files'},indent=2))
