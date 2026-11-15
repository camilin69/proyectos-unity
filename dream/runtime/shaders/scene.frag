#version 330 core
in vec3 worldPos;in vec3 worldNormal;in vec2 uv;flat in int matId;
in float ao;
out vec4 frag;
uniform vec4 baseRough[32];
uniform vec4 properties[32];
uniform vec3 eye;
uniform vec2 resolution;
uniform int reflected;
uniform int renderPass,environment;
uniform int debugShading;
uniform int reflectionSurface;
uniform float time;
uniform float farClip;
uniform sampler2D plaid;
uniform sampler2D reflection;
uniform sampler2D sky;
uniform sampler2D ceramicNormal;
uniform sampler2D ceramicRough;
uniform sampler2D sceneColor,sceneDepth,leafDetail,biosphere;
uniform sampler2D floorReflection;
uniform sampler2D floorSurface,floorFlow,roomProbe;
uniform int localLightCount;
uniform vec4 localLights[16],localRadiance[16];
const float PI=3.14159265;
vec3 env(vec3 d){return texture(sky,vec2(atan(d.y,d.x)/(2.*PI)+.5,asin(clamp(d.z,-1.,1.))/PI+.5)).rgb;}
vec3 stairMappedNormal(vec3 n,vec3 sampleNormal,float strength){
 // Environment 3 exports per-face metric UVs, including the vertical risers.
 // Reconstruct the UV frame without a new tangent vertex attribute. Grass
 // uses world XY UVs; vertical end caps can therefore have zero UV area.
 vec3 dpdx=dFdx(worldPos),dpdy=dFdy(worldPos);
 vec2 duvdx=dFdx(uv),duvdy=dFdy(uv);
 float determinant=duvdx.x*duvdy.y-duvdx.y*duvdy.x;
 vec3 t=normalize(cross(abs(n.z)>.95?vec3(0,1,0):vec3(0,0,1),n));
 vec3 b=cross(n,t);
 if(abs(determinant)>1e-10){
   vec3 tangent=(dpdx*duvdy.y-dpdy*duvdx.y)/determinant;
   vec3 bitangent=(dpdy*duvdx.x-dpdx*duvdy.x)/determinant;
   tangent-=n*dot(n,tangent);
   if(dot(tangent,tangent)>1e-12){
     t=normalize(tangent);b=cross(n,t);
     if(dot(b,bitangent)<0.)b=-b;
   }
 }
 vec3 bump=sampleNormal*2.-1.;
 return normalize(n*max(bump.z,.1)+strength*(bump.x*t+bump.y*b));
}
vec3 roomEnvironment(vec3 origin,vec3 direction,float rough){
 // Box projection anchors the static probe to the room enclosure instead of
 // reflecting a distant blue sky through solid interior walls.
 vec3 lo=vec3(-2.4,-2.7,.016),hi=vec3(.45,2.7,3.2);
 vec3 safeDirection=mix(vec3(-1.),vec3(1.),step(vec3(0.),direction))*max(abs(direction),vec3(.0001));
 vec3 exitDistance=max((lo-origin)/safeDirection,(hi-origin)/safeDirection);
 float distance=max(0.,min(exitDistance.x,min(exitDistance.y,exitDistance.z)));
 vec3 ray=normalize(origin+direction*distance-vec3(-.85,.3,1.45));
 vec2 probeUV=vec2(atan(ray.y,ray.x)/(2.*PI)+.5,asin(clamp(ray.z,-1.,1.))/PI+.5);
 vec2 dx=dFdx(probeUV),dy=dFdy(probeUV);
 dx.x-=round(dx.x);dy.x-=round(dy.x); // longitude seam is periodic
 vec2 size=vec2(textureSize(roomProbe,0));
 float pixelFootprint=max(length(dx*size),length(dy*size));
 float roughFootprint=1.+rough*rough*size.x/PI;
 // Respect both the GGX lobe and the footprint of a thin curved tube. Fixed
 // low LOD made individual reflected tiles sparkle like a woven fabric.
 return textureLod(roomProbe,probeUV,log2(max(roughFootprint,max(pixelFootprint,1.)))).rgb;
}
float depthMetres(float d){return 2.*.05*farClip/(farClip+.05-(d*2.-1.)*(farClip-.05));}
vec3 light(vec3 n,vec3 v,vec3 l,vec3 base,float rough,float metal,vec3 radiance){
 vec3 h=normalize(v+l);float nv=max(dot(n,v),.001),nl=max(dot(n,l),0.);
 float nh=max(dot(n,h),0.),vh=max(dot(v,h),0.);float a=rough*rough,a2=a*a;
 float den=nh*nh*(a2-1.)+1.;float D=a2/max(PI*den*den,.0001);
 float k=(rough+1.)*(rough+1.)/8.;float G=nv/(nv*(1.-k)+k)*nl/(nl*(1.-k)+k);
 vec3 f0=mix(vec3(.04),base,metal);vec3 F=f0+(1.-f0)*pow(1.-vh,5.);
 return ((1.-F)*(1.-metal)*base/PI+D*G*F/max(4.*nv*nl,.001))*radiance*nl;
}
vec3 floorSpecularReturn(vec3 p,vec3 n,vec3 v,vec3 base,float rough){
 // Continuous area return from the wet floor, complementing the LDR probe.
 // Above a vertical tube, the reflected view points down toward this surface.
 vec3 ray=reflect(-v,n);
 // Evaluate derivatives before masking upward rays; derivatives inside a
 // fragment-dependent early-return branch are undefined near that boundary.
 float distance=(.05-p.z)/min(ray.z,-.001);
 vec2 hit=(p+ray*distance).xy;
 float spread=max(.025,max(distance*rough*rough,.5*length(fwidth(hit))));
 vec2 lower=smoothstep(vec2(-1.7,-2.2)-spread,vec2(-1.7,-2.2)+spread,hit);
 vec2 upper=smoothstep(vec2(-.7,.8)-spread,vec2(-.7,.8)+spread,hit);
 // Difference of cumulative filters preserves area under broad footprints.
 // Multiplying four edges would leave residual light as spread -> infinity.
 vec2 axis=max(lower-upper,vec2(0.));float coverage=axis.x*axis.y;
 vec3 f=base+(1.-base)*pow(1.-max(dot(n,v),0.),5.);
 return vec3(.90,.96,1.)*.75*coverage*f*float(ray.z<-.001&&p.z>.05);
}
vec3 waveEmitterReturn(vec3 n,vec3 v,vec3 delta,float radius,float rough,vec3 intensity){
 // Finite spherical emitter approximation, evaluated at each real tread's
 // world position. A single floor reflection plane would float above stairs.
 // Filter the reflected disk by roughness and the pixel footprint; preserve
 // its integrated solid angle as that footprint grows. This covers emitters,
 // not reflections of the surrounding architecture or visibility/shadows.
 float distance=max(length(delta),radius+.001);
 vec3 direction=delta/distance,ray=reflect(-v,n);
 float angularRadius=asin(clamp(radius/distance,0.,.99));
 float angle=acos(clamp(dot(ray,direction),-1.,1.));
 float blur=max(rough*rough,max(fwidth(angle),.001));
 float outer=angularRadius+blur;
 float coverage=1.-smoothstep(max(0.,angularRadius-blur),outer,angle);
 coverage*=angularRadius*angularRadius/(outer*outer);
 float fresnel=.04+.96*pow(1.-max(dot(n,v),0.),5.);
 return intensity/(PI*radius*radius)*coverage*fresnel*float(dot(n,direction)>0.);
}
vec3 waveCorridor(int kind,vec3 n,vec3 v,vec3 base,float rough,float metal){
 // Environment 4 owns these slots: wall, paint normal, floor roughness,
 // ceiling, sign, floor colour/normal, and packed linear surface data.
 vec2 metricUV=uv;
 vec2 paintUV=metricUV/vec2(5.5436925067,4.4651979429)+vec2(.38914925865,.68636455012);
 if(kind==13){
   base=texture(floorSurface,paintUV).rgb;
   rough=texture(ceramicRough,paintUV).r;
   n=stairMappedNormal(n,texture(floorFlow,metricUV/.5).rgb,1.6);
 }else if(kind==14||kind==15){
   base=kind==14?texture(plaid,metricUV/.5).rgb:texture(leafDetail,metricUV/.5).rgb;
   vec2 surface=texture(roomProbe,metricUV/.5).rg;
   rough=kind==14?surface.r:surface.g;
   n=stairMappedNormal(n,texture(ceramicNormal,metricUV/.5).rgb,kind==14?.5:1.);
 }else if(kind==16)base=texture(biosphere,clamp(uv,vec2(.002),vec2(.998))).rgb;
 if(debugShading==1)return base;
 if(debugShading==2)return n*.5+.5;
 if(debugShading==3)return vec3(ao);
 if(kind==7)return base*max(properties[matId].w,1.);
 vec3 color=base*(kind==13?1.:.55)*mix(.65,1.,ao);
 for(int i=0;i<localLightCount;i++){
   int receiver=int(localRadiance[i].w+.1);
   if((receiver==1&&kind!=13)||(receiver==2&&kind!=15))continue;
   vec3 delta=localLights[i].xyz-worldPos;
   float distance=max(length(delta),.02);
   vec3 radiance=localRadiance[i].rgb/(.5+distance*distance);
   // Finite emitter size softens the point proxy's GGX lobe. Fixtures remain
   // actual meshes; these highlights move with the view and surface normals.
   float effectiveRough=sqrt(rough*rough+localLights[i].w/distance*.12);
   color+=light(n,v,delta/distance,base,clamp(effectiveRough,.08,1.),metal,radiance)*ao;
   if(kind==13)color+=.55*waveEmitterReturn(n,v,delta,localLights[i].w,.13,localRadiance[i].rgb)*ao;
 }
 if(kind==16)color+=base*6.*texture(roomProbe,clamp(uv,vec2(.002),vec2(.998))).b;
 return color;
}
vec3 oceanExitWater(vec3 n,vec3 v,vec3 base){
 vec2 screenUV=gl_FragCoord.xy/resolution;
 float surfaceDepth=depthMetres(gl_FragCoord.z);
 vec2 detailUV=uv*2.+vec2(0.,-time*.0666667);
 vec3 ripple=texture(floorFlow,detailUV*4.).xyz*2.-1.;
 n=normalize(n+vec3(ripple.xy*.12,0.));
 float opaqueDepth=depthMetres(texture(sceneDepth,screenUV).r);
 vec2 distortion=n.xy*.018*clamp((opaqueDepth-surfaceDepth)*.35,0.,1.);
 vec2 refractUV=clamp(screenUV+distortion,vec2(.002),vec2(.998));
 if(depthMetres(texture(sceneDepth,refractUV).r)<surfaceDepth)refractUV=screenUV;
 float thickness=max(depthMetres(texture(sceneDepth,refractUV).r)-surfaceDepth,0.);
 vec3 transmitted=texture(sceneColor,refractUV).rgb;
 vec3 absorption=exp(-vec3(.92,.13,.08)*min(thickness,18.));
 float offshore=smoothstep(5.2,6.0,worldPos.y);
 vec3 shallowTint=mix(vec3(.018,.38,.29),vec3(.006,.028,.052),offshore);
 vec3 body=transmitted*absorption+shallowTint*(1.-absorption);
 vec3 reflected=texture(reflection,clamp(vec2(screenUV.x,1.-screenUV.y)+n.xy*.012,vec2(.002),vec2(.998))).rgb;
 float fresnel=.075+.72*pow(1.-max(dot(n,v),0.),5.);
 float foam=texture(leafDetail,detailUV).r;
 float shoreline=(1.-smoothstep(.12,.62,abs(worldPos.z)))*smoothstep(-2.15,-1.8,worldPos.y);
 float foamAmount=clamp((smoothstep(.84,.98,foam)*.24+shoreline*.10)*mix(1.,.12,offshore),0.,.30);
 float glint=pow(max(0.,sin(uv.x*31.+sin(uv.y*13.+time*.33))),24.)*.035;
 // The doorway begins at y=5.3m. Anchor the broad pink reflection just beyond
 // its threshold so it reaches both the pool and the near ocean in the shot.
 float exitFalloff=exp(-pow(worldPos.x/1.15,2.)-pow((worldPos.y-6.7)/2.5,2.));
 float reflectedBreakup=.52+.48*texture(leafDetail,detailUV*1.7+vec2(.13,time*.018)).r;
 float reflectionWave=.50+.50*pow(max(0.,.5+.5*sin(uv.x*33.+sin(uv.y*19.+time*.4)*1.7+uv.y*8.)),1.2);
 float roomFalloff=exp(-pow(worldPos.x/1.25,2.)-pow((worldPos.y-2.1)/1.25,2.));
 float roomBreakup=.35+.65*texture(leafDetail,detailUV*1.7+vec2(.13,time*.018)).r;
 vec3 pinkReflection=vec3(.34,.012,.18)*exitFalloff*reflectedBreakup*reflectionWave
                    +vec3(.20,.008,.105)*roomFalloff*roomBreakup;
 body=mix(body,reflected,clamp(fresnel,.035,.58));
 body=mix(body,vec3(.57,.77,.71),foamAmount);
 return body+pinkReflection+glint*vec3(.55,.78,.78);
}
void main(){
 vec4 m=baseRough[matId];float rough=m.a,metal=properties[matId].x;int kind=int(properties[matId].y+.1);
 if(renderPass==0&&(kind==4||kind==6||kind==9))discard;
 if(renderPass==1&&kind!=4)discard;
 if(renderPass==2&&kind!=6&&kind!=9)discard;
 if(reflected==1&&(kind==4||kind==reflectionSurface))discard;
 vec3 n=normalize(worldNormal);if(!gl_FrontFacing)n=-n;
 if(environment==4){frag=vec4(waveCorridor(kind,n,normalize(eye-worldPos),m.rgb,rough,metal),1);return;}
 if(environment==5&&kind==4){frag=vec4(oceanExitWater(n,normalize(eye-worldPos),m.rgb),1);return;}
 if((kind==1&&environment!=0)||(kind==3&&environment!=5)){
   vec3 t=normalize(cross(abs(n.z)<.9?vec3(0,0,1):vec3(0,1,0),n));vec3 b=cross(n,t);
   vec3 bump=texture(ceramicNormal,uv).xyz*2.-1.;n=normalize(n+bump.x*t*.18+bump.y*b*.18);
   rough=clamp(rough*texture(ceramicRough,uv).r/.27,.09,.85);
 }
 vec3 v=normalize(eye-worldPos);vec3 base=m.rgb;
 if(kind==1&&environment==0){
   base=texture(floorSurface,uv).rgb;
   vec2 tilt=(texture(floorFlow,uv).rg*2.-1.)*.65;
   n=normalize(n+vec3(tilt,0));
 }
 if(kind==9){
   // UV.y increases upwards: adding time moves the streaks down the curtain.
   float flow=uv.y*28.+time*3.;
   float strands=pow(.5+.5*sin(uv.x*170.+sin(flow)*.8),5.);
   float beads=pow(.5+.5*sin(flow+uv.x*34.),9.);
   float foam=1.-smoothstep(0.,.12,uv.y);
   vec3 water=mix(base,vec3(.79,.94,1.),clamp(strands*.6+beads*.25+foam*.4,0.,1.));
   float alpha=properties[matId].z*(.48+strands*.4+beads*.12);
   frag=vec4(water,alpha);return;
 }
 if(kind==4){
   vec2 screenUV=gl_FragCoord.xy/resolution;
   float undistortedDepth=depthMetres(texture(sceneDepth,screenUV).r);
   float surfaceDepth=depthMetres(gl_FragCoord.z);
   vec2 distort=n.xy*.025*clamp((undistortedDepth-surfaceDepth)*.5,0.,1.);
   vec2 refractUV=clamp(screenUV+distort,vec2(.002),vec2(.998));
   if(depthMetres(texture(sceneDepth,refractUV).r)<surfaceDepth)refractUV=screenUV;
   float thickness=max(depthMetres(texture(sceneDepth,refractUV).r)-surfaceDepth,0.);
   vec3 transmitted=texture(sceneColor,refractUV).rgb;
   vec3 absorption=exp(-vec3(.7,.10,.07)*thickness);
   vec3 waterColor=transmitted*absorption+vec3(.015,.24,.3)*(1.-absorption);
   vec3 refl=texture(reflection,clamp(vec2(screenUV.x,1.-screenUV.y)+n.xy*.016,vec2(.002),vec2(.998))).rgb;
   float fresnel=.02+.98*pow(1.-max(dot(n,v),0.),5.);
   float caustic=pow(max(0.,1.-abs(sin(worldPos.x*8.+time*.55+sin(worldPos.y*6.)))) ,18.)*.12;
   frag=vec4(mix(waterColor+caustic*exp(-thickness)*vec3(.3,.9,1.),refl,clamp(fresnel,.12,.88)),1);return;
 }
 if(kind==2)base=texture(plaid,uv).rgb;
 if(kind==5)base=texture(leafDetail,uv).rgb*(.75+base.g*.5);
 if(kind==8)base=texture(biosphere,uv).rgb;
 if(environment==5&&kind==3){
   // The capture is pastel and pink, with the green/blue channels lifted by
   // the phone's soft, warm exposure. Keep the ceramic readable without neon.
   base=texture(plaid,uv).rgb*vec3(.85,1.60,1.30);
   n=stairMappedNormal(n,texture(ceramicNormal,uv).xyz,.52);
   rough=clamp(rough*texture(ceramicRough,uv).r,.08,.75);
 }
 if(environment==5&&kind==7)base=texture(biosphere,clamp(uv,vec2(.002),vec2(.998))).rgb;
 if(environment==5&&kind==8)base=texture(floorSurface,clamp(uv,vec2(.002),vec2(.998))).rgb;
 if(kind==11){
   // The kitchen profile binds its grass maps to these two existing slots.
   // World UVs remain continuous across the doorway, meadow and grass blades.
   float treeGrassLod=0.;
   if(environment==6){
     vec2 texSize=vec2(textureSize(floorSurface,0));
     vec2 dx=dFdx(uv)*texSize,dy=dFdy(uv)*texSize;
     treeGrassLod=clamp(log2(max(max(length(dx),length(dy)),1.))+1.,0.,9.);
     base=textureLod(floorSurface,uv,treeGrassLod).rgb;
   }else base=texture(floorSurface,uv).rgb;
   if(properties[matId].w<.5){
     vec3 bump=texture(floorFlow,uv).xyz*2.-1.;
     if(environment==3)n=stairMappedNormal(n,texture(floorFlow,uv).xyz,.28);
     else n=normalize(n+vec3(bump.xy*.28,0.));
   }
 }
 if(environment==6&&kind==0){
   base=texture(plaid,uv).rgb;
   base*=mix(vec3(.78),vec3(1.),clamp(base.r,0.,1.));
   n=stairMappedNormal(n,texture(ceramicNormal,uv).rgb,.42);
   rough=clamp(texture(ceramicRough,uv).r,.68,1.);
 }
 if(environment==6&&kind==5){
   base=texture(leafDetail,uv).rgb;
   rough=.92;
 }
 if(environment==6&&kind==11){
   vec2 texSize=vec2(textureSize(floorFlow,0));
   vec2 dx=dFdx(uv)*texSize,dy=dFdy(uv)*texSize;
   float treeGrassLod=clamp(log2(max(max(length(dx),length(dy)),1.))+1.,0.,9.);
   n=stairMappedNormal(n,textureLod(floorFlow,uv,treeGrassLod).rgb,.22);
   rough=clamp(texture(biosphere,uv).r,.78,1.);
 }
 if(environment==6&&kind==17){
   // A static, mesh-shaped canopy shadow complements the real Blender sun
   // shadow while keeping the OpenGL profile inexpensive on integrated GPUs.
   frag=vec4(base*.42,1);return;
 }
 if(environment==3&&kind==12){
   // Opaque plush, variant 0: pink fibre albedo plus a linear normal map.
   // The same UV convention covers treads, risers and explicit fine fibres.
   base=texture(plaid,uv).rgb;
   n=stairMappedNormal(n,texture(ceramicNormal,uv).xyz,.42);
   rough=clamp(rough,.88,1.);metal=0.;
 }
 if(debugShading>0){frag=vec4(debugShading==1?base:(debugShading==2?n*.5+.5:vec3(ao)),1);return;}
 if(kind==6){float f=.05+.95*pow(1.-abs(dot(n,v)),5.);frag=vec4(mix(base*.65,env(reflect(-v,n)),f),max(.1,properties[matId].z)+f*.42);return;}
 if(environment==5){
   if(kind==7){frag=vec4(base*3.1,1);return;}
   if(kind==8){frag=vec4(base*.88,1);return;}
   float ambient=kind==10?.82:(kind==3?.60:.31);
   vec3 color=base*vec3(ambient,ambient*.97,ambient*.91)*mix(.82,1.,ao);
   for(int i=0;i<localLightCount;i++){
     vec3 delta=localLights[i].xyz-worldPos;float distance=max(length(delta),.025);
     vec3 radiance=localRadiance[i].rgb/(1.+dot(delta,delta)*.30);
     color+=light(n,v,delta/distance,base,max(rough,.2),metal,radiance)*mix(.68,1.,ao);
   }
   vec3 reflectionColor=env(reflect(-v,n));
   float fresnel=.04+.96*pow(1.-max(dot(n,v),0.),5.);
   color+=reflectionColor*fresnel*mix(.035,.22,1.-rough);
   if(kind==3)color+=base*.10*pow(1.-max(dot(n,v),0.),3.);
   if(kind==10)color*=vec3(.64,.57,.55);
   frag=vec4(color,1);return;
 }
 if(kind==7){frag=vec4(base*1.2,1);return;}
 vec3 roomRadiance=vec3(.66,.60,.65);
 vec3 color=base*(1.-metal)*(.42+.1*max(n.z,0.))*ao*roomRadiance;
 vec3 positions[3]=vec3[](vec3(-1.1,2.5,2.2),vec3(.25,.9,2.4),vec3(-.975,-.5,2.85));
 vec3 colors[3]=vec3[](vec3(.83,.87,1.)*3.,vec3(1.,.85,.94)*3.5,vec3(.85,1.,.96)*1.8);
 // Broad highlights approximate the large window/door light sources.
 if(environment==0){
   // Limit the broad analytical fill on the upper front ceramic wall. This
   // authored irradiance field is anchored to the room, with a soft height
   // transition; lower tiles, side walls and painted trim keep their fill.
   float upperFrontFill=kind==3?smoothstep(1.45,1.85,worldPos.z)*smoothstep(2.35,2.65,worldPos.y)*smoothstep(.75,.98,-n.y):0.;
   for(int i=0;i<3;i++){vec3 delta=positions[i]-worldPos;color+=light(n,v,normalize(delta),base,max(rough,mix(.48,.30,metal)),metal,colors[i]*roomRadiance*mix(1.,.68,upperFrontFill)/(1.+dot(delta,delta)*.14))*mix(.75,1.,ao);}
   if(metal>.8)color+=floorSpecularReturn(worldPos,n,v,base,rough);
   // The painted leaf faces away from the direct window lights. Give this
   // diffuse paint the missing broad return from the left/front room wall;
   // the glazed ceramics retain their separately calibrated room fill.
   if(kind==0&&metal<.05&&rough<.6){
     vec3 wallReturn=vec3(-2.25,clamp(worldPos.y,.45,2.45),clamp(worldPos.z,.35,2.60));
     vec3 delta=wallReturn-worldPos;
     vec3 bounce=vec3(1.15,.95,1.45)/(1.+dot(delta,delta)*.65);
     color+=light(n,v,normalize(delta),base,max(rough,.7),metal,bounce)*mix(.65,1.,ao);
   }
 }
 else if(environment==1){color=base*(.48+.18*max(n.z,0.))*ao;color+=light(n,v,normalize(vec3(-.4,-.25,1)),base,max(rough,.3),metal,vec3(1.1,1.04,.93));if(kind==5)color+=base*.18*max(dot(-n,normalize(vec3(-.4,-.25,1))),0.);}
 else if(environment==2){
   // Explicit kitchen lighting: a broad pink ceiling and daylight at the exit.
   // Scene-local diffuse returns calibrated against the kitchen reference.
   float outside=smoothstep(1.65,2.05,worldPos.y);
   vec3 ambient=mix(vec3(.70,.54,.55),vec3(.63,.74,.70),outside);
   color=base*(.72+.22*max(n.z,0.))*ambient*mix(.55,1.,ao);
   vec3 daylight=vec3(.65,2.4,3.2)-worldPos;
   color+=light(n,v,normalize(daylight),base,max(rough,.5),metal,
                vec3(1.25,1.40,1.35)/(1.+dot(daylight,daylight)*.045))*ao;
   vec3 ceiling=vec3(-.25,-.05,2.67)-worldPos;
   color+=light(n,v,normalize(ceiling),base,max(rough,.6),metal,
                vec3(1.40,.50,.85)*(1.-outside)/(1.+dot(ceiling,ceiling)*.4))*ao;
   if(kind==0&&metal<.05){
     // Matte walls/soffit need the broad interior return missing from the
     // analytical lamps. Orientation keeps the ceiling below the wall fill;
     // enamel and cabinetry retain their independently lit highlights.
     float mattePaint=smoothstep(.78,.82,rough)*(1.-outside);
     vec3 paintedReturn=mix(vec3(1.42,1.50,1.23),vec3(2.12,2.35,1.96),
                            1.-abs(n.z));
     color*=mix(vec3(1.),paintedReturn,mattePaint);
     if(rough<.65)color*=mix(vec3(1.15,1.20,1.15),vec3(1.),outside);
   }
   if(kind==11){
     color+=base*.11*max(dot(-n,normalize(vec3(-.2,.4,1.))),0.);
     // Low overlapping blades scatter a warm return indoors and receive a
     // brighter, cooler exterior fill over several metres beyond the doorway.
     float grassDaylight=smoothstep(1.0,5.2,worldPos.y);
     color*=mix(vec3(1.75,1.43,1.30),vec3(2.33,2.11,3.15),grassDaylight);
     // Haze is applied after the return so the horizon cannot overexpose.
     float haze=1.-exp(-max(length(eye-worldPos)-18.,0.)*.005);
     color=mix(color,vec3(.25,.40,.28),haze);
   }
 }
 else if(environment==3){
   // Stair exterior prototype: broad overhead daylight, mint sky fill and
   // a weak pink return. These are scene-local sources, not the room lamps.
   // Geometry, exposure and texture calibration remain separate gates.
   color=base*(1.-metal)*(.45+.20*max(n.z,0.))*vec3(.84,.96,.90)*mix(.65,1.,ao);
   color+=light(n,v,normalize(vec3(-.40,-.65,1.)),base,max(rough,.42),metal,
                vec3(1.55,1.38,1.33))*mix(.65,1.,ao);
   color+=light(n,v,normalize(vec3(.50,.75,.40)),base,max(rough,.75),metal,
                vec3(.28,.46,.37))*ao;
   color+=light(n,v,normalize(vec3(-.20,-.80,.25)),base,max(rough,.80),metal,
                vec3(.28,.13,.18))*ao;
   if(kind==11)color+=base*.08*max(dot(-n,normalize(vec3(-.4,-.65,1.))),0.);
   if(kind==12){
     float sheen=pow(1.-max(dot(n,v),0.),4.);
     color+=mix(base,vec3(1.),.20)*(.085*sheen)*ao;
   }
 }
 else if(environment==6){
   vec3 sunDirection=normalize(vec3(-.50,-.62,1.));
   float skyFill=mix(.58,1.,max(n.z,0.));
   color=base*vec3(.20,.23,.15)*skyFill*mix(.56,1.,ao);
   if(kind!=17){
     vec3 sunRadiance=vec3(2.05,1.92,1.62);
     color+=light(n,v,sunDirection,base,max(rough,.42),metal,sunRadiance)*mix(.55,1.,ao);
   }
   if(kind==5)color+=base*.16*max(dot(-n,sunDirection),0.);
   if(kind==11)color+=base*.06*max(dot(-n,sunDirection),0.);
   if(kind==18)color=base*(.24+.22*max(dot(n,sunDirection),0.))*mix(.7,1.,ao);
 }
 if(kind==1&&environment==0){
   float film=texture(floorFlow,uv).b;
   // Tint the substrate before adding the wet layer's reflections. Reflected
   // objects remain visible across the colored patches instead of being tinted
   // afterwards as if the finish were an opaque decal.
   color*=mix(vec3(.87,.95,.94),vec3(1.60,1.40,1.20),film*.75);
 }
 // Environment contribution complements the analytical direct lighting.
 vec3 fresnel=mix(vec3(.04),base,metal)+(1.-mix(vec3(.04),base,metal))*pow(1.-max(dot(n,v),0.),5.);
 vec3 environmentReflection=environment==0?roomEnvironment(worldPos,reflect(-v,n),rough):env(reflect(-v,n));
 // Roughness redistributes the metal's reflected light; the filtered probe
 // already accounts for that spread, so do not attenuate its energy again.
 if(environment==3){
   // Filter the stair sky for broad metal returns; no planar/wet reflection.
   vec3 ray=reflect(-v,n);
   vec2 skyUV=vec2(atan(ray.y,ray.x)/(2.*PI)+.5,asin(clamp(ray.z,-1.,1.))/PI+.5);
   float lod=log2(1.+rough*rough*float(textureSize(sky,0).x)/PI);
   color+=textureLod(sky,skyUV,lod).rgb*fresnel*mix((1.-rough)*.35,.65,metal);
 }else color+=environmentReflection*fresnel*(environment==0?mix((1.-rough)*.35,1.,metal):(1.-rough)*.35);
 if(kind==1&&reflected==0&&n.z>.5){
   vec2 p=gl_FragCoord.xy/resolution;vec2 sampleUV=vec2(p.x,1.-p.y);
   vec3 reflectedColor;
   if(environment==0){
     sampleUV=clamp(sampleUV+n.xy*.35,vec2(.002),vec2(.998));
     // A broad 9-tap footprint represents the softly scattered wet coating;
     // the separate normal field still breaks up the reflected architecture.
     vec2 blur=vec2(6.)/resolution;
     reflectedColor=texture(reflection,sampleUV).rgb*.20;
     for(int y=-1;y<=1;y++)for(int x=-1;x<=1;x++)if(x!=0||y!=0)
       reflectedColor+=texture(reflection,sampleUV+vec2(x,y)*blur).rgb*.10;
   }else reflectedColor=texture(floorReflection,sampleUV).rgb;
   float facing=pow(1.-max(dot(n,v),0.),4.);
   float f=environment==0?.18+.45*facing:.18+.5*facing;
   color=mix(color,reflectedColor,f);
 }
 // Gentle contact darkening at the base of the walls; not a replacement for shadows.
 float edge=min(min(worldPos.x+2.4,.45-worldPos.x),2.7-abs(worldPos.y));
 if(kind==1&&environment==0)color*=mix(.77,1.,smoothstep(0.,.18,edge));
 frag=vec4(color,1);
}
