#version 330 core
layout(location=0) in vec3 position;
layout(location=1) in vec3 normal;
layout(location=2) in vec2 texcoord;
layout(location=3) in float material;
layout(location=4) in float occlusion;
uniform mat4 vp;
uniform int reflected;
out vec3 worldPos;
out vec3 worldNormal;
out vec2 uv;
out float ao;
flat out int matId;
void main(){
 worldPos=position;worldNormal=normal;uv=texcoord;matId=int(material+.1);ao=occlusion;
 gl_Position=vp*vec4(position,1);
 gl_ClipDistance[0]=reflected==1 ? position.z-.03 : 1.;
}
