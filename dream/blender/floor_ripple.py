"""Pure, deterministic world-space floor ripple field.

No filesystem, Git, Blender, image library or global random state is used here.
The input mask is copied unchanged into flow B; it does not drive the waves.
Callers choose where and how to serialize the returned maps.
"""
import numpy as np
from scipy.ndimage import map_coordinates

RIPPLE_SEED=680613


def _periodic_endpoint(a):
    return np.pad(a,((0,1),(0,1)),mode='wrap')


def generate_floor_ripple(mask_u8, *, seed=RIPPLE_SEED,
                          world_extent_m=(2.85,5.4), include_roughness=False):
    """Return scalar height, normalized normals and matching RGB8 normal/flow.

    ``mask_u8`` is a 2D uint8 array, PNG top = +world Y. R/G encode +X/+Y.
    The height and its derivatives are periodic over the entire world extent,
    with matching endpoint texels. No caller array or external RNG is mutated.
    Optional roughness is separate experimental data, disabled in production.
    """
    mask=np.asarray(mask_u8)
    if mask.ndim!=2 or mask.dtype!=np.uint8 or min(mask.shape)<32:
        raise ValueError('mask_u8 must be a 2D uint8 map of at least 32 pixels per axis')
    if len(world_extent_m)!=2 or not all(np.isfinite(v) and v>0 for v in world_extent_m):
        raise ValueError('world_extent_m must contain two positive finite lengths')
    h,w=mask.shape;ny,nx=h-1,w-1
    dx=world_extent_m[0]/nx;dy=world_extent_m[1]/ny
    fx=np.fft.fftfreq(nx,d=dx)[None,:]
    fy=-np.fft.fftfreq(ny,d=dy)[:,None]
    radial=np.sqrt(fx*fx+fy*fy)
    rng=np.random.default_rng(seed)

    def band(wavelength,octaves=.42):
        raw=rng.normal(size=(ny,nx))
        log_distance=np.log2(np.maximum(radial,1e-5)*wavelength)
        filt=np.exp(-.5*(log_distance/octaves)**2);filt[0,0]=0
        value=np.fft.ifft2(np.fft.fft2(raw)*filt).real
        return (value-value.mean())/value.std()

    grid_y,grid_x=np.indices((ny,nx),dtype=np.float64)
    warp_x=band(1.65,.30)*.075
    warp_y=band(1.35,.32)*.075
    warp_coords=(grid_y-warp_y/dy,grid_x+warp_x/dx)
    envelope=.35+1.35/(1+np.exp(-1.5*band(.95,.40)))
    components=[(1.25,.00220),(.38,.00165),(.11,.00024)]
    height=np.zeros((ny,nx),np.float64)
    for index,(wavelength,amplitude_m) in enumerate(components):
        component=map_coordinates(band(wavelength),warp_coords,order=3,mode='grid-wrap')
        height+=component*amplitude_m*(1 if index==0 else envelope)
    height-=height.mean()
    spectrum=np.fft.fft2(height)
    gx=np.fft.ifft2(spectrum*(2j*np.pi*fx)).real
    gy=np.fft.ifft2(spectrum*(2j*np.pi*fy)).real
    gain=.045/float(np.sqrt(np.mean(gx*gx+gy*gy)))
    height*=gain;gx*=gain;gy*=gain
    height=_periodic_endpoint(height);gx=_periodic_endpoint(gx);gy=_periodic_endpoint(gy)
    normal=np.stack([-gx,-gy,np.ones((h,w))],axis=-1)
    normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
    normal_rgb=np.uint8(np.clip(np.rint((normal*.5+.5)*255),0,255))
    flow_rgb=np.dstack([normal_rgb[:,:,:2],mask])
    roughness=None
    if include_roughness:
        roughness=_periodic_endpoint(.095+.080/(1+np.exp(-band(.65,.45)*1.1)))

    parameters={'generator':'floor_ripple.generate_floor_ripple/v6',
                'seed':seed,'world_extent_m':list(world_extent_m),'shape':[w,h],
                'basis':'periodic scalar-height Fourier bands; world-space cubic domain warp; analytic spectral derivatives',
                'bands':[{'central_wavelength_m':wave,'unscaled_height_sigma_m':amp,'spectral_width_octaves':.42} for wave,amp in components],
                'domain_warp_sigma_m':.075,'middle_fine_amplitude_envelope':[.35,1.70],
                'height_global_gain':gain,'target_slope_rms':.045,
                'normal_encoding':'linear RGB; R=+world X / +U, G=+world Y / +V; PNG top is +Y; normalized Z positive',
                'continuity':'Periodic height and derivatives, duplicated first/last texels in both dimensions. Apply once over the whole slab UV; not per checker tile.',
                'height_min_m':float(height.min()),'height_max_m':float(height.max()),'height_sigma_m':float(height.std())}
    if roughness is not None:
        parameters.update(roughness_range=[.095,.175],roughness_mean=float(roughness.mean()))
    return {'height_m':height,'normal':normal,'normal_rgb':normal_rgb,
            'flow_rgb':flow_rgb,'roughness':roughness,'parameters':parameters}
