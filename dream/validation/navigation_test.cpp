#include "../runtime/src/scene.hpp"
#include <cassert>
#include <iostream>

int main(int argc,char** argv) {
    assert(argc==2);
    std::filesystem::path assets=argv[1];
    SceneSettings room(assets/"pastel_room.scene"),atrium(assets/"atrium.scene");
    // Large simulated frame movement cannot jump through the open door.
    Vec3 start{-1.9f,1.8f,1.6f};
    Vec3 end=room.move(start,{.8f,0,0});
    assert(end.x<-1.4f);
    assert(room.move(room.spawn,{0,30,0}).y<=room.yMax);
    assert(room.move(room.spawn,{30,0,0}).x<=room.xMax);
    // Walk toward the pond from every direction; never enter it or the pots.
    for(int direction=0;direction<360;direction++) {
        float a=direction*3.14159265f/180;
        Vec3 p{-1+9*std::cos(a),4+9*std::sin(a),1.85f};
        for(int step=0;step<180;step++) {
            p=atrium.move(p,norm(Vec3{-1-p.x,4-p.y,0})*.05f);
            assert(std::hypot(p.x+1,p.y-4)>=4.55f-.002f);
            assert(std::hypot(p.x+1,p.y-4)<=10.0f+.002f);
            for(const auto& d:atrium.obstacles)assert(std::hypot(p.x-d.x,p.y-d.y)>=d.r-.002f);
        }
    }
    std::cout<<"navigation=PASS (door, walls, pond, columns, planters; 64800 steps)\n";
}
