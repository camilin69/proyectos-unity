#include "../runtime/src/scene.hpp"
#include <iomanip>
#include <iostream>
#include <limits>

// CPU integration test against the real exported kitchen settings. It never
// modifies the scene or replaces its colliders with synthetic test geometry.
namespace {
constexpr float positionTolerance=.012f;
constexpr float heightTolerance=.0001f;
constexpr float contactTolerance=.0002f;
struct Event {
    std::string name;
    Vec3 start{},target{},end{};
    int moves=0;
    bool passed=false;
};
struct Results {
    int checks=0,positionSamples=0;
    float minClearance=std::numeric_limits<float>::max();
    float maxHeightError=0;
    std::vector<std::string> failures;
    std::vector<Event> events;
    void check(bool okay,const std::string& message) {
        checks++;
        if(!okay&&failures.size()<40)failures.push_back(message);
    }
};
float distance(Vec3 a,Vec3 b) { return std::hypot(a.x-b.x,a.y-b.y); }
float capsuleDistance(Vec3 p,const Capsule& c) {
    const float dx=c.b.x-c.a.x,dy=c.b.y-c.a.y;
    const float length=dx*dx+dy*dy;
    const float t=length>0?std::clamp(((p.x-c.a.x)*dx+(p.y-c.a.y)*dy)/length,0.f,1.f):0;
    return std::hypot(p.x-c.a.x-dx*t,p.y-c.a.y-dy*t);
}
bool validPosition(const SceneSettings& scene,Vec3 p) {
    if(!std::isfinite(p.x)||!std::isfinite(p.y)||!std::isfinite(p.z)||
       p.x<scene.xMin-contactTolerance||p.x>scene.xMax+contactTolerance||
       p.y<scene.yMin-contactTolerance||p.y>scene.yMax+contactTolerance||
       !scene.hasSupport(p))return false;
    for(const auto& c:scene.capsules)
        if(capsuleDistance(p,c)<c.radius-contactTolerance)return false;
    for(const auto& d:scene.obstacles)
        if(std::hypot(p.x-d.x,p.y-d.y)<d.r-contactTolerance)return false;
    return true;
}
void inspectPosition(const SceneSettings& scene,Vec3 p,const std::string& label,Results& results) {
    results.positionSamples++;
    results.check(validPosition(scene,p),label+": position is unsupported, out of bounds or penetrating a collider");
    const float error=std::abs(p.z-1.48f);
    results.maxHeightError=std::max(results.maxHeightError,error);
    results.check(error<=heightTolerance,label+": eye height differs from the exported 1.480 m");
    for(const auto& c:scene.capsules)
        results.minClearance=std::min(results.minClearance,capsuleDistance(p,c)-c.radius);
}
void follow(const SceneSettings& scene,Vec3& p,Vec3 target,const std::string& name,
            float stride,Results& results) {
    Event event{name,p,target,p,0,false};
    int stalled=0;
    for(int i=0;i<4000&&distance(p,target)>positionTolerance;i++) {
        Vec3 movement{target.x-p.x,target.y-p.y,0};
        float length=distance(target,p);
        if(stride>0&&length>stride)movement=movement*(stride/length);
        Vec3 next=scene.move(p,movement);
        inspectPosition(scene,next,name,results);
        event.moves++;
        stalled=distance(p,next)<1e-6f?stalled+1:0;
        p=next;
        if(stalled>=6)break;
    }
    event.end=p;
    event.passed=distance(p,target)<=positionTolerance&&std::abs(p.z-target.z)<=heightTolerance;
    results.check(event.passed,name+": waypoint not reached");
    results.events.push_back(event);
}
void route(const SceneSettings& scene,float stride,const std::string& suffix,Results& results) {
    const std::vector<std::pair<std::string,Vec3>> waypoints{
        {"before_entry",{-.27f,-1.85f,1.48f}},
        {"inside_entry",{-.27f,-1.15f,1.48f}},
        {"clear_open_leaf",{-.20f,-.65f,1.48f}},
        {"kitchen_centre",{.40f,0,1.48f}},
        {"before_exterior_aperture",{.40f,1.50f,1.48f}},
        {"across_support_seam",{.40f,1.90f,1.48f}},
        {"meadow",{.40f,3.50f,1.48f}}
    };
    Vec3 p=scene.spawn;
    inspectPosition(scene,p,"spawn_"+suffix,results);
    for(const auto& waypoint:waypoints)
        follow(scene,p,waypoint.second,"out_"+waypoint.first+"_"+suffix,stride,results);
    results.check(p.y>3,"outward route never reached meadow y > 3");
    for(auto it=waypoints.rbegin()+1;it!=waypoints.rend();++it)
        follow(scene,p,it->second,"return_"+it->first+"_"+suffix,stride,results);
    follow(scene,p,scene.spawn,"return_spawn_"+suffix,stride,results);
}
void attackCapsule(const SceneSettings& scene,size_t index,float t,float side,
                   const std::string& name,Results& results) {
    if(index>=scene.capsules.size()) {
        results.check(false,name+": expected exported capsule missing");return;
    }
    const auto& c=scene.capsules[index];
    Vec3 axis=c.b-c.a;
    Vec3 normal=norm(Vec3{-axis.y,axis.x,0})*side;
    Vec3 centre=c.a+axis*t;centre.z=scene.spawn.z;
    Vec3 start=centre+normal*(c.radius+.43f);
    Vec3 target=centre-normal*1.2f;
    Event event{name,start,target,start,0,false};
    results.check(validPosition(scene,start),name+": attack start not in a valid free position");
    if(validPosition(scene,start)) {
        Vec3 p=start;
        // A single long request catches frame-hitch tunnelling, followed by
        // repeated short requests to confirm that contact remains stable.
        p=scene.move(p,target-p);event.moves++;
        inspectPosition(scene,p,name+"_long",results);
        for(int i=0;i<45;i++) {
            p=scene.move(p,normal*-.04f);event.moves++;
            inspectPosition(scene,p,name+"_repeat",results);
        }
        event.end=p;
        const float signedDistance=(p.x-centre.x)*normal.x+(p.y-centre.y)*normal.y;
        event.passed=signedDistance>=c.radius-contactTolerance&&distance(p,target)>.4f&&
                     distance(p,start)>.1f&&validPosition(scene,p);
        results.check(event.passed,name+": crossed collider centreline or failed to make contact");
    }
    results.events.push_back(event);
}
void edge(const SceneSettings& scene,Vec3 start,Vec3 movement,int coordinate,
          float expected,const std::string& name,Results& results) {
    Event event{name,start,start+movement,start,1,false};
    results.check(validPosition(scene,start),name+": edge start not in a valid position");
    Vec3 p=scene.move(start,movement);
    inspectPosition(scene,p,name,results);
    const float coordinateValue=coordinate==0?p.x:p.y;
    event.end=p;
    // Support edges conservatively stop the final substep, at most 8 cm
    // before the boundary; global bounds may clamp exactly onto the edge.
    event.passed=std::abs(coordinateValue-expected)<=.081f&&validPosition(scene,p)&&
                 distance(p,event.target)>.5f;
    results.check(event.passed,name+": did not stop at the expected floor/bounds edge");
    results.events.push_back(event);
}
void quote(const std::string& value) {
    std::cout<<'"';
    for(char c:value) {
        if(c=='"'||c=='\\')std::cout<<'\\';
        if(c=='\n')std::cout<<"\\n";else std::cout<<c;
    }
    std::cout<<'"';
}
void point(Vec3 p) { std::cout<<'['<<p.x<<','<<p.y<<','<<p.z<<']'; }
void output(const Results& results,size_t surfaceCount,size_t capsuleCount) {
    std::cout<<std::setprecision(8)<<"{\"status\":\""<<(results.failures.empty()?"PASS":"FAIL")
        <<"\",\"checks\":"<<results.checks<<",\"position_samples\":"<<results.positionSamples
        <<",\"surface_count\":"<<surfaceCount<<",\"capsule_count\":"<<capsuleCount
        <<",\"max_eye_height_error_m\":"<<results.maxHeightError
        <<",\"minimum_capsule_clearance_m\":"
        <<(results.positionSamples?results.minClearance:0)
        <<",\"waypoint_tolerance_m\":"<<positionTolerance
        <<",\"height_tolerance_m\":"<<heightTolerance
        <<",\"contact_tolerance_m\":"<<contactTolerance<<",\"events\":[";
    for(size_t i=0;i<results.events.size();i++) {
        const auto& event=results.events[i];if(i)std::cout<<',';
        std::cout<<"{\"name\":";quote(event.name);
        std::cout<<",\"passed\":"<<(event.passed?"true":"false")<<",\"start\":";point(event.start);
        std::cout<<",\"requested_target\":";point(event.target);
        std::cout<<",\"end\":";point(event.end);
        std::cout<<",\"move_calls\":"<<event.moves<<'}';
    }
    std::cout<<"],\"failures\":[";
    for(size_t i=0;i<results.failures.size();i++) { if(i)std::cout<<',';quote(results.failures[i]); }
    std::cout<<"]}\n";
}
}
int main(int argc,char** argv) {
    Results results;size_t surfaces=0,capsules=0;
    try {
        if(argc!=2)throw std::runtime_error("Usage: kitchen-navigation <assets-directory>");
        const SceneSettings scene(std::filesystem::path(argv[1])/"kitchen_meadow.scene");
        surfaces=scene.surfaces.size();capsules=scene.capsules.size();
        results.check(surfaces==2,"Expected the real two-surface kitchen export");
        results.check(capsules==10,"Expected ten object-derived kitchen capsules");
        results.check(distance(scene.spawn,{-.35f,-2.8f,1.48f})<.0001f&&
                      std::abs(scene.spawn.z-1.48f)<heightTolerance,"Unexpected kitchen spawn");
        route(scene,.035f,"35mm",results);
        route(scene,.075f,"75mm",results);
        route(scene,0,"single_long_request_per_leg",results);
        attackCapsule(scene,0,.15f,-1,"left_wall",results);
        attackCapsule(scene,1,.50f,1,"right_wall",results);
        attackCapsule(scene,2,.50f,1,"exterior_wall_from_meadow",results);
        attackCapsule(scene,3,.50f,-1,"right_exterior_post",results);
        attackCapsule(scene,4,.50f,-1,"entry_wall_left",results);
        attackCapsule(scene,5,.50f,-1,"entry_wall_right",results);
        attackCapsule(scene,6,.50f,1,"open_door_leaf",results);
        attackCapsule(scene,7,.50f,-1,"cabinet_front",results);
        edge(scene,{-1,-2.45f,1.48f},{-10,0,0},0,-1.65f,"approach_floor_left",results);
        edge(scene,{1,-2.45f,1.48f},{10,0,0},0,1.85f,"approach_floor_right",results);
        edge(scene,scene.spawn,{0,-10,0},1,-3.2f,"approach_back_limit",results);
        edge(scene,{.4f,3.5f,1.48f},{-40,0,0},0,-16,"meadow_left_limit",results);
        edge(scene,{.4f,3.5f,1.48f},{40,0,0},0,16,"meadow_right_limit",results);
        edge(scene,{.4f,3.5f,1.48f},{0,40,0},1,20,"meadow_far_limit",results);
        // A grounded move cannot fly over the furniture or alter eye height.
        Vec3 vertical=scene.move(scene.spawn,{0,0,100});
        results.check(distance(vertical,scene.spawn)<.0001f&&
                      std::abs(vertical.z-scene.spawn.z)<heightTolerance,"Vertical request changed grounded pose");
    } catch(const std::exception& e) { results.check(false,e.what()); }
    output(results,surfaces,capsules);
    return results.failures.empty()?0:1;
}
