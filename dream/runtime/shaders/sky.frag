#version 330 core
in vec2 uv;out vec4 frag;
uniform sampler2D sky;
uniform vec3 forwardDir,rightDir,upDir;
uniform float aspect,tanHalfFov;
void main(){vec2 p=uv*2.-1.;vec3 d=normalize(forwardDir+rightDir*p.x*aspect*tanHalfFov+upDir*p.y*tanHalfFov);vec2 t=vec2(atan(d.y,d.x)/6.2831853+.5,asin(clamp(d.z,-1.,1.))/3.14159265+.5);frag=vec4(texture(sky,t).rgb,1);}
