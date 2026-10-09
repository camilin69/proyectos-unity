"""One world-space ripple variant of the accepted f207845 floor maps.

No Blender, runtime or production assets are changed. The reference image is
used for evaluation only; the scalar height, normals and optional roughness
are stationary world-space fields independent of the camera and color mask.
"""
from pathlib import Path
import argparse
import hashlib
import io
import json
import math
import subprocess

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import map_coordinates
from floor_ripple import generate_floor_ripple

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent
BASELINE='f207845'


def baseline_bytes(name):
    return subprocess.check_output(['git','show',f'{BASELINE}:dream/assets/textures/{name}'],cwd=REPO)


def decode_normal(rgb):
    n=np.asarray(rgb,dtype=np.float64)/127.5-1
    return n/np.maximum(np.linalg.norm(n,axis=-1,keepdims=True),1e-8)


def normal_metrics(n):
    slope=np.linalg.norm(n[:,:,:2],axis=-1)/np.maximum(n[:,:,2],1e-8)
    # Differences at 2.8-3.5 mm texel spacing diagnose continuity, not fidelity.
    step=np.r_[np.linalg.norm(np.diff(n,axis=0),axis=-1).ravel(),
               np.linalg.norm(np.diff(n,axis=1),axis=-1).ravel()]
    angles=np.arctan(slope)*180/np.pi
    return {'slope_rms':float(np.sqrt(np.mean(slope*slope))),
            'slope_p50':float(np.percentile(slope,50)),
            'slope_p95':float(np.percentile(slope,95)),
            'slope_p99':float(np.percentile(slope,99)),
            'tilt_degrees_p95':float(np.percentile(angles,95)),
            'tilt_degrees_max':float(angles.max()),
            'normal_neighbor_delta_p95':float(np.percentile(step,95)),
            'normal_neighbor_delta_max':float(step.max()),
            'normal_mean':n.mean(axis=(0,1)).tolist()}


def save_rgb(directory,stem,rgb):
    im=Image.fromarray(np.uint8(np.clip(np.rint(rgb),0,255)),'RGB')
    im.save(directory/(stem+'.png'))
    im.save(directory/(stem+'.bmp'))
    return np.asarray(im)


