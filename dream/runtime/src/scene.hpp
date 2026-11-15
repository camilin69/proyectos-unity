#pragma once
#include "math.hpp"
#include <filesystem>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <algorithm>
#include <stdexcept>
#include <utility>

struct Disc { float x,y,r; };
struct Capsule { Vec3 a,b;float radius; };
struct SupportSurface {
    float xMin,yMin,xMax,yMax,z,gx=0,gy=0;
    float heightAt(double x,double y)const { return z+gx*static_cast<float>(x)+gy*static_cast<float>(y); }
};
struct LocalLight { Vec3 position{},radiance{};float radius=0;int receiver=0; };
struct SceneSettings {
    Vec3 spawn{};
    float yaw=0,pitch=0,roll=0,tanHalfFov=.9f,reflectionHeight=.016f,exposure=0,farClip=200,cameraShiftNdc=0;
    int environment=0;
    float xMin=-100,xMax=100,yMin=-100,yMax=100;
    Disc boundary{0,0,0};
    std::vector<Disc> obstacles;
    std::vector<Capsule> capsules;
    std::vector<SupportSurface> surfaces;
    std::vector<LocalLight> lights;
    float eyeHeight=1.6f,maxStepUp=.18f,maxStepDown=.18f;

    explicit SceneSettings(const std::filesystem::path& path) {
        std::ifstream file(path);
        if(!file)throw std::runtime_error("Cannot read scene settings: "+path.string());
        std::string line;
        while(std::getline(file,line)) {
            std::istringstream in(line);std::string key;
            if(!(in>>key)||key[0]=='#')continue;
            if(key=="camera")in>>spawn.x>>spawn.y>>spawn.z>>yaw>>pitch;
            else if(key=="camera_roll")in>>roll;
            else if(key=="camera_shift_y")in>>cameraShiftNdc;
            else if(key=="light") { LocalLight l{};in>>l.position.x>>l.position.y>>l.position.z>>l.radiance.x>>l.radiance.y>>l.radiance.z>>l.radius>>l.receiver;lights.push_back(l); }
            else if(key=="fov")in>>tanHalfFov;
            else if(key=="far_clip")in>>farClip;
            else if(key=="reflection")in>>reflectionHeight;
            else if(key=="environment")in>>environment;
            else if(key=="exposure")in>>exposure;
            else if(key=="eye_height")in>>eyeHeight;
            else if(key=="step_limits")in>>maxStepUp>>maxStepDown;
            else if(key=="surface") { SupportSurface s{};in>>s.xMin>>s.yMin>>s.xMax>>s.yMax>>s.z;surfaces.push_back(s); }
            else if(key=="ramp") { SupportSurface s{};in>>s.xMin>>s.yMin>>s.xMax>>s.yMax>>s.z>>s.gx>>s.gy;surfaces.push_back(s); }
            else if(key=="bounds")in>>xMin>>xMax>>yMin>>yMax;
            else if(key=="boundary")in>>boundary.x>>boundary.y>>boundary.r;
            else if(key=="disc") { Disc d{};in>>d.x>>d.y>>d.r;obstacles.push_back(d); }
            else if(key=="capsule") { Capsule c{};in>>c.a.x>>c.a.y>>c.b.x>>c.b.y>>c.radius;capsules.push_back(c); }
            else throw std::runtime_error("Unknown scene setting: "+key);
            if(!in)throw std::runtime_error("Malformed scene setting: "+line);
            std::string extra;
            if(in>>extra&&extra[0]!='#')throw std::runtime_error("Unexpected scene setting data: "+line);
        }
        for(float value:{spawn.x,spawn.y,spawn.z,yaw,pitch,roll,tanHalfFov,reflectionHeight,cameraShiftNdc,
                         exposure,farClip,xMin,xMax,yMin,yMax,boundary.x,boundary.y,
                         boundary.r,eyeHeight,maxStepUp,maxStepDown})
            if(!std::isfinite(value))throw std::runtime_error("Scene values must be finite");
        if(tanHalfFov<=0||std::abs(cameraShiftNdc)>2||xMin>=xMax||yMin>=yMax||boundary.r<0||environment<0)
            throw std::runtime_error("Invalid scene settings");
        if(!std::isfinite(farClip)||farClip<=.05f)throw std::runtime_error("far_clip must be finite and greater than the near plane (0.05)");
        if(eyeHeight<=0||maxStepUp<0||maxStepDown<0)
            throw std::runtime_error("eye_height must be positive and step_limits nonnegative");
        if(lights.size()>16)throw std::runtime_error("At most sixteen local lights are supported");
        for(const auto& l:lights)
            if(!finite(l.position)||!finite(l.radiance)||!std::isfinite(l.radius)||l.radius<=0||
               l.radiance.x<0||l.radiance.y<0||l.radiance.z<0||l.receiver<0||l.receiver>2)
                throw std::runtime_error("Invalid local light");
        for(const auto& d:obstacles)
            if(!std::isfinite(d.x)||!std::isfinite(d.y)||!std::isfinite(d.r)||d.r<=0)
                throw std::runtime_error("Invalid obstacle disc");
        for(const auto& c:capsules)
            if(!finite(c.a)||!finite(c.b)||!std::isfinite(c.radius)||c.radius<=0)
                throw std::runtime_error("Invalid obstacle capsule");
        for(const auto& s:surfaces)
            if(!std::isfinite(s.xMin)||!std::isfinite(s.yMin)||!std::isfinite(s.xMax)||
               !std::isfinite(s.yMax)||!std::isfinite(s.z)||!std::isfinite(s.gx)||!std::isfinite(s.gy)||
               s.xMin>=s.xMax||s.yMin>=s.yMax||std::hypot(s.gx,s.gy)>1.)
                throw std::runtime_error("Invalid support surface");
        if(!surfaces.empty()) {
            if(!hasSupport(spawn))throw std::runtime_error("Spawn has no support at spawn.z - eye_height");
            Vec3 p=constrain(spawn);
            if(std::hypot(p.x-spawn.x,p.y-spawn.y)>heightEpsilon)
                throw std::runtime_error("Supported spawn is outside bounds or inside an obstacle");
        }
    }
    Vec3 constrain(Vec3 p)const {
        if(!finite(p))throw std::runtime_error("Position must be finite");
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
        if(!finite(start)||!finite(movement)||std::hypot(double(movement.x),double(movement.y),double(movement.z))>80000.)
            throw std::runtime_error("Invalid or excessive movement");
        // Preserve the original arithmetic/XY behavior for all older scenes.
        if(!surfaces.empty())return moveSupported(start,movement);
        // Small substeps prevent a frame hitch from crossing a thin obstacle.
        int steps=std::max(1,int(std::ceil(std::sqrt(dot(movement,movement))/.08f)));
        for(int i=0;i<steps;i++)start=constrain(start+movement*(1.f/steps));
        return start;
    }
    bool hasSupport(Vec3 eye)const {
        if(!finite(eye))return false;
        return !supportsAt(eye.x,eye.y,eye.z-eyeHeight).empty();
    }

private:
    static constexpr float heightEpsilon=1e-4f;
    static bool finite(Vec3 p) { return std::isfinite(p.x)&&std::isfinite(p.y)&&std::isfinite(p.z); }
    static bool contains(const SupportSurface& s,double x,double y) {
        return x>=s.xMin&&x<=s.xMax&&y>=s.yMin&&y<=s.yMax;
    }
    std::vector<size_t> supportsAt(double x,double y,float z)const {
        std::vector<size_t> result;
        for(size_t i=0;i<surfaces.size();i++)
            if(contains(surfaces[i],x,y)&&std::abs(surfaces[i].heightAt(x,y)-z)<=heightEpsilon)result.push_back(i);
        return result;
    }
    static bool adjacent(const SupportSurface& a,const SupportSurface& b,double x,double y) {
        // Different levels may join along a shared edge, never by picking a
        // platform above/below an overlapping footprint. A corner alone is
        // not a height-changing join. Coverage intervals below detect even gaps
        // smaller than a movement substep; this tolerance only handles edges.
        constexpr double e=1e-6;
        double lo=std::max(a.yMin,b.yMin),hi=std::min(a.yMax,b.yMax);
        if(hi-lo>e&&y>=lo&&y<=hi&&
           ((std::abs(a.xMax-b.xMin)<=e&&std::abs(x-a.xMax)<=e)||
            (std::abs(a.xMin-b.xMax)<=e&&std::abs(x-a.xMin)<=e)))return true;
        lo=std::max(a.xMin,b.xMin);hi=std::min(a.xMax,b.xMax);
        return hi-lo>e&&x>=lo&&x<=hi&&
            ((std::abs(a.yMax-b.yMin)<=e&&std::abs(y-a.yMax)<=e)||
             (std::abs(a.yMin-b.yMax)<=e&&std::abs(y-a.yMin)<=e));
    }
    bool supportedSegment(Vec3 start,Vec3 end,float& finalHeight)const {
        float height=start.z-eyeHeight;
        auto active=supportsAt(start.x,start.y,height);
        if(active.empty())return false; // Never snap a pose in a gap onto a floor.
        double dx=double(end.x)-start.x,dy=double(end.y)-start.y;
        std::vector<double> cuts{0.,1.};
        for(const auto& s:surfaces) {
            if(dx!=0)for(float edge:{s.xMin,s.xMax}) { double t=(edge-start.x)/dx;if(t>0&&t<1)cuts.push_back(t); }
            if(dy!=0)for(float edge:{s.yMin,s.yMax}) { double t=(edge-start.y)/dy;if(t>0&&t<1)cuts.push_back(t); }
        }
        std::sort(cuts.begin(),cuts.end());
        cuts.erase(std::unique(cuts.begin(),cuts.end()),cuts.end());
        for(size_t c=1;c<cuts.size();c++) {
            double t=(cuts[c-1]+cuts[c])*.5;
            double x=start.x+dx*t,y=start.y+dy*t;
            double bx=start.x+dx*cuts[c-1],by=start.y+dy*cuts[c-1];
            double ex=start.x+dx*cuts[c],ey=start.y+dy*cuts[c];
            std::vector<size_t> continuing;
            for(size_t i:active)
                if(contains(surfaces[i],x,y)&&std::abs(surfaces[i].heightAt(bx,by)-height)<=heightEpsilon)
                    continuing.push_back(i);
            if(!continuing.empty()) {
                float chosen=surfaces[continuing.front()].heightAt(ex,ey);
                for(size_t i:continuing)
                    if(std::abs(surfaces[i].heightAt(ex,ey)-chosen)>heightEpsilon)return false;
                height=chosen;active=std::move(continuing);continue;
            }
            std::vector<size_t> next;
            for(size_t i=0;i<surfaces.size();i++) {
                const auto& candidate=surfaces[i];float change=candidate.heightAt(bx,by)-height;
                if(!contains(candidate,x,y)||change>maxStepUp+heightEpsilon||change< -maxStepDown-heightEpsilon)continue;
                for(size_t previous:active)if(adjacent(surfaces[previous],candidate,bx,by)) { next.push_back(i);break; }
            }
            if(next.empty())return false;
            float chosen=surfaces[next.front()].heightAt(ex,ey);
            for(size_t i:next)if(std::abs(surfaces[i].heightAt(ex,ey)-chosen)>heightEpsilon)return false;
            height=chosen;active=std::move(next);
        }
        finalHeight=height;
        return true;
    }
    static double pointSegmentDistance2(Vec3 p,Vec3 a,Vec3 b) {
        double dx=double(b.x)-a.x,dy=double(b.y)-a.y,length=dx*dx+dy*dy;
        double t=length>0?std::clamp(((p.x-a.x)*dx+(p.y-a.y)*dy)/length,0.,1.):0;
        double x=p.x-(a.x+t*dx),y=p.y-(a.y+t*dy);return x*x+y*y;
    }
    static double segmentDistance2(Vec3 a,Vec3 b,Vec3 c,Vec3 d) {
        double rx=double(b.x)-a.x,ry=double(b.y)-a.y,sx=double(d.x)-c.x,sy=double(d.y)-c.y;
        double den=rx*sy-ry*sx;
        if(std::abs(den)>1e-15) {
            double qx=double(c.x)-a.x,qy=double(c.y)-a.y;
            double t=(qx*sy-qy*sx)/den,u=(qx*ry-qy*rx)/den;
            if(t>=0&&t<=1&&u>=0&&u<=1)return 0;
        }
        return std::min({pointSegmentDistance2(a,c,d),pointSegmentDistance2(b,c,d),
                         pointSegmentDistance2(c,a,b),pointSegmentDistance2(d,a,b)});
    }
    bool crossesObstacle(Vec3 start,Vec3 end)const {
        // Endpoint projection alone can skip obstacles thinner than 8 cm.
        // The supported path also checks the complete horizontal segment.
        for(const auto& d:obstacles)
            if(pointSegmentDistance2({d.x,d.y,0},start,end)<double(d.r)*d.r*(1.-1e-6))return true;
        for(const auto& c:capsules)
            if(segmentDistance2(start,end,c.a,c.b)<double(c.radius)*c.radius*(1.-1e-6))return true;
        return false;
    }
    Vec3 moveSupported(Vec3 start,Vec3 movement)const {
        if(!hasSupport(start))return start;
        movement.z=0; // Grounded movement cannot request flight or a vertical snap.
        int steps=std::max(1,int(std::ceil(std::hypot(movement.x,movement.y)/.08f)));
        Vec3 delta=movement*(1.f/steps);
        for(int i=0;i<steps;i++) {
            Vec3 candidate=constrain(start+delta);float support=0;
            if(supportedSegment(start,candidate,support)&&!crossesObstacle(start,candidate)) {
                candidate.z=support+eyeHeight;
                start=candidate;
            }
        }
        return start;
    }
};
