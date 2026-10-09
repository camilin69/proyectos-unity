"""Author the continuous, shallow-water-like pastel floor in both renderers.

The albedo includes a 0.6 m checker underneath irregular interference patches.
It is an artistic approximation, not texture recovered from the reference.
Global UV: X [-2.4,.45], Y [-2.7,2.7]. PNG top is positive world Y; BMP and
Blender/OpenGL therefore read the same world-aligned surface without flipping.
"""
from pathlib import Path
import json
import math
import numpy as np
from scipy.ndimage import gaussian_filter, zoom, map_coordinates
from PIL import Image

root=Path(__file__).resolve().parents[1]/'assets/textures'
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
for line in (root.parents[0]/'pastel_room.scene').read_text(encoding='utf-8').splitlines():
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
    patch_fields.append(field);mask=np.maximum(mask,field)
    point=floor_hit(u,v)
    patch['world_center']=point.tolist()
    patch['uv_center']=[float((point[0]+2.4)/2.85),float((point[1]+2.7)/5.4)]
mask=gaussian_filter(mask,.75)
strength=.79*mask

# Coral fields with a few lime islands, plus cyan at the low edge of the main
# pool. No repeating hue cycle: that produced the previous long zigzag bands.
islands=smoothstep(.42,.60,noise(23)*.75+medium*.25)
coral=np.array([238,134,150],dtype=float)/255
lime=np.array([191,206,109],dtype=float)/255
cyan=np.array([114,199,209],dtype=float)/255
film=coral*(1-islands[:,:,None])+lime*islands[:,:,None]
cyan_weight=.58*smoothstep(.788,.82,screen_y)*(patch_fields[0]>.03)
cyan_weight+=.12*(1-smoothstep(.15,.45,medium))
film=film*(1-cyan_weight[:,:,None])+cyan*cyan_weight[:,:,None]
linear=lambda c:np.where(c>.04045,((c+.055)/1.055)**2.4,c/12.92)
srgb=lambda c:np.where(c>.0031308,1.055*np.maximum(c,0)**(1/2.4)-.055,c*12.92)
def save(name,rgb):
    im=Image.fromarray(np.uint8(np.rint(np.clip(rgb*255,0,255))))
    im.save(root/f'{name}.png');im.save(root/f'{name}.bmp')

base_colors={'pink':'AAA3AF','mint':'93AAA3'}
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
# Absorption of the neutral wet coating counters the blue environment while
# leaving the localized coral/lime interference colors intact.
neutral_absorption=np.array([1.04,.98,.77])
surface*=neutral_absorption*(1-mask[:,:,None])+mask[:,:,None]
save('floor_surface_albedo',srgb(surface))

# Broad millimetre-scale undulations, with a smaller crossing wave, produce
# a continuous moving-water-like distortion once reflected by the renderer.
height=.008*np.sin(x*4.5+y*2.1)+.006*np.sin(y*5.3-x*1.7)+.004*gaussian_filter(medium,3)
dy,dx=np.gradient(height,-5.4/(h-1),2.85/(w-1))
normal_length=np.sqrt(1+dx*dx+dy*dy)
nx=-dx/normal_length;ny=-dy/normal_length;nz=1/normal_length
save('floor_flow',np.stack([nx*.5+.5,ny*.5+.5,mask],axis=-1))
save('floor_normal',np.stack([nx*.5+.5,ny*.5+.5,nz*.5+.5],axis=-1))
screen_rows,screen_cols=np.indices((640,360),dtype=float)
screen_u=(screen_cols+.5)/360;screen_v=(screen_rows+.5)/640
rays=forward+right[None,None,:]*((2*screen_u-1)*aspect*tan_half_fov)[:,:,None]+up[None,None,:]*((1-2*screen_v)*tan_half_fov)[:,:,None]
distance=(floor_z-eye[2])/rays[:,:,2]
hits=eye+rays*distance[:,:,None]
visible_floor=(distance>0)&(hits[:,:,0]>=-2.4)&(hits[:,:,0]<=.45)&(hits[:,:,1]>=-2.7)&(hits[:,:,1]<=2.7)
projected_mask=map_coordinates(mask,[(2.7-hits[:,:,1])/5.4*(h-1),(hits[:,:,0]+2.4)/2.85*(w-1)],order=1,mode='constant',cval=0)
manifest={'source':'authored isolated interference pools, continuous slab v3',
    'base_colors_srgb':base_colors,'color_space':'albedo sRGB; flow and normal linear',
    'blend':'linear-light RGB','room_uv_extent_m':[2.85,5.4],
    'world_uv_bounds':{'x':[-2.4,.45],'y':[-2.7,2.7]},'image_top_world_y':2.7,
    'tile_period_m':.6,'joint_style':'soft refracted colour transition, no dark grout',
    'primary_albedo':'floor_surface_albedo.png','seed':1431,
    'neutral_absorption_linear':neutral_absorption.tolist(),
    'placement':{'method':'reference image coordinates raycast onto the current camera floor plane',
                 'camera':camera_values,'tan_half_fov':tan_half_fov,'aspect':aspect,
                 'floor_z':floor_z,'patches':patches},
    'statistics':{'strong_patch_fraction':float(np.mean(mask>.5)),
                  'neutral_fraction':float(np.mean(mask<.1)),
                  'projected_floor_neutral_fraction':float(np.mean(projected_mask[visible_floor]<.1)),
                  'projected_floor_strong_fraction':float(np.mean(projected_mask[visible_floor]>.5)),
                  'projection_scope':'camera rays hitting the slab; excludes no occluding geometry',
                  'normal_xy_rms':float(np.sqrt(np.mean(nx*nx+ny*ny))),
                  'normal_xy_p95':float(np.percentile(np.sqrt(nx*nx+ny*ny),95))},
    'limitation':'Artistic approximation with fixed albedo colors. Reflections respond to view angle; this is not a physical thin-film simulation.'}
(root/'floor_finish.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print('Saved continuous floor albedo, normal and reflection-flow maps.')
