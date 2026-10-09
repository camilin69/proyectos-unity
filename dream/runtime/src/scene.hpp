#pragma once
#include "math.hpp"
#include <filesystem>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <algorithm>
#include <stdexcept>

struct Disc { float x,y,r; };
struct Capsule { Vec3 a,b;float radius; };
struct SceneSettings {
    Vec3 spawn{};
    float yaw=0,pitch=0,tanHalfFov=.9f,reflectionHeight=.016f;
    int environment=0;
    float xMin=-100,xMax=100,yMin=-100,yMax=100;
    Disc boundary{0,0,0};
    std::vector<Disc> obstacles;
    std::vector<Capsule> capsules;

    explicit SceneSettings(const std::filesystem::path& path) {
        std::ifstream file(path);
        if(!file)throw std::runtime_error("Cannot read scene settings: "+path.string());
        std::string line;
        while(std::getline(file,line)) {
            std::istringstream in(line);std::string key;
            if(!(in>>key)||key[0]=='#')continue;
            if(key=="camera")in>>spawn.x>>spawn.y>>spawn.z>>yaw>>pitch;
            else if(key=="fov")in>>tanHalfFov;
            else if(key=="reflection")in>>reflectionHeight;
            else if(key=="environment")in>>environment;
            else if(key=="bounds")in>>xMin>>xMax>>yMin>>yMax;
            else if(key=="boundary")in>>boundary.x>>boundary.y>>boundary.r;
            else if(key=="disc") { Disc d{};in>>d.x>>d.y>>d.r;obstacles.push_back(d); }
            else if(key=="capsule") { Capsule c{};in>>c.a.x>>c.a.y>>c.b.x>>c.b.y>>c.radius;capsules.push_back(c); }
            else throw std::runtime_error("Unknown scene setting: "+key);
            if(!in)throw std::runtime_error("Malformed scene setting: "+line);
        }
        if(tanHalfFov<=0||xMin>=xMax||yMin>=yMax)throw std::runtime_error("Invalid scene settings");
    }
    Vec3 constrain(Vec3 p)const {
        // Repeated projections resolve simultaneous wall / obstacle contacts.
        for(int pass=0;pass<3;pass++) {
            for(const auto& d:obstacles) {
                Vec3 away{p.x-d.x,p.y-d.y,0};float distance=std::sqrt(dot(away,away));
                if(distance<d.r) { away=distance>1e-5f?away*(1/distance):Vec3{1,0,0};p.x=d.x+away.x*d.r;p.y=d.y+away.y*d.r; }
            }
            for(const auto& c:capsules) {
                Vec3 a{c.a.x,c.a.y,p.z},delta=c.b-c.a;
                float length=dot(delta,delta),t=length>0?std::clamp(dot(p-a,delta)/length,0.f,1.f):0;
                Vec3 on=a+delta*t,away=p-on;float distance=std::sqrt(dot(away,away));
                if(distance<c.radius)p=on+(distance>1e-5f?away*(1/distance):norm(Vec3{-delta.y,delta.x,0}))*c.radius;
            }
            p.x=std::clamp(p.x,xMin,xMax);p.y=std::clamp(p.y,yMin,yMax);
            Vec3 radial{p.x-boundary.x,p.y-boundary.y,0};float distance=std::sqrt(dot(radial,radial));
            if(boundary.r>0&&distance>boundary.r) { radial=radial*(boundary.r/distance);p.x=boundary.x+radial.x;p.y=boundary.y+radial.y; }
        }
        return p;
    }
    Vec3 move(Vec3 start,Vec3 movement)const {
        // Small substeps prevent a frame hitch from crossing a thin obstacle.
        int steps=std::max(1,int(std::ceil(std::sqrt(dot(movement,movement))/.08f)));
        for(int i=0;i<steps;i++)start=constrain(start+movement*(1.f/steps));
        return start;
    }
};
