#include "../runtime/src/scene.hpp"
#include <cassert>
#include <iostream>

static float capsuleDistance(Vec3 p,const Capsule& c) {
    Vec3 d=c.b-c.a;float length=dot(d,d);
    float t=length>0?std::clamp(dot(p-c.a,d)/length,0.f,1.f):0;
    Vec3 delta=p-(c.a+d*t);return std::hypot(delta.x,delta.y);
}
static void freePosition(const SceneSettings& scene,Vec3 p) {
    assert(std::isfinite(p.x)&&std::isfinite(p.y)&&std::isfinite(p.z));
    assert(p.x>=scene.xMin-.003f&&p.x<=scene.xMax+.003f);
    assert(p.y>=scene.yMin-.003f&&p.y<=scene.yMax+.003f);
    if(scene.boundary.r>0)
        assert(std::hypot(p.x-scene.boundary.x,p.y-scene.boundary.y)<=scene.boundary.r+.003f);
    for(const auto& d:scene.obstacles)
        assert(std::hypot(p.x-d.x,p.y-d.y)>=d.r-.003f);
    for(const auto& c:scene.capsules)assert(capsuleDistance(p,c)>=c.radius-.003f);
}

int main(int argc,char** argv) {
    assert(argc==2);
    std::filesystem::path assets=argv[1];
    SceneSettings room(assets/"pastel_room.scene"),atrium(assets/"atrium.scene");
    // Large simulated frame movement cannot jump through the open door.
    Vec3 start{-1.9f,1.8f,1.6f};
    Vec3 end=room.move(start,{.8f,0,0});
    assert(end.x<-1.4f);freePosition(room,end);
    freePosition(room,room.move(room.spawn,{0,30,0}));
    freePosition(room,room.move(room.spawn,{30,0,0}));

    // Isolated capsule cases exercise long moves, rounded ends, diagonal
    // segments and an unobstructed route around an end, even with old assets.
    auto fixture=atrium;fixture.obstacles.clear();fixture.capsules.clear();
    fixture.boundary.r=0;fixture.xMin=fixture.yMin=-20;fixture.xMax=fixture.yMax=20;
    fixture.capsules.push_back({{0,-2,0},{0,2,0},.75f});
    end=fixture.move({-3,0,1.85f},{6,0,0});
    assert(end.x<=-.749f&&std::abs(end.z-1.85f)<.0001f);freePosition(fixture,end);
    end=fixture.move({0,4,1.85f},{0,-5,0});
    assert(end.y>=2.749f);freePosition(fixture,end);
    end=fixture.move({-3,-3,1.85f},{6,0,0});
    assert(std::abs(end.x-3)<.001f&&std::abs(end.y+3)<.001f);freePosition(fixture,end);
    fixture.capsules={{{-2,-2,0},{2,2,0},.5f}};
    end=fixture.move({-3,3,1.85f},{6,-6,0});
    assert((end.y-end.x)/std::sqrt(2.f)>=.499f);freePosition(fixture,end);

    // Walk toward the pond from every direction. Start constrained because
    // the new canal reaches some positions on the old 9 m starting circle.
    int movementChecks=0;
    for(int direction=0;direction<360;direction++) {
        float a=direction*3.14159265f/180;
        Vec3 p=atrium.constrain({-1+9*std::cos(a),4+9*std::sin(a),1.85f});
        freePosition(atrium,p);
        for(int step=0;step<180;step++) {
            p=atrium.move(p,norm(Vec3{-1-p.x,4-p.y,0})*.05f);
            freePosition(atrium,p);movementChecks++;
        }
    }
    // Attack each exported capsule from both sides, including overlapping
    // capsule joins. This checks the actual canal settings after re-export.
    for(const auto& c:atrium.capsules) {
        Vec3 middle=(c.a+c.b)*.5f;middle.z=atrium.spawn.z;
        Vec3 d=c.b-c.a,normal=norm(Vec3{-d.y,d.x,0});
        for(int side:{-1,1}) {
            Vec3 p=atrium.constrain(middle+normal*(side*(c.radius+.3f)));
            freePosition(atrium,p);
            for(int step=0;step<60;step++) {
                p=atrium.move(p,norm(middle-p)*.05f);
                freePosition(atrium,p);movementChecks++;
            }
        }
    }
    // The canal must not close the outer circulation: complete an entire
    // loop in each direction, reaching every target rather than merely
    // stopping without penetration.
    float startAngle=std::atan2(atrium.spawn.y-4,atrium.spawn.x+1);
    for(int direction:{-1,1}) {
        Vec3 p{-1+9.65f*std::cos(startAngle),4+9.65f*std::sin(startAngle),atrium.spawn.z};
        freePosition(atrium,p);
        for(int step=1;step<=180;step++) {
            float a=startAngle+direction*step*6.2831853f/180;
            Vec3 target{-1+9.65f*std::cos(a),4+9.65f*std::sin(a),p.z};
            p=atrium.move(p,target-p);freePosition(atrium,p);
            assert(std::hypot(p.x-target.x,p.y-target.y)<.015f);movementChecks++;
        }
    }
    std::cout<<"navigation=PASS checks="<<movementChecks
             <<" exported_canal_capsules="<<atrium.capsules.size()
             <<" (door, walls, pond, obstacles, capsule fixtures, complete outer routes)\n";
    if(atrium.capsules.empty())
        std::cout<<"canal_export=NOT_VERIFIED (current atrium asset predates the canal; re-export and rerun)\n";
}
