#version 330 core
layout(location=0) in vec3 position;
layout(location=1) in vec3 normal;
layout(location=2) in vec2 texcoord;
layout(location=3) in float material;
layout(location=4) in float occlusion;
uniform mat4 vp;
uniform int reflected;
uniform float reflectionHeight;
uniform float time;
uniform vec4 properties[32];
out vec3 worldPos;
out vec3 worldNormal;
out vec2 uv;
out float ao;
flat out int matId;
void main(){
 matId=int(material+.1);int kind=int(properties[matId].y+.1);
 vec3 p=position,n=normal;
 if(kind==4){
   float a=p.x*2.6+p.y*1.2+time*.9,b=p.x*-1.7+p.y*3.5-time*1.15;
   p.z+=sin(a)*.018+sin(b)*.011;
   n=normalize(vec3(-cos(a)*.0468+cos(b)*.0187,-cos(a)*.0216-cos(b)*.0385,1));
 }
 if(kind==5){float weight=texcoord.y*texcoord.y;p.x+=sin(time*.8+p.y*1.7+p.x)*.035*weight;p.y+=cos(time*.65+p.x*1.3)*.02*weight;}
 if(kind==9){float flutter=sin(texcoord.y*36.+time*4.+texcoord.x*13.)*.012;p+=normal*flutter;}
 worldPos=p;worldNormal=n;uv=texcoord;ao=occlusion;
 gl_Position=vp*vec4(p,1);
 gl_ClipDistance[0]=reflected==1 ? p.z-reflectionHeight-.006 : 1.;
}
