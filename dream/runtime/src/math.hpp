#pragma once
#include <cmath>
struct Vec3 {
    float x=0,y=0,z=0;
    Vec3 operator+(Vec3 v)const{return{x+v.x,y+v.y,z+v.z};}
    Vec3 operator-(Vec3 v)const{return{x-v.x,y-v.y,z-v.z};}
    Vec3 operator*(float s)const{return{x*s,y*s,z*s};}
};
inline float dot(Vec3 a,Vec3 b){return a.x*b.x+a.y*b.y+a.z*b.z;}
inline Vec3 cross(Vec3 a,Vec3 b){return{a.y*b.z-a.z*b.y,a.z*b.x-a.x*b.z,a.x*b.y-a.y*b.x};}
inline Vec3 norm(Vec3 a){float n=std::sqrt(dot(a,a));return n>1e-6f?a*(1/n):Vec3{};}
struct Mat4 {float v[16]{};};
inline Mat4 multiply(Mat4 a,Mat4 b){Mat4 m;for(int c=0;c<4;c++)for(int r=0;r<4;r++)for(int k=0;k<4;k++)m.v[c*4+r]+=a.v[k*4+r]*b.v[c*4+k];return m;}
inline Mat4 perspective(float fov,float aspect,float nearZ,float farZ){Mat4 m;float t=1/std::tan(fov*.5f);m.v[0]=t/aspect;m.v[5]=t;m.v[10]=(farZ+nearZ)/(nearZ-farZ);m.v[11]=-1;m.v[14]=2*farZ*nearZ/(nearZ-farZ);return m;}
inline Mat4 look(Vec3 eye,Vec3 forward,Vec3 up){Vec3 f=norm(forward),r=norm(cross(f,up)),u=cross(r,f);Mat4 m;m.v[0]=r.x;m.v[4]=r.y;m.v[8]=r.z;m.v[1]=u.x;m.v[5]=u.y;m.v[9]=u.z;m.v[2]=-f.x;m.v[6]=-f.y;m.v[10]=-f.z;m.v[12]=-dot(r,eye);m.v[13]=-dot(u,eye);m.v[14]=dot(f,eye);m.v[15]=1;return m;}