def camera_projection(normals, probe, camera, size=(360,640)):
    """Bare specular environment reflection diagnostic, not a scene render."""
    w,h=size
    eye=np.array(camera[:3]);yaw,pitch=camera[3:]
    f=np.array([math.cos(yaw)*math.cos(pitch),math.sin(yaw)*math.cos(pitch),math.sin(pitch)])
    right=np.cross(f,[0,0,1]);right/=np.linalg.norm(right);up=np.cross(right,f)
    xx,yy=np.meshgrid((np.arange(w)+.5)/w,(np.arange(h)+.5)/h)
    ray=f+right[None,None,:]*((2*xx-1)*(9/16)*.7)[:,:,None]+up[None,None,:]*((1-2*yy)*.7)[:,:,None]
    distance=(.016-eye[2])/ray[:,:,2]
    hit=eye+ray*distance[:,:,None]
    visible=(distance>0)&(hit[:,:,0]>=-2.4)&(hit[:,:,0]<=.45)&(hit[:,:,1]>=-2.7)&(hit[:,:,1]<=2.7)
    uv=[(2.7-hit[:,:,1])/5.4*(normals.shape[0]-1),(hit[:,:,0]+2.4)/2.85*(normals.shape[1]-1)]
    n=np.stack([map_coordinates(normals[:,:,c],uv,order=1,mode='nearest') for c in range(3)],axis=-1)
    n/=np.linalg.norm(n,axis=-1,keepdims=True)
    incoming=ray/np.linalg.norm(ray,axis=-1,keepdims=True)
    reflected=incoming-2*(incoming*n).sum(axis=-1,keepdims=True)*n
    u=(np.arctan2(reflected[:,:,1],reflected[:,:,0])/(2*np.pi)+.5)*probe.shape[1]-.5
    v=(.5-np.arcsin(np.clip(reflected[:,:,2],-1,1))/np.pi)*probe.shape[0]-.5
    rgb=np.stack([map_coordinates(probe[:,:,c],(v,u),order=1,mode='wrap') for c in range(3)],axis=-1)
    rgb[~visible]=[34,37,45]
    return Image.fromarray(np.uint8(np.clip(rgb,0,255)),'RGB')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=ROOT/'assets/textures/floor_v6_candidate')
    args=parser.parse_args();dest=args.output_dir.resolve()
    if dest==(ROOT/'assets/textures').resolve():
        parser.error('This experimental generator writes a separate variant, not the production asset directory.')
    dest.mkdir(parents=True,exist_ok=True)
    source_names=[f'{stem}.{ext}' for stem in ['floor_pink_albedo','floor_mint_albedo','floor_surface_albedo','floor_flow','floor_normal'] for ext in ['png','bmp']]
    source={name:baseline_bytes(name) for name in source_names}
    meta=json.loads(baseline_bytes('floor_finish.json'))
    before=np.asarray(Image.open(io.BytesIO(source['floor_normal.png'])).convert('RGB'))
    old_flow=np.asarray(Image.open(io.BytesIO(source['floor_flow.png'])).convert('RGB'))
    h,w=before.shape[:2]
    ripple=generate_floor_ripple(old_flow[:,:,2],include_roughness=True)
    height=ripple['height_m'];normal=ripple['normal']
    normal_rgb=save_rgb(dest,'floor_normal',ripple['normal_rgb'])
    flow=ripple['flow_rgb'];save_rgb(dest,'floor_flow',flow)
    for stem in ['floor_pink_albedo','floor_mint_albedo','floor_surface_albedo']:
        for ext in ['png','bmp']:
            (dest/f'{stem}.{ext}').write_bytes(source[f'{stem}.{ext}'])

    # Separate, optional microscopic roughness. No use of camera, height slope
    # or colored-film mask, avoiding baked highlights and double-counted waves.
    roughness=ripple['roughness']
    save_rgb(dest,'floor_roughness',np.repeat(roughness[:,:,None]*255,3,axis=2))
    np.save(dest/'floor_height_m.npy',height.astype(np.float32))
    display_height=(height-height.min())/(height.max()-height.min())
    Image.fromarray(np.uint16(np.rint(display_height*65535))).save(dest/'floor_height_preview16.png')

    for stem in ['floor_pink_albedo','floor_mint_albedo','floor_surface_albedo','floor_flow','floor_normal','floor_roughness']:
        a=np.asarray(Image.open(dest/(stem+'.png')).convert('RGB'))
        b=np.asarray(Image.open(dest/(stem+'.bmp')).convert('RGB'))
        assert np.array_equal(a,b),stem
    assert np.array_equal(flow[:,:,:2],normal_rgb[:,:,:2])
    assert np.array_equal(flow[:,:,2],old_flow[:,:,2])
    for stem in ['floor_pink_albedo','floor_mint_albedo','floor_surface_albedo']:
        for ext in ['png','bmp']:
            assert (dest/f'{stem}.{ext}').read_bytes()==source[f'{stem}.{ext}']
    assert np.array_equal(normal_rgb[0],normal_rgb[-1]) and np.array_equal(normal_rgb[:,0],normal_rgb[:,-1])

    parameters=dict(ripple['parameters']);parameters['world_bounds_m']=meta['world_uv_bounds']
    report={'schema':'dream.floor_ripple_variant.v6','baseline_commit':BASELINE,'accepted':False,
            'scope':'Candidate material data only. No final Blender/OpenGL render has been produced by this generator.',
            'reference':'dream/referencias/estetica/evidencias/video-35/11s.png',
            'geometry_gate':'dream/validation/room-geometry-review.json: sufficient_for_material_calibration=true; residual geometry differences remain.',
            'before':normal_metrics(decode_normal(before)),'after':normal_metrics(decode_normal(normal_rgb)),
            'parameters':parameters,'source_sha256':{name:hashlib.sha256(blob).hexdigest() for name,blob in source.items()},
            'candidate_sha256':{f'{stem}.{ext}':hashlib.sha256((dest/f'{stem}.{ext}').read_bytes()).hexdigest()
                                for stem in ['floor_pink_albedo','floor_mint_albedo','floor_surface_albedo','floor_flow','floor_normal','floor_roughness'] for ext in ['png','bmp']},
            'checks':{'six_png_bmp_pairs_identical':True,'flow_rg_equals_normal_rg':True,'flow_b_mask_unchanged':True,
                      'three_albedo_pairs_byte_identical_to_baseline':True,'opposite_normal_edges_identical':True},
            'integration':{'required':['Replace floor_normal and floor_flow as one matched pair. Preserve existing UV and linear sampling.'],
                           'optional':['floor_roughness is a linear scalar map; test after normals alone. It is not wired into either renderer here.'],
                           'height':'floor_height_m.npy is signed metres and is diagnostic/source data, not required for runtime displacement.',
                           'diagnostics':'floor_height_preview16.png is a normalized 16-bit height preview, not a runtime texture; contact and reflection diagnostic PNGs are not material maps.',
                           'pending':'Render in both existing backends and compare reference floor highlights and reflection shape. Map statistics are not a likeness score.'}}
    (dest/'floor_v6_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    meta['source']='continuous slab v6 candidate, multiscale organic normal over unchanged v5 colors'
    meta['output_role']='variant';meta['ripple_parameters']=parameters;meta['optional_roughness']='floor_roughness.png'
    encoded_xy=decode_normal(normal_rgb)[:,:,:2]
    meta['statistics']['normal_xy_rms']=float(np.sqrt(np.mean(np.sum(encoded_xy*encoded_xy,axis=-1))))
    meta['statistics']['normal_xy_p95']=float(np.percentile(np.linalg.norm(encoded_xy,axis=-1),95))
    meta['statistics']['normal_statistics_source']='decoded 8-bit candidate normal map'
    (dest/'floor_finish.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')

    # Two explicitly diagnostic visuals, never presented as final scene renders.
    probe=np.asarray(Image.open(io.BytesIO(baseline_bytes('room_probe.png'))).convert('RGB'),dtype=np.float64)
    camera=meta['placement']['camera']
    previous=camera_projection(decode_normal(before),probe,camera)
    proposed=camera_projection(decode_normal(normal_rgb),probe,camera)
    sheet=Image.new('RGB',(720,380),(34,37,45));draw=ImageDraw.Draw(sheet)
    draw.text((10,10),'V5 / ENVIRONMENT REFLECTION DIAGNOSTIC',fill='white')
    draw.text((370,10),'V6 / SAME CAMERA AND ENVIRONMENT',fill='white')
    sheet.paste(previous.crop((0,290,360,640)),(0,28));sheet.paste(proposed.crop((0,290,360,640)),(360,28))
    sheet.save(dest/'floor_reflection_diagnostic.png')
    panel=Image.new('RGB',(1024,530),(34,37,45));draw=ImageDraw.Draw(panel)
    visuals=[('V5 NORMAL XY x5',before),('V6 NORMAL XY x5',normal_rgb),
             ('V6 HEIGHT / NORMALIZED',np.repeat(display_height[:,:,None]*255,3,axis=2)),
             ('OPTIONAL ROUGHNESS / 0..1',np.repeat(roughness[:,:,None]*255,3,axis=2))]
    for index,(label,data) in enumerate(visuals):
        visual=np.asarray(data,dtype=float).copy()
        if index<2:visual[:,:,:2]=127.5+(visual[:,:,:2]-127.5)*5
        im=Image.fromarray(np.uint8(np.clip(visual,0,255))).resize((256,480),Image.Resampling.LANCZOS)
        draw.text((index*256+6,12),label,fill='white');panel.paste(im,(index*256,40))
    panel.save(dest/'floor_maps_contact.png')
    print(json.dumps({'directory':str(dest),'before':report['before'],'after':report['after'],'height_sigma_mm':height.std()*1000,'checks':report['checks']},indent=2))


if __name__=='__main__':
    main()
