#include "gl_api.hpp"
#include "math.hpp"
#include "scene.hpp"
#include <algorithm>
#include <array>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <sstream>
#include <vector>
#include <cstring>
#include <memory>
namespace fs=std::filesystem;
static constexpr float pi=3.14159265359f;
static Vec3 eye{-.05f,-1.35f,1.6f};
static float yaw=1.32f,pitch=-.24f;
static bool captured=false,firstMouse=true;
static double mouseX=0,mouseY=0;
static Vec3 forward(){return{std::cos(yaw)*std::cos(pitch),std::sin(yaw)*std::cos(pitch),std::sin(pitch)};}
static void cursor(GLFWwindow*,double x,double y){if(!captured)return;if(firstMouse){mouseX=x;mouseY=y;firstMouse=false;}yaw-=float(x-mouseX)*.002f;pitch=std::clamp(pitch-float(y-mouseY)*.002f,-1.5f,1.5f);mouseX=x;mouseY=y;}
static void mouse(GLFWwindow* w,int button,int action,int){if(button==GLFW_MOUSE_BUTTON_LEFT&&action==GLFW_PRESS){captured=true;firstMouse=true;glfwSetInputMode(w,GLFW_CURSOR,GLFW_CURSOR_DISABLED);}}
static std::string readText(const fs::path& path){std::ifstream f(path);if(!f)throw std::runtime_error("Cannot read "+path.string());return{std::istreambuf_iterator<char>(f),{}};}
static GLuint shader(GLenum type,const std::string& text){GLuint s=glCreateShader(type);const char* p=text.c_str();glShaderSource(s,1,&p,nullptr);glCompileShader(s);GLint ok;glGetShaderiv(s,GL_COMPILE_STATUS,&ok);if(!ok){char log[8192]{};glGetShaderInfoLog(s,sizeof(log),nullptr,log);throw std::runtime_error(log);}return s;}
static GLuint program(const fs::path& dir,const char* name){GLuint v=shader(GL_VERTEX_SHADER,readText(dir/(std::string(name)+".vert"))),f=shader(GL_FRAGMENT_SHADER,readText(dir/(std::string(name)+".frag"))),p=glCreateProgram();glAttachShader(p,v);glAttachShader(p,f);glLinkProgram(p);GLint ok;glGetProgramiv(p,GL_LINK_STATUS,&ok);if(!ok){char log[8192]{};glGetProgramInfoLog(p,sizeof(log),nullptr,log);throw std::runtime_error(log);}glDeleteShader(v);glDeleteShader(f);return p;}
static void vec(GLuint p,const char* name,Vec3 v){glUniform3f(glGetUniformLocation(p,name),v.x,v.y,v.z);}
static void integer(GLuint p,const char* name,int v){glUniform1i(glGetUniformLocation(p,name),v);}
static void scalar(GLuint p,const char* name,float v){glUniform1f(glGetUniformLocation(p,name),v);}
static GLuint bitmap(const fs::path& file,bool srgb=true){
 std::ifstream f(file,std::ios::binary);unsigned char h[54]{};f.read((char*)h,54);
 auto u32=[&](int at){uint32_t v;std::memcpy(&v,h+at,4);return v;};
 if(!f||h[0]!='B'||h[1]!='M'||h[28]!=24||u32(30)!=0)throw std::runtime_error("Expected uncompressed RGB24 BMP: "+file.string());
 uint32_t w=u32(18),height=u32(22),stride=(w*3+3)&~3u;
 if(!w||!height||w>8192||height>8192)throw std::runtime_error("Invalid BMP dimensions");
 std::vector<unsigned char> data(size_t(stride)*height);f.seekg(u32(10));f.read((char*)data.data(),data.size());if(!f)throw std::runtime_error("Truncated BMP");
 GLuint t;glGenTextures(1,&t);glBindTexture(GL_TEXTURE_2D,t);glTexImage2D(GL_TEXTURE_2D,0,srgb?GL_SRGB8:GL_RGB8,w,height,0,GL_BGR,GL_UNSIGNED_BYTE,data.data());glGenerateMipmap(GL_TEXTURE_2D);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR_MIPMAP_LINEAR);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_REPEAT);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_REPEAT);return t;
}
static void texture(int unit,GLuint tex){glActiveTexture(GL_TEXTURE0+unit);glBindTexture(GL_TEXTURE_2D,tex);}
struct Mesh{
 struct GlassRange { GLint first;GLsizei count;Vec3 center; };
 std::vector<GlassRange> glass;
 bool water=false,floor=false,hasGlass=false;
 GLuint vao=0,vbo=0;uint32_t count=0;std::vector<std::array<float,4>> base,props;
 ~Mesh(){if(vbo)glDeleteBuffers(1,&vbo);if(vao)glDeleteVertexArrays(1,&vao);}
 explicit Mesh(const fs::path& path){
  std::ifstream f(path,std::ios::binary);char magic[8];uint32_t mats;f.read(magic,8);f.read((char*)&mats,4);f.read((char*)&count,4);
  if(!f||std::memcmp(magic,"DREAMM02",8)||mats==0||mats>32||count>3000000||count%3)throw std::runtime_error("Invalid dreammesh header");
  for(uint32_t i=0;i<mats;i++){float a[8];f.read((char*)a,sizeof(a));base.push_back({a[0],a[1],a[2],a[3]});props.push_back({a[4],a[5],a[6],a[7]});if(int(a[5]+.1f)==4)water=true;if(int(a[5]+.1f)==1)floor=true;if(int(a[5]+.1f)==6)hasGlass=true;}
  std::vector<float> vertices(size_t(count)*10);f.read((char*)vertices.data(),vertices.size()*sizeof(float));if(!f)throw std::runtime_error("Truncated mesh");
  glGenVertexArrays(1,&vao);glBindVertexArray(vao);glGenBuffers(1,&vbo);glBindBuffer(GL_ARRAY_BUFFER,vbo);glBufferData(GL_ARRAY_BUFFER,vertices.size()*sizeof(float),vertices.data(),GL_STATIC_DRAW);
  int offsets[]={0,3,6,8,9},sizes[]={3,3,2,1,1};for(int i=0;i<5;i++){glEnableVertexAttribArray(i);glVertexAttribPointer(i,sizes[i],GL_FLOAT,GL_FALSE,10*sizeof(float),(void*)(size_t(offsets[i])*sizeof(float)));}
  fs::path ranges=path;ranges.replace_extension(".draws");std::ifstream rf(ranges);GlassRange r{};
  while(rf>>r.first>>r.count>>r.center.x>>r.center.y>>r.center.z){if(r.first<0||r.count<0||uint64_t(r.first)+r.count>count)throw std::runtime_error("Invalid glass draw range");glass.push_back(r);}
  if(hasGlass&&glass.empty())throw std::runtime_error("Missing glass draw groups: "+ranges.string());
 }
};
struct ReflectTarget{
 GLuint fbo=0,color=0,depth=0;int width=0,height=0;
 ReflectTarget(){glGenFramebuffers(1,&fbo);glGenTextures(1,&color);glGenTextures(1,&depth);}
 void resize(int w,int h){
  if(w==width&&h==height)return;
  width=w;height=h;
  glBindTexture(GL_TEXTURE_2D,color);glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA16F,w,h,0,GL_RGBA,GL_FLOAT,nullptr);
  glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE);
  glBindTexture(GL_TEXTURE_2D,depth);glTexImage2D(GL_TEXTURE_2D,0,GL_DEPTH_COMPONENT24,w,h,0,GL_DEPTH_COMPONENT,GL_FLOAT,nullptr);
  glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE);
  glBindFramebuffer(GL_FRAMEBUFFER,fbo);glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,color,0);glFramebufferTexture2D(GL_FRAMEBUFFER,GL_DEPTH_ATTACHMENT,GL_TEXTURE_2D,depth,0);
  if(glCheckFramebufferStatus(GL_FRAMEBUFFER)!=GL_FRAMEBUFFER_COMPLETE)throw std::runtime_error("Incomplete render target");
  glBindFramebuffer(GL_FRAMEBUFFER,0);
 }
};
static void screenshot(const fs::path& path,int w,int h){std::vector<unsigned char> data(size_t(w)*h*3);glPixelStorei(GL_PACK_ALIGNMENT,1);glReadPixels(0,0,w,h,GL_RGB,GL_UNSIGNED_BYTE,data.data());std::ofstream f(path,std::ios::binary);f<<"P6\n"<<w<<" "<<h<<"\n255\n";for(int y=h-1;y>=0;y--)f.write((char*)data.data()+size_t(y)*w*3,w*3);if(!f)throw std::runtime_error("Screenshot write failed");}
