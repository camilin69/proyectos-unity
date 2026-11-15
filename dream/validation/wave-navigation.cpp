#include "../runtime/src/scene.hpp"
#include <iostream>
#include <iomanip>

// Exercise the actual exported supports using the production controller.
namespace {
constexpr float tolerance=.0002f;
struct Audit {
    int checks=0,positions=0;
    void require(bool condition,const std::string& message) {
        ++checks;
        if(!condition)throw std::runtime_error(message);
    }
    void inspect(const SceneSettings& scene,Vec3 p) {
        ++positions;
        require(scene.hasSupport(p),"Unsupported pose");
        const auto free=scene.constrain(p);
        require(std::hypot(free.x-p.x,free.y-p.y)<tolerance,"Outside bounds or inside column");
    }
};
bool near(Vec3 a,Vec3 b) { return std::hypot(a.x-b.x,a.y-b.y)<.008f&&std::abs(a.z-b.z)<tolerance; }
void walk(const SceneSettings& scene,Vec3& position,Vec3 target,float stride,
          int& up,int& down,Audit& audit) {
    for(int count=0;count<2500&&!near(position,target);++count) {
        auto delta=target-position;delta.z=0;
        const auto distance=std::hypot(delta.x,delta.y);
        if(distance>stride)delta=delta*(stride/distance);
        const auto next=scene.move(position,delta);
        const auto height=next.z-position.z;
        if(height>.01f)++up;
        if(height<-.01f)++down;
        audit.require(height<=scene.maxStepUp+tolerance&&-height<=scene.maxStepDown+tolerance,"Step limit exceeded");
        audit.inspect(scene,next);position=next;
    }
    audit.require(near(position,target),"Route did not reach target");
}
}
int main(int argc,char** argv) {
    Audit audit;
    try {
        if(argc!=2)throw std::runtime_error("Usage: wave-navigation <assets-directory>");
        const SceneSettings scene(std::filesystem::path(argv[1])/"wave_corridor.scene");
        audit.require(scene.environment==4&&scene.surfaces.size()==17,"Wrong exported wave scene");
        audit.require(scene.capsules.size()==2,"Missing hall column collisions");
        audit.require(std::abs(scene.surfaces.back().z+1.1596664988460463)<tolerance,"Wrong total descent");
        int observedRisers=0;
        for(size_t i=1;i<scene.surfaces.size();++i) {
            const auto& a=scene.surfaces[i-1];const auto& b=scene.surfaces[i];
            audit.require(std::abs(a.yMax-b.yMin)<1e-6,"Disconnected support edges");
            if(std::abs(a.z-b.z)>.01f)++observedRisers;
        }
        audit.require(observedRisers==12,"Expected twelve nonuniform risers");
        for(float stride:{.035f,.075f}) {
            auto p=scene.spawn;int up=0,down=0;
            audit.inspect(scene,p);
            for(size_t i=1;i<scene.surfaces.size();++i) {
                const auto& s=scene.surfaces[i];
                walk(scene,p,{0,(s.yMin+s.yMax)*.5f,s.z+scene.eyeHeight},stride,up,down,audit);
            }
            for(int i=int(scene.surfaces.size())-2;i>=1;--i) {
                const auto& s=scene.surfaces[size_t(i)];
                walk(scene,p,{0,(s.yMin+s.yMax)*.5f,s.z+scene.eyeHeight},stride,up,down,audit);
            }
            walk(scene,p,scene.spawn,stride,up,down,audit);
            audit.require(up==12&&down==12,"Round trip skipped a riser");
        }
        // Large requests must stop at solid boundaries instead of tunnelling.
        const auto far=scene.move(scene.spawn,{0,40,0});audit.inspect(scene,far);
        audit.require(std::abs(far.y-scene.yMax)<tolerance&&std::abs(far.z-(scene.eyeHeight-1.1596665f))<tolerance,"Full descent failed");
        const auto back=scene.move(far,{0,-40,0});audit.inspect(scene,back);
        audit.require(std::abs(back.y-scene.yMin)<tolerance&&std::abs(back.z-scene.eyeHeight)<tolerance,"Full ascent failed");
        for(size_t i:{size_t(0),size_t(7),size_t(14),size_t(16)}) {
            const auto& s=scene.surfaces[i];
            // Hall centreline at y=13.3 crosses the columns; test its walls
            // from y=15, and test the columns independently below.
            const Vec3 start{0,i==16?15.f:(s.yMin+s.yMax)*.5f,s.z+scene.eyeHeight};
            for(float direction:{-1.f,1.f}) {
                const auto edge=scene.move(start,{direction*40,0,0});audit.inspect(scene,edge);
                audit.require(edge.x>=s.xMin-tolerance&&edge.x<=s.xMax+tolerance,"Crossed a side wall");
                audit.require(std::abs(edge.x-(direction<0?s.xMin:s.xMax))<.081f,"Stopped away from side wall");
            }
        }
        for(const auto& column:scene.capsules) {
            const Vec3 start{column.a.x,11.f,scene.eyeHeight+scene.surfaces.back().z};
            const auto stopped=scene.move(start,{0,8,0});audit.inspect(scene,stopped);
            audit.require(stopped.y<=column.a.y-column.radius+tolerance,"Tunnelled through column");
            auto p=start;int up=0,down=0;
            const float side=column.a.x<0?-2.1f:2.1f;
            walk(scene,p,{side,11,p.z},.05f,up,down,audit);
            walk(scene,p,{side,15,p.z},.05f,up,down,audit);
            walk(scene,p,{column.a.x,15,p.z},.05f,up,down,audit);
        }
        audit.require(near(scene.move(scene.spawn,{0,0,100}),scene.spawn),"Vertical input bypassed support");
        std::cout<<"{\"status\":\"PASS\",\"checks\":"<<audit.checks<<",\"position_samples\":"<<audit.positions
                 <<",\"surfaces\":17,\"risers_each_way\":12,\"round_trip_strides_m\":[0.035,0.075],"
                 <<"\"total_descent_m\":1.1596665,\"column_obstacles\":2,\"large_request_m\":40}\n";
    } catch(const std::exception& error) {
        std::cerr<<"Wave navigation FAIL: "<<error.what()<<'\n';return 1;
    }
}
