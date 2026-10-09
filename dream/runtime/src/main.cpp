#include "gl_api.hpp"
#include "math.hpp"
#include <algorithm>
#include <array>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <sstream>
#include <vector>
#include <cstring>
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
 GLuint vao=0,vbo=0;uint32_t count=0;std::vector<std::array<float,4>> base,props;
 explicit Mesh(const fs::path& path){
  std::ifstream f(path,std::ios::binary);char magic[8];uint32_t mats;f.read(magic,8);f.read((char*)&mats,4);f.read((char*)&count,4);
  if(!f||std::memcmp(magic,"DREAMM02",8)||mats==0||mats>32||count>3000000||count%3)throw std::runtime_error("Invalid dreammesh header");
  for(uint32_t i=0;i<mats;i++){float a[8];f.read((char*)a,sizeof(a));base.push_back({a[0],a[1],a[2],a[3]});props.push_back({a[4],a[5],0,0});}
  std::vector<float> vertices(size_t(count)*10);f.read((char*)vertices.data(),vertices.size()*sizeof(float));if(!f)throw std::runtime_error("Truncated mesh");
  glGenVertexArrays(1,&vao);glBindVertexArray(vao);glGenBuffers(1,&vbo);glBindBuffer(GL_ARRAY_BUFFER,vbo);glBufferData(GL_ARRAY_BUFFER,vertices.size()*sizeof(float),vertices.data(),GL_STATIC_DRAW);
  int offsets[]={0,3,6,8,9},sizes[]={3,3,2,1,1};for(int i=0;i<5;i++){glEnableVertexAttribArray(i);glVertexAttribPointer(i,sizes[i],GL_FLOAT,GL_FALSE,10*sizeof(float),(void*)(size_t(offsets[i])*sizeof(float)));}
 }
};
struct ReflectTarget{
 GLuint fbo=0,color=0,depth=0;int width=0,height=0;
 ReflectTarget(){glGenFramebuffers(1,&fbo);glGenTextures(1,&color);glGenRenderbuffers(1,&depth);}
 void resize(int w,int h){if(w==width&&h==height)return;width=w;height=h;glBindTexture(GL_TEXTURE_2D,color);glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA16F,w,h,0,GL_RGBA,GL_FLOAT,nullptr);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE);glBindRenderbuffer(GL_RENDERBUFFER,depth);glRenderbufferStorage(GL_RENDERBUFFER,GL_DEPTH_COMPONENT24,w,h);glBindFramebuffer(GL_FRAMEBUFFER,fbo);glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,color,0);glFramebufferRenderbuffer(GL_FRAMEBUFFER,GL_DEPTH_ATTACHMENT,GL_RENDERBUFFER,depth);if(glCheckFramebufferStatus(GL_FRAMEBUFFER)!=GL_FRAMEBUFFER_COMPLETE)throw std::runtime_error("Incomplete reflection FBO");glBindFramebuffer(GL_FRAMEBUFFER,0);}
};
static void screenshot(const fs::path& path,int w,int h){std::vector<unsigned char> data(size_t(w)*h*3);glPixelStorei(GL_PACK_ALIGNMENT,1);glReadPixels(0,0,w,h,GL_RGB,GL_UNSIGNED_BYTE,data.data());std::ofstream f(path,std::ios::binary);f<<"P6\n"<<w<<" "<<h<<"\n255\n";for(int y=h-1;y>=0;y--)f.write((char*)data.data()+size_t(y)*w*3,w*3);if(!f)throw std::runtime_error("Screenshot write failed");}
int main(int argc,char** argv){try{
 fs::path root=fs::absolute(fs::path(argv[0])).parent_path().parent_path().parent_path();fs::path shot;int frameLimit=0,width=960,height=720;bool hidden=false,smoke=false;
 for(int i=1;i<argc;i++){std::string a=argv[i];if(a=="--root"&&i+1<argc)root=argv[++i];else if(a=="--capture"&&i+1<argc)shot=argv[++i];else if(a=="--frames"&&i+1<argc)frameLimit=std::stoi(argv[++i]);else if(a=="--width"&&i+1<argc)width=std::stoi(argv[++i]);else if(a=="--height"&&i+1<argc)height=std::stoi(argv[++i]);else if(a=="--hidden")hidden=true;else if(a=="--smoke")smoke=true;else throw std::runtime_error("Unknown/incomplete argument: "+a);}
 if(width<64||height<64||width>8192||height>8192||frameLimit<0)throw std::runtime_error("Invalid dimensions/frame count");
 if(!shot.empty()&&frameLimit==0)frameLimit=1;
 if(smoke){float originalYaw=yaw;captured=true;firstMouse=false;cursor(nullptr,10,0);if(yaw>=originalYaw)throw std::runtime_error("Mouse orientation test failed");yaw=originalYaw;captured=false;firstMouse=true;std::cout<<"mouse_orientation=PASS\n";}
 glfwSetErrorCallback([](int code,const char* message){std::cerr<<"GLFW "<<code<<": "<<message<<"\n";});
 if(!glfwInit())throw std::runtime_error("GLFW initialization failed");
 glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR,3);glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR,3);glfwWindowHint(GLFW_OPENGL_PROFILE,GLFW_OPENGL_CORE_PROFILE);glfwWindowHint(GLFW_SRGB_CAPABLE,GLFW_TRUE);glfwWindowHint(GLFW_VISIBLE,hidden?GLFW_FALSE:GLFW_TRUE);
 GLFWwindow* window=glfwCreateWindow(width,height,"DREAM | WASD mover - clic mirar - Esc liberar - R reiniciar",nullptr,nullptr);if(!window)throw std::runtime_error("OpenGL 3.3 context unavailable");glfwMakeContextCurrent(window);glfwSwapInterval(hidden?0:1);loadGL();glfwSetCursorPosCallback(window,cursor);glfwSetMouseButtonCallback(window,mouse);
 std::cout<<"GPU: "<<glGetString(GL_RENDERER)<<"\nOpenGL: "<<glGetString(GL_VERSION)<<"\n";
 GLuint sceneProgram=program(root/"runtime/shaders","scene"),skyProgram=program(root/"runtime/shaders","sky"),emptyVao;glGenVertexArrays(1,&emptyVao);
 Mesh mesh(root/"assets/pastel_room.dreammesh");GLuint sky=bitmap(root/"assets/textures/cloud_sky.bmp"),plaid=bitmap(root/"assets/textures/curtain_plaid.bmp"),ceramicNormal=bitmap(root/"assets/textures/ceramic_normal.bmp",false),ceramicRough=bitmap(root/"assets/textures/ceramic_roughness.bmp",false);ReflectTarget reflect;
 glUseProgram(sceneProgram);glUniform4fv(glGetUniformLocation(sceneProgram,"baseRough"),mesh.base.size(),mesh.base[0].data());glUniform4fv(glGetUniformLocation(sceneProgram,"properties"),mesh.props.size(),mesh.props[0].data());integer(sceneProgram,"sky",0);integer(sceneProgram,"plaid",1);integer(sceneProgram,"reflection",2);
 integer(sceneProgram,"ceramicNormal",3);integer(sceneProgram,"ceramicRough",4);
 glUseProgram(skyProgram);integer(skyProgram,"sky",0);scalar(skyProgram,"tanHalfFov",.9f);
 double previous=glfwGetTime(),begin=previous,lastTitle=previous;int frames=0;
 auto draw=[&](Vec3 pos,Vec3 dir,bool mirrored,int w,int h){
  glViewport(0,0,w,h);glClearColor(.4f,.5f,.6f,1);glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT);
  Vec3 up{0,0,1};Vec3 right=norm(cross(dir,up)),camUp=cross(right,dir);
  texture(0,sky);texture(1,plaid);texture(2,mirrored?0:reflect.color);texture(3,ceramicNormal);texture(4,ceramicRough);
  glDisable(GL_DEPTH_TEST);glDisable(GL_CLIP_DISTANCE0);glUseProgram(skyProgram);vec(skyProgram,"forwardDir",dir);vec(skyProgram,"rightDir",right);vec(skyProgram,"upDir",camUp);scalar(skyProgram,"aspect",float(w)/h);glBindVertexArray(emptyVao);glDrawArrays(GL_TRIANGLES,0,3);
  glEnable(GL_DEPTH_TEST);glEnable(GL_CLIP_DISTANCE0);glUseProgram(sceneProgram);vec(sceneProgram,"eye",pos);integer(sceneProgram,"reflected",mirrored?1:0);glUniform2f(glGetUniformLocation(sceneProgram,"resolution"),w,h);Mat4 vp=multiply(perspective(2*std::atan(.9f),float(w)/h,.05f,200),look(pos,dir,up));glUniformMatrix4fv(glGetUniformLocation(sceneProgram,"vp"),1,GL_FALSE,vp.v);glBindVertexArray(mesh.vao);glDrawArrays(GL_TRIANGLES,0,mesh.count);
 };
 while(!glfwWindowShouldClose(window)){
  double now=glfwGetTime();float dt=float(std::min(now-previous,.05));previous=now;glfwPollEvents();
  if(glfwGetKey(window,GLFW_KEY_ESCAPE)==GLFW_PRESS){captured=false;glfwSetInputMode(window,GLFW_CURSOR,GLFW_CURSOR_NORMAL);}
  if(glfwGetKey(window,GLFW_KEY_R)==GLFW_PRESS){eye={-.05f,-1.35f,1.6f};yaw=1.32f;pitch=-.24f;}
  Vec3 dir=forward(),flat=norm(Vec3{dir.x,dir.y,0}),right=norm(cross(flat,{0,0,1})),movement{};
  if(glfwGetKey(window,GLFW_KEY_W)==GLFW_PRESS)movement=movement+flat;
  if(glfwGetKey(window,GLFW_KEY_S)==GLFW_PRESS)movement=movement-flat;
  if(glfwGetKey(window,GLFW_KEY_D)==GLFW_PRESS)movement=movement+right;
  if(glfwGetKey(window,GLFW_KEY_A)==GLFW_PRESS)movement=movement-right;
  if(smoke){dt=1.f/60;movement=flat;if(frames>=180)yaw+=dt*.8f;if(frames==120)glfwSetWindowSize(window,640,480);if(frames==180)glfwSetWindowSize(window,width,height);}
  float speed=glfwGetKey(window,GLFW_KEY_LEFT_SHIFT)==GLFW_PRESS?3.0f:1.6f;
  eye=eye+norm(movement)*(speed*dt);eye.x=std::clamp(eye.x,-2.15f,2.02f);eye.y=std::clamp(eye.y,-2.45f,2.36f);
  Vec3 hinge{-1.82f,2.6f,1.6f},doorAxis{.22495f,-.97437f,0};
  Vec3 onDoor=hinge+doorAxis*std::clamp(dot(eye-hinge,doorAxis),0.f,1.46f),fromDoor=eye-onDoor;
  float doorDistance=std::sqrt(dot(fromDoor,fromDoor));
  if(doorDistance<.22f)eye=onDoor+(doorDistance>1e-5f?fromDoor*(1/doorDistance):Vec3{.97437f,.22495f,0})*.22f;
  int w,h;glfwGetFramebufferSize(window,&w,&h);if(w==0||h==0){glfwWaitEventsTimeout(.05);continue;}
  reflect.resize(std::max(1,w/2),std::max(1,h/2));glDisable(GL_FRAMEBUFFER_SRGB);glBindFramebuffer(GL_FRAMEBUFFER,reflect.fbo);Vec3 rEye=eye,rDir=forward();rEye.z=-rEye.z+.032f;rDir.z=-rDir.z;draw(rEye,rDir,true,reflect.width,reflect.height);
  glBindFramebuffer(GL_FRAMEBUFFER,0);glEnable(GL_FRAMEBUFFER_SRGB);draw(eye,forward(),false,w,h);frames++;
  if(frameLimit&&frames>=frameLimit){if(!shot.empty())screenshot(shot,w,h);break;}
  glfwSwapBuffers(window);
  if(now-lastTitle>1){std::ostringstream t;t<<"DREAM | "<<int(frames/(now-begin))<<" FPS | WASD mover - clic mirar - Esc liberar";glfwSetWindowTitle(window,t.str().c_str());lastTitle=now;}
 }
 GLenum error=glGetError();std::cout<<"frames="<<frames<<" elapsed="<<glfwGetTime()-begin<<" vertices="<<mesh.count<<" gl_error="<<error<<" camera="<<eye.x<<","<<eye.y<<","<<eye.z<<" yaw="<<yaw<<"\n";glfwDestroyWindow(window);glfwTerminate();return error?2:0;
 }catch(const std::exception& e){std::cerr<<"DREAM: "<<e.what()<<"\n";glfwTerminate();return 1;}}
