#include "render_support.hpp"

int main(int argc,char** argv) {
 try {
    fs::path root=fs::absolute(fs::path(argv[0])).parent_path().parent_path().parent_path(),shot;
    std::string sceneName="pastel_room";
    int frameLimit=0,width=960,height=720,debugShading=0;
    bool hidden=false,smoke=false,cycle=false;
    float fixedTime=-1;
    for(int i=1;i<argc;i++) {
        std::string a=argv[i];
        if(a=="--root"&&i+1<argc)root=argv[++i];
        else if(a=="--scene"&&i+1<argc)sceneName=argv[++i];
        else if(a=="--capture"&&i+1<argc)shot=argv[++i];
        else if(a=="--frames"&&i+1<argc)frameLimit=std::stoi(argv[++i]);
        else if(a=="--width"&&i+1<argc)width=std::stoi(argv[++i]);
        else if(a=="--height"&&i+1<argc)height=std::stoi(argv[++i]);
        else if(a=="--time"&&i+1<argc)fixedTime=std::stof(argv[++i]);
        else if(a=="--debug-shading"&&i+1<argc)debugShading=std::stoi(argv[++i]);
        else if(a=="--hidden")hidden=true;
        else if(a=="--smoke")smoke=true;
        else if(a=="--cycle")cycle=true;
        else throw std::runtime_error("Unknown/incomplete argument: "+a);
    }
    if(width<64||height<64||width>8192||height>8192||frameLimit<0)throw std::runtime_error("Invalid dimensions/frame count");
    if(debugShading<0||debugShading>3)throw std::runtime_error("Debug shading must be 0=lit, 1=albedo, 2=normals or 3=AO");
    if(!shot.empty()&&frameLimit==0)frameLimit=1;
    if(smoke) {
        float originalYaw=yaw;captured=true;firstMouse=false;cursor(nullptr,10,0);
        if(yaw>=originalYaw)throw std::runtime_error("Mouse orientation test failed");
        yaw=originalYaw;captured=false;firstMouse=true;
        std::cout<<"mouse_orientation=PASS\n";
    }
    glfwSetErrorCallback([](int code,const char* message){std::cerr<<"GLFW "<<code<<": "<<message<<"\n";});
    if(!glfwInit())throw std::runtime_error("GLFW initialization failed");
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR,3);glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR,3);
    glfwWindowHint(GLFW_OPENGL_PROFILE,GLFW_OPENGL_CORE_PROFILE);
    glfwWindowHint(GLFW_SRGB_CAPABLE,GLFW_TRUE);glfwWindowHint(GLFW_VISIBLE,hidden?GLFW_FALSE:GLFW_TRUE);
    GLFWwindow* window=glfwCreateWindow(width,height,"DREAM | 1 habitacion - 2 atrio | WASD - clic mirar - Esc liberar",nullptr,nullptr);
    if(!window)throw std::runtime_error("OpenGL 3.3 context unavailable");
    glfwMakeContextCurrent(window);glfwSwapInterval(hidden?0:1);loadGL();
    glfwSetCursorPosCallback(window,cursor);glfwSetMouseButtonCallback(window,mouse);
    std::cout<<"GPU: "<<glGetString(GL_RENDERER)<<"\nOpenGL: "<<glGetString(GL_VERSION)<<"\n";

    GLuint sceneProgram=program(root/"runtime/shaders","scene"),skyProgram=program(root/"runtime/shaders","sky");
    GLuint presentProgram=program(root/"runtime/shaders","present"),emptyVao;
    glGenVertexArrays(1,&emptyVao);
    GLuint sky=bitmap(root/"assets/textures/cloud_sky.bmp"),plaid=bitmap(root/"assets/textures/curtain_plaid.bmp");
    GLuint ceramicNormal=bitmap(root/"assets/textures/ceramic_normal.bmp",false),ceramicRough=bitmap(root/"assets/textures/ceramic_roughness.bmp",false);
    GLuint leaf=bitmap(root/"assets/textures/leaf_detail.bmp"),globe=bitmap(root/"assets/textures/biosphere.bmp");
    GLuint floorSurface=bitmap(root/"assets/textures/floor_surface_albedo.bmp");
    GLuint floorFlow=bitmap(root/"assets/textures/floor_flow.bmp",false);
    ReflectTarget reflect,opaque,floorReflect,composite;
    std::unique_ptr<Mesh> mesh;
    std::unique_ptr<SceneSettings> settings;
    auto resetCamera=[&](){eye=settings->spawn;yaw=settings->yaw;pitch=settings->pitch;firstMouse=true;};
    auto loadScene=[&](const std::string& name) {
        if(name!="pastel_room"&&name!="atrium")throw std::runtime_error("Unknown scene: "+name);
        auto nextSettings=std::make_unique<SceneSettings>(root/("assets/"+name+".scene"));
        auto nextMesh=std::make_unique<Mesh>(root/("assets/"+name+".dreammesh"));
        settings=std::move(nextSettings);mesh=std::move(nextMesh);sceneName=name;resetCamera();
        glUseProgram(sceneProgram);
        glUniform4fv(glGetUniformLocation(sceneProgram,"baseRough"),mesh->base.size(),mesh->base[0].data());
        glUniform4fv(glGetUniformLocation(sceneProgram,"properties"),mesh->props.size(),mesh->props[0].data());
        integer(sceneProgram,"environment",settings->environment);scalar(sceneProgram,"reflectionHeight",settings->reflectionHeight);
        std::cout<<"scene="<<name<<" vertices="<<mesh->count<<" glass_groups="<<mesh->glass.size()<<" water="<<mesh->water<<"\n";
    };
    loadScene(sceneName);
    const std::string initialScene=sceneName;
    glUseProgram(sceneProgram);
    const char* samplers[]={"sky","plaid","reflection","ceramicNormal","ceramicRough","sceneColor","sceneDepth","leafDetail","biosphere","floorReflection","floorSurface","floorFlow"};
    for(int i=0;i<12;i++)integer(sceneProgram,samplers[i],i);
    glUseProgram(skyProgram);integer(skyProgram,"sky",0);
    glUseProgram(presentProgram);integer(presentProgram,"sceneColor",5);integer(presentProgram,"sceneDepth",6);
    double previous=glfwGetTime(),begin=previous,lastTitle=previous;
    float elapsed=0;int frames=0;GLenum firstError=GL_NO_ERROR;

    auto draw=[&](Vec3 pos,Vec3 dir,bool mirrored,int pass,int w,int h) {
        glViewport(0,0,w,h);
        Vec3 up{0,0,1},right=norm(cross(dir,up)),camUp=cross(right,dir);
        texture(0,sky);texture(1,plaid);texture(2,mirrored?0:reflect.color);
        texture(3,ceramicNormal);texture(4,ceramicRough);
        // Never sample an attachment of the framebuffer being written.
        texture(5,pass==1?opaque.color:0);texture(6,pass==1?opaque.depth:0);texture(7,leaf);texture(8,globe);texture(9,mirrored?0:floorReflect.color);
        texture(10,floorSurface);texture(11,floorFlow);
        glDepthMask(GL_TRUE);
        if(pass==0) {
            glClearColor(.4f,.5f,.6f,1);glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT);
            glDisable(GL_DEPTH_TEST);glDisable(GL_CLIP_DISTANCE0);glUseProgram(skyProgram);
            vec(skyProgram,"forwardDir",dir);vec(skyProgram,"rightDir",right);vec(skyProgram,"upDir",camUp);
            scalar(skyProgram,"aspect",float(w)/h);scalar(skyProgram,"tanHalfFov",settings->tanHalfFov);
            glBindVertexArray(emptyVao);glDrawArrays(GL_TRIANGLES,0,3);
        }
        glEnable(GL_DEPTH_TEST);glEnable(GL_CLIP_DISTANCE0);glUseProgram(sceneProgram);
        vec(sceneProgram,"eye",pos);integer(sceneProgram,"reflected",mirrored?1:0);integer(sceneProgram,"renderPass",pass);
        integer(sceneProgram,"debugShading",debugShading);
        scalar(sceneProgram,"time",fixedTime>=0?fixedTime:elapsed);glUniform2f(glGetUniformLocation(sceneProgram,"resolution"),w,h);
        Mat4 vp=multiply(perspective(2*std::atan(settings->tanHalfFov),float(w)/h,.05f,200),look(pos,dir,up));
        glUniformMatrix4fv(glGetUniformLocation(sceneProgram,"vp"),1,GL_FALSE,vp.v);glBindVertexArray(mesh->vao);
        if(pass==2) {
            auto groups=mesh->glass;
            std::sort(groups.begin(),groups.end(),[&](const auto& a,const auto& b){return dot(a.center-pos,a.center-pos)>dot(b.center-pos,b.center-pos);});
            glEnable(GL_BLEND);glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);glDepthMask(GL_FALSE);
            for(const auto& group:groups)glDrawArrays(GL_TRIANGLES,group.first,group.count);
            glDepthMask(GL_TRUE);glDisable(GL_BLEND);
        } else glDrawArrays(GL_TRIANGLES,0,mesh->count);
    };

    while(!glfwWindowShouldClose(window)) {
        double now=glfwGetTime();float dt=float(std::min(now-previous,.05));previous=now;glfwPollEvents();
        if(glfwGetKey(window,GLFW_KEY_ESCAPE)==GLFW_PRESS){captured=false;glfwSetInputMode(window,GLFW_CURSOR,GLFW_CURSOR_NORMAL);}
        if(glfwGetKey(window,GLFW_KEY_1)==GLFW_PRESS&&sceneName!="pastel_room")loadScene("pastel_room");
        if(glfwGetKey(window,GLFW_KEY_2)==GLFW_PRESS&&sceneName!="atrium")loadScene("atrium");
        if(glfwGetKey(window,GLFW_KEY_R)==GLFW_PRESS)resetCamera();
        if(cycle&&frames==240)loadScene(initialScene=="atrium"?"pastel_room":"atrium");
        if(cycle&&frames==480)loadScene(initialScene);
        Vec3 dir=forward(),flat=norm(Vec3{dir.x,dir.y,0}),right=norm(cross(flat,{0,0,1})),movement{};
        if(glfwGetKey(window,GLFW_KEY_W)==GLFW_PRESS)movement=movement+flat;
        if(glfwGetKey(window,GLFW_KEY_S)==GLFW_PRESS)movement=movement-flat;
        if(glfwGetKey(window,GLFW_KEY_D)==GLFW_PRESS)movement=movement+right;
        if(glfwGetKey(window,GLFW_KEY_A)==GLFW_PRESS)movement=movement-right;
        if(smoke){dt=1.f/60;movement=flat;if(frames>=180)yaw+=dt*.8f;if(frames==120)glfwSetWindowSize(window,640,480);if(frames==180)glfwSetWindowSize(window,width,height);}
        elapsed+=dt;
        float speed=glfwGetKey(window,GLFW_KEY_LEFT_SHIFT)==GLFW_PRESS?3.f:1.6f;
        eye=settings->move(eye,norm(movement)*(speed*dt));
        int w,h;glfwGetFramebufferSize(window,&w,&h);
        if(w==0||h==0){glfwWaitEventsTimeout(.05);continue;}
        reflect.resize(std::max(1,w/2),std::max(1,h/2));opaque.resize(w,h);composite.resize(w,h);
        if(mesh->water&&mesh->floor) {
            floorReflect.resize(std::max(1,w/2),std::max(1,h/2));
            glDisable(GL_FRAMEBUFFER_SRGB);glBindFramebuffer(GL_FRAMEBUFFER,floorReflect.fbo);
            glUseProgram(sceneProgram);scalar(sceneProgram,"reflectionHeight",.2f);integer(sceneProgram,"reflectionSurface",1);
            Vec3 pos=eye,dir=forward();pos.z=.4f-eye.z;dir.z=-dir.z;
            draw(pos,dir,true,0,floorReflect.width,floorReflect.height);
            draw(pos,dir,true,2,floorReflect.width,floorReflect.height);
        }
        glDisable(GL_FRAMEBUFFER_SRGB);glBindFramebuffer(GL_FRAMEBUFFER,reflect.fbo);
        glUseProgram(sceneProgram);scalar(sceneProgram,"reflectionHeight",settings->reflectionHeight);integer(sceneProgram,"reflectionSurface",mesh->water?4:1);
        Vec3 reflectedEye=eye,reflectedDir=forward();
        reflectedEye.z=2*settings->reflectionHeight-eye.z;reflectedDir.z=-reflectedDir.z;
        draw(reflectedEye,reflectedDir,true,0,reflect.width,reflect.height);
        if(!mesh->glass.empty())draw(reflectedEye,reflectedDir,true,2,reflect.width,reflect.height);
        glBindFramebuffer(GL_FRAMEBUFFER,opaque.fbo);draw(eye,forward(),false,0,w,h);

        glBindFramebuffer(GL_FRAMEBUFFER,composite.fbo);glViewport(0,0,w,h);
        glDisable(GL_CLIP_DISTANCE0);glUseProgram(presentProgram);
        integer(presentProgram,"antialias",0);
        texture(5,opaque.color);texture(6,opaque.depth);glBindVertexArray(emptyVao);
        glDepthFunc(GL_ALWAYS);glDrawArrays(GL_TRIANGLES,0,3);glDepthFunc(GL_LESS);
        if(mesh->water)draw(eye,forward(),false,1,w,h);
        if(!mesh->glass.empty())draw(eye,forward(),false,2,w,h);
        glBindFramebuffer(GL_FRAMEBUFFER,0);glEnable(GL_FRAMEBUFFER_SRGB);
        glDisable(GL_CLIP_DISTANCE0);glUseProgram(presentProgram);integer(presentProgram,"antialias",1);scalar(presentProgram,"exposure",settings->exposure);
        texture(5,composite.color);texture(6,composite.depth);glBindVertexArray(emptyVao);
        glDepthFunc(GL_ALWAYS);glDrawArrays(GL_TRIANGLES,0,3);glDepthFunc(GL_LESS);
        frames++;
        GLenum error=glGetError();if(error!=GL_NO_ERROR&&firstError==GL_NO_ERROR)firstError=error;
        if(frameLimit&&frames>=frameLimit){if(!shot.empty())screenshot(shot,w,h);break;}
        glfwSwapBuffers(window);
        if(now-lastTitle>1) {
            std::ostringstream title;title<<"DREAM - "<<sceneName<<" | "<<int(frames/(now-begin))<<" FPS | 1 habitacion - 2 atrio | WASD - clic mirar - Esc liberar";
            glfwSetWindowTitle(window,title.str().c_str());lastTitle=now;
        }
    }
    std::cout<<"frames="<<frames<<" elapsed="<<glfwGetTime()-begin<<" vertices="<<mesh->count<<" gl_error="<<firstError<<" camera="<<eye.x<<","<<eye.y<<","<<eye.z<<" yaw="<<yaw<<"\n";
    mesh.reset();glfwDestroyWindow(window);glfwTerminate();return firstError?2:0;
 }catch(const std::exception& e){std::cerr<<"DREAM: "<<e.what()<<"\n";glfwTerminate();return 1;}
}
