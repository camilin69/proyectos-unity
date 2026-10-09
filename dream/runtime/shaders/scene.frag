#version 330 core
in vec3 worldPos;in vec3 worldNormal;in vec2 uv;flat in int matId;
in float ao;
out vec4 frag;
uniform vec4 baseRough[32];
uniform vec4 properties[32];
uniform vec3 eye;
uniform vec2 resolution;
uniform int reflected;
uniform sampler2D plaid;
uniform sampler2D reflection;
uniform sampler2D sky;
uniform sampler2D ceramicNormal;
uniform sampler2D ceramicRough;
const float PI=3.14159265;
vec3 env(vec3 d){return texture(sky,vec2(atan(d.y,d.x)/(2.*PI)+.5,asin(clamp(d.z,-1.,1.))/PI+.5)).rgb;}
vec3 light(vec3 n,vec3 v,vec3 l,vec3 base,float rough,float metal,vec3 radiance){
 vec3 h=normalize(v+l);float nv=max(dot(n,v),.001),nl=max(dot(n,l),0.);
 float nh=max(dot(n,h),0.),vh=max(dot(v,h),0.);float a=rough*rough,a2=a*a;
 float den=nh*nh*(a2-1.)+1.;float D=a2/max(PI*den*den,.0001);
 float k=(rough+1.)*(rough+1.)/8.;float G=nv/(nv*(1.-k)+k)*nl/(nl*(1.-k)+k);
 vec3 f0=mix(vec3(.04),base,metal);vec3 F=f0+(1.-f0)*pow(1.-vh,5.);
 return ((1.-F)*(1.-metal)*base/PI+D*G*F/max(4.*nv*nl,.001))*radiance*nl;
}
void main(){
 vec4 m=baseRough[matId];float rough=m.a,metal=properties[matId].x;int kind=int(properties[matId].y+.1);
 if(reflected==1&&kind==1)discard;
 vec3 n=normalize(worldNormal);if(!gl_FrontFacing)n=-n;
 if(kind==1||kind==3){
   vec3 t=normalize(cross(abs(n.z)<.9?vec3(0,0,1):vec3(0,1,0),n));vec3 b=cross(n,t);
   vec3 bump=texture(ceramicNormal,uv).xyz*2.-1.;n=normalize(n+bump.x*t*.18+bump.y*b*.18);
   rough=clamp(rough*texture(ceramicRough,uv).r/.27,.09,.85);
 }
 vec3 v=normalize(eye-worldPos);vec3 base=m.rgb;
 if(kind==2)base=texture(plaid,uv).rgb;
 if(kind==1){float ir=.5+.5*sin(worldPos.x*2.4+worldPos.y*1.3);base=mix(base,base*vec3(.94,1.12,1.08),ir*.18);}
 vec3 color=base*(.42+.1*max(n.z,0.))*ao;
 vec3 positions[3]=vec3[](vec3(-1.1,2.5,2.2),vec3(2.2,.9,2.4),vec3(0,-.5,2.85));
 vec3 colors[3]=vec3[](vec3(.83,.87,1.)*3.,vec3(1.,.85,.94)*3.5,vec3(.85,1.,.96)*1.8);
 // Broad highlights approximate the large window/door light sources.
 for(int i=0;i<3;i++){vec3 delta=positions[i]-worldPos;color+=light(n,v,normalize(delta),base,max(rough,.48),metal,colors[i]/(1.+dot(delta,delta)*.14))*mix(.75,1.,ao);}
 // Environment contribution complements the analytical direct lighting.
 vec3 fresnel=mix(vec3(.04),base,metal)+(1.-mix(vec3(.04),base,metal))*pow(1.-max(dot(n,v),0.),5.);
 color+=env(reflect(-v,n))*fresnel*(1.-rough)*.35;
 if(kind==1&&reflected==0&&n.z>.5){
   vec2 p=gl_FragCoord.xy/resolution;vec3 reflectedColor=texture(reflection,vec2(p.x,1.-p.y)).rgb;
   float f=.18+.5*pow(1.-max(dot(n,v),0.),4.);color=mix(color,reflectedColor,f);
 }
 // Gentle contact darkening at the base of the walls; not a replacement for shadows.
 float edge=min(2.4-abs(worldPos.x),2.7-abs(worldPos.y));
 if(kind==1)color*=mix(.77,1.,smoothstep(0.,.18,edge));
 frag=vec4(color,1);
}
