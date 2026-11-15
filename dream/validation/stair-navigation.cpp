#include "../runtime/src/scene.hpp"
#include <iomanip>
#include <iostream>

// Real-asset integration test. No synthetic settings, catalog mutation or GL.
namespace {
constexpr float xyTolerance=.008f,heightTolerance=.00015f;
struct Event {std::string name;Vec3 start{},target{},end{};int moves=0;bool passed=false;};
struct Route {std::string name;int up=0,down=0;float maximumStep=0;bool passed=false;};
struct Result {
    int checks=0,positions=0;
    std::vector<std::string> failures;
    std::vector<Event> events;
    std::vector<Route> routes;
    void check(bool good,const std::string& error) {
        checks++;if(!good&&failures.size()<30)failures.push_back(error);
    }
};
float xyDistance(Vec3 a,Vec3 b){return std::hypot(a.x-b.x,a.y-b.y);}
float clearance(Vec3 p,const Capsule& c){
    Vec3 d=c.b-c.a;float length=d.x*d.x+d.y*d.y;
    float t=length>0?std::clamp(((p.x-c.a.x)*d.x+(p.y-c.a.y)*d.y)/length,0.f,1.f):0;
    return std::hypot(p.x-c.a.x-d.x*t,p.y-c.a.y-d.y*t)-c.radius;
}
bool supportedFree(const SceneSettings& s,Vec3 p){
    if(!s.hasSupport(p)||p.x<s.xMin-heightTolerance||p.x>s.xMax+heightTolerance||
       p.y<s.yMin-heightTolerance||p.y>s.yMax+heightTolerance)return false;
    for(const auto& c:s.capsules)if(clearance(p,c)<-heightTolerance)return false;
    for(const auto& d:s.obstacles)if(std::hypot(p.x-d.x,p.y-d.y)<d.r-heightTolerance)return false;
    return true;
}
void inspect(const SceneSettings& s,Vec3 p,const std::string& label,Result& result){
    result.positions++;result.check(supportedFree(s,p),label+": unsupported/outside/penetrating pose");
    result.check(std::isfinite(p.x)&&std::isfinite(p.y)&&std::isfinite(p.z),label+": nonfinite pose");
}
void follow(const SceneSettings& s,Vec3& p,Vec3 target,float stride,const std::string& label,
            Route& route,Result& result){
    Event event{label,p,target,p,0,false};int stalled=0;
    while(xyDistance(p,target)>xyTolerance&&event.moves<2000){
        Vec3 movement{target.x-p.x,target.y-p.y,0};float distance=xyDistance(p,target);
        if(stride>0&&distance>stride)movement=movement*(stride/distance);
        Vec3 next=s.move(p,movement);event.moves++;inspect(s,next,label,result);
        float change=next.z-p.z;route.maximumStep=std::max(route.maximumStep,std::abs(change));
        if(change>.01f)route.up++;
        if(change<-.01f)route.down++;
        result.check(change<=s.maxStepUp+heightTolerance&&-change<=s.maxStepDown+heightTolerance,
                     label+": recorded height change exceeds configured step limit");
        stalled=xyDistance(p,next)<1e-6f?stalled+1:0;p=next;
        if(stalled>=6)break;
    }
    event.end=p;event.passed=xyDistance(p,target)<=xyTolerance&&std::abs(p.z-target.z)<=heightTolerance;
    result.check(event.passed,label+": target XY/eye height not reached");result.events.push_back(event);
}
void roundTrip(const SceneSettings& s,float stride,const std::string& label,Result& result){
    const size_t failureCount=result.failures.size();
    Route route{label,0,0,0,false};Vec3 p=s.spawn;
    inspect(s,p,label+"_spawn",result);
    // Visit the centre of every actual exported tread, then the landing.
    for(size_t i=1;i<s.surfaces.size();i++){
        const auto& surface=s.surfaces[i];
        Vec3 target{0,(surface.yMin+surface.yMax)*.5f,surface.z+s.eyeHeight};
        follow(s,p,target,stride,label+"_up_"+std::to_string(i),route,result);
    }
    result.check(std::abs(p.z-s.spawn.z-1.92f)<heightTolerance,label+": ascent is not +1.92 m");
    for(int i=int(s.surfaces.size())-2;i>=1;i--){
        const auto& surface=s.surfaces[size_t(i)];
        follow(s,p,{0,(surface.yMin+surface.yMax)*.5f,surface.z+s.eyeHeight},stride,
               label+"_down_"+std::to_string(i),route,result);
    }
    follow(s,p,s.spawn,stride,label+"_return_spawn",route,result);
    result.check(route.up==12&&route.down==12,label+": did not traverse twelve risers each way");
    route.passed=result.failures.size()==failureCount;result.routes.push_back(route);
}
void pushLimit(const SceneSettings& s,Vec3 start,Vec3 movement,int axis,float bound,
               float expectedZ,const std::string& label,Result& result){
    Event event{label,start,start+movement,start,1,false};
    result.check(supportedFree(s,start),label+": invalid start");
    Vec3 p=s.move(start,movement);inspect(s,p,label,result);
    const float value=axis==0?p.x:p.y;
    event.end=p;event.passed=std::abs(value-bound)<.001f&&std::abs(p.z-expectedZ)<heightTolerance&&
                            supportedFree(s,p);
    result.check(event.passed,label+": boundary or support height failed");result.events.push_back(event);
}
void quote(const std::string& s){
    std::cout<<'"';for(char c:s){if(c=='"'||c=='\\')std::cout<<'\\';if(c=='\n')std::cout<<"\\n";else std::cout<<c;}std::cout<<'"';
}
void point(Vec3 p){std::cout<<'['<<p.x<<','<<p.y<<','<<p.z<<']';}
void output(const Result& result,size_t surfaces){
    std::cout<<std::setprecision(8)<<"{\"status\":\""<<(result.failures.empty()?"PASS":"FAIL")
      <<"\",\"checks\":"<<result.checks<<",\"position_samples\":"<<result.positions
      <<",\"actual_exported_surfaces\":"<<surfaces<<",\"height_gain_m\":1.92,\"routes\":[";
    for(size_t i=0;i<result.routes.size();i++){
        if(i)std::cout<<',';
        const auto& r=result.routes[i];std::cout<<"{\"name\":";quote(r.name);
        std::cout<<",\"upward_risers\":"<<r.up<<",\"downward_risers\":"<<r.down
          <<",\"maximum_recorded_step_m\":"<<r.maximumStep<<",\"passed\":"<<(r.passed?"true":"false")<<'}';
    }
    std::cout<<"],\"events\":[";
    for(size_t i=0;i<result.events.size();i++){
        if(i)std::cout<<',';
        const auto& e=result.events[i];std::cout<<"{\"name\":";quote(e.name);
        std::cout<<",\"passed\":"<<(e.passed?"true":"false")<<",\"start\":";point(e.start);
        std::cout<<",\"requested_target\":";point(e.target);std::cout<<",\"end\":";point(e.end);
        std::cout<<",\"move_calls\":"<<e.moves<<'}';
    }
    std::cout<<"],\"failures\":[";
    for(size_t i=0;i<result.failures.size();i++){if(i)std::cout<<',';quote(result.failures[i]);}
    std::cout<<"]}\n";
}
}
int main(int argc,char** argv){
    Result result;size_t surfaceCount=0;
    try{
        if(argc!=2)throw std::runtime_error("Usage: stair-navigation <assets-directory>");
        SceneSettings stair(std::filesystem::path(argv[1])/"stair_sky.scene");
        surfaceCount=stair.surfaces.size();
        if(surfaceCount!=14)throw std::runtime_error("Expected fourteen actual exported stair surfaces");
        result.check(stair.environment==3,"Expected staircase environment 3");
        result.check(std::abs(stair.eyeHeight-1.55f)<heightTolerance,"Unexpected eye height");
        result.check(std::abs(stair.surfaces.front().z)<heightTolerance&&
                     std::abs(stair.surfaces.back().z-1.92f)<heightTolerance,"Unexpected approach/landing elevations");
        for(size_t i=1;i<=12;i++){
            const auto& a=stair.surfaces[i-1];const auto& b=stair.surfaces[i];
            result.check(std::abs(b.z-a.z-.16f)<heightTolerance,"Exported riser differs from 0.16 m");
            result.check(std::abs(b.yMin-a.yMax)<1e-6f,"Exported support edges not joined");
        }
        roundTrip(stair,.035f,"35mm",result);
        roundTrip(stair,.075f,"75mm",result);
        roundTrip(stair,0,"single_request_per_tread",result);
        for(size_t index:{size_t(0),size_t(6),size_t(13)}){
            const auto& s=stair.surfaces[index];Vec3 p{0,(s.yMin+s.yMax)*.5f,s.z+stair.eyeHeight};
            pushLimit(stair,p,{-20,0,0},0,stair.xMin,p.z,"left_limit_surface_"+std::to_string(index),result);
            pushLimit(stair,p,{20,0,0},0,stair.xMax,p.z,"right_limit_surface_"+std::to_string(index),result);
        }
        // Full-flight requests also traverse the production 8 cm substeps.
        pushLimit(stair,stair.spawn,{0,40,0},1,stair.yMax,stair.eyeHeight+1.92f,"long_ascent_stops_before_landing_void",result);
        Vec3 top{0,4.8f,stair.eyeHeight+1.92f};
        pushLimit(stair,top,{0,-40,0},1,stair.yMin,stair.eyeHeight,"long_descent_stops_at_approach_bound",result);
        Vec3 vertical=stair.move(stair.spawn,{0,0,100});
        result.check(xyDistance(vertical,stair.spawn)<1e-6f&&std::abs(vertical.z-stair.spawn.z)<heightTolerance,
                     "Vertical input bypassed grounded stair controller");
    }catch(const std::exception& e){result.check(false,e.what());}
    output(result,surfaceCount);return result.failures.empty()?0:1;
}
