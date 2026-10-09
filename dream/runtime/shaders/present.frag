#version 330 core
in vec2 uv;
out vec4 frag;
uniform sampler2D sceneColor,sceneDepth;
uniform int antialias;
uniform float exposure;
void main(){
 vec3 color=texture(sceneColor,uv).rgb;
 if(antialias==1){
   vec2 pixel=1./vec2(textureSize(sceneColor,0));vec3 luma=vec3(.299,.587,.114);
   float nw=dot(texture(sceneColor,uv+vec2(-1,1)*pixel).rgb,luma);
   float ne=dot(texture(sceneColor,uv+vec2(1,1)*pixel).rgb,luma);
   float sw=dot(texture(sceneColor,uv+vec2(-1,-1)*pixel).rgb,luma);
   float se=dot(texture(sceneColor,uv+vec2(1,-1)*pixel).rgb,luma);
   float m=dot(color,luma),low=min(m,min(min(nw,ne),min(sw,se))),high=max(m,max(max(nw,ne),max(sw,se)));
   if(high-low>max(.025,high*.125)){
     vec2 dir=vec2(-(nw+ne-sw-se),nw+sw-ne-se);
     float reduce=max((nw+ne+sw+se)*.03125,.0078125);
     dir=clamp(dir/(min(abs(dir.x),abs(dir.y))+reduce),vec2(-8),vec2(8))*pixel;
     vec3 a=.5*(texture(sceneColor,uv+dir*(-1./6.)).rgb+texture(sceneColor,uv+dir*(1./6.)).rgb);
     vec3 b=a*.5+.25*(texture(sceneColor,uv+dir*-.5).rgb+texture(sceneColor,uv+dir*.5).rgb);
     float lb=dot(b,luma);color=(lb<low||lb>high)?a:b;
   }
 }
 frag=vec4(color*(antialias==1?exp2(exposure):1.),1);gl_FragDepth=texture(sceneDepth,uv).r;
}
