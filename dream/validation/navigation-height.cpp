#include "../runtime/src/scene.hpp"
#include <chrono>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <limits>
#include <random>

static int checks=0;
static void require(bool pass,const char* message) {
    ++checks;if(!pass)throw std::runtime_error(message);
}
static bool same(Vec3 a,Vec3 b) {
    return std::memcmp(&a.x,&b.x,sizeof(float))==0&&std::memcmp(&a.y,&b.y,sizeof(float))==0&&std::memcmp(&a.z,&b.z,sizeof(float))==0;
}
struct Fixtures {
    std::filesystem::path directory;
    std::vector<std::filesystem::path> files;
    Fixtures() {
        directory=std::filesystem::temp_directory_path()/
            ("dream-navigation-height-"+std::to_string(std::chrono::high_resolution_clock::now().time_since_epoch().count()));
        if(!std::filesystem::create_directory(directory))throw std::runtime_error("Cannot create isolated fixture directory");
    }
    ~Fixtures() {
        // Only explicitly created files and the empty fixture directory; no
        // recursive cleanup or computed directory tree deletion.
        std::error_code error;
        for(const auto& file:files)std::filesystem::remove(file,error);
        std::filesystem::remove(directory,error);
    }
    std::filesystem::path write(const std::string& source) {
        auto file=directory/(std::to_string(files.size())+".scene");
        std::ofstream stream(file);stream<<source;stream.close();
        if(!stream)throw std::runtime_error("Cannot write fixture");
        files.push_back(file);return file;
    }
};

// Frozen pre-height controller. This oracle deliberately retains float
// operation order to check bit-for-bit compatibility of existing scenes.
static Vec3 legacyConstrain(const SceneSettings& s,Vec3 p) {
    for(int pass=0;pass<3;pass++) {
        for(const auto& d:s.obstacles) {
            Vec3 away{p.x-d.x,p.y-d.y,0};float distance=std::sqrt(dot(away,away));
            if(distance<d.r) { away=distance>1e-5f?away*(1/distance):Vec3{1,0,0};p.x=d.x+away.x*d.r;p.y=d.y+away.y*d.r; }
        }
        for(const auto& c:s.capsules) {
            Vec3 a{c.a.x,c.a.y,p.z},delta=c.b-c.a;
            float length=dot(delta,delta),t=length>0?std::clamp(dot(p-a,delta)/length,0.f,1.f):0;
            Vec3 on=a+delta*t,away=p-on;float distance=std::sqrt(dot(away,away));
            if(distance<c.radius)p=on+(distance>1e-5f?away*(1/distance):norm(Vec3{-delta.y,delta.x,0}))*c.radius;
        }
        p.x=std::clamp(p.x,s.xMin,s.xMax);p.y=std::clamp(p.y,s.yMin,s.yMax);
        Vec3 radial{p.x-s.boundary.x,p.y-s.boundary.y,0};float distance=std::sqrt(dot(radial,radial));
        if(s.boundary.r>0&&distance>s.boundary.r) { radial=radial*(s.boundary.r/distance);p.x=s.boundary.x+radial.x;p.y=s.boundary.y+radial.y; }
    }
    return p;
}
static Vec3 legacyMove(const SceneSettings& s,Vec3 start,Vec3 movement) {
    int steps=std::max(1,int(std::ceil(std::sqrt(dot(movement,movement))/.08f)));
    for(int i=0;i<steps;i++)start=legacyConstrain(s,start+movement*(1.f/steps));
    return start;
}
static void legacyRegression(const SceneSettings& s) {
    require(s.surfaces.empty(),"Legacy fixture unexpectedly has surfaces");
    std::mt19937 rng(42071);std::uniform_real_distribution<float> displacement(-4,4);
    Vec3 current=s.spawn;
    for(int i=0;i<160;i++) {
        Vec3 movement{displacement(rng),displacement(rng),displacement(rng)*.05f};
        Vec3 old=legacyMove(s,current,movement),actual=s.move(current,movement);
        require(same(old,actual),"Legacy move differs at float-bit level");
        require(same(legacyConstrain(s,current),s.constrain(current)),"Legacy constrain differs at float-bit level");
        current=actual;
    }
}

int main(int argc,char** argv) {
    try {
        require(argc==2,"Usage: navigation-height <assets-directory>");
        Fixtures fixture;
        std::ostringstream source;source<<std::fixed<<std::setprecision(6);
        source<<"camera 0 -1 1.55 1.57 0\neye_height 1.55\nstep_limits .18 .18\n"
              <<"bounds -.72 .72 -5.2 5.0\nsurface -.93 -5.2 .93 0 0\n";
        for(int i=0;i<12;i++)source<<"surface -.93 "<<i*.3<<" .93 "<<(i+1)*.3<<' '<<(i+1)*.16<<'\n';
        source<<"surface -.93 3.6 .93 5.2 1.92\n";
        SceneSettings stair(fixture.write(source.str()));
        require(stair.surfaces.size()==14,"Expected fourteen staircase support rectangles");
        require(stair.farClip==200,"Default far clip changed");
        Vec3 p=stair.spawn;int upward=0,downward=0;
        for(int i=0;i<145;i++) {
            Vec3 before=p;p=stair.move(p,{0,.04f,0});
            require(stair.hasSupport(p),"No support during ascent");
            require(p.z-before.z>=-1e-5f&&p.z-before.z<=.1801f,"Ascent exceeded step limit");
            if(p.z-before.z>.01f)upward++;
        }
        require(std::abs(p.y-4.8f)<.002f&&std::abs(p.z-3.47f)<.0001f,"Did not reach upper landing at +1.92 m");
        require(upward==12,"Did not traverse exactly twelve upward risers");
        for(int i=0;i<145;i++) {
            Vec3 before=p;p=stair.move(p,{0,-.04f,0});
            require(stair.hasSupport(p),"No support during descent");
            require(p.z-before.z<=1e-5f&&before.z-p.z<=.1801f,"Descent exceeded step limit");
            if(before.z-p.z>.01f)downward++;
        }
        require(std::abs(p.z-1.55f)<.0001f&&downward==12,"Did not descend all twelve risers");
        p=stair.move(stair.spawn,{0,5.8f,99});
        require(std::abs(p.y-4.8f)<.002f&&std::abs(p.z-3.47f)<.0001f,"Long move skipped support or allowed flight");
        p=stair.move(p,{0,100,0});
        require(p.y<=5.0001f&&std::abs(p.z-3.47f)<.0001f,"Walked beyond landing/navigation bound");

        auto supported=[&](const std::string& surfaces,float initialZ=1.55f) {
            return SceneSettings(fixture.write("camera -1 0 "+std::to_string(initialZ)+" 0 0\neye_height 1.55\nstep_limits .18 .18\n"+surfaces));
        };
        auto high=supported("surface -2 -1 0 1 0\nsurface 0 -1 2 1 .30\n");
        p=high.move(high.spawn,{2,0,0});
        require(p.x<=.0001f&&p.z==high.spawn.z,"Climbed a step above maxStepUp");
        auto drop=supported("surface -2 -1 0 1 .30\nsurface 0 -1 2 1 0\n",1.85f);
        p=drop.move(drop.spawn,{2,0,0});
        require(p.x<=.0001f&&std::abs(p.z-1.85f)<.0001f,"Fell farther than maxStepDown");
        auto gap=supported("surface -2 -1 0 1 0\nsurface .002 -1 2 1 0\n");
        p=gap.move(gap.spawn,{2,0,0});
        require(p.x<=.0001f,"Skipped a 2 mm unsupported gap inside an 8 cm substep");
        Vec3 unsupported{.001f,0,1.55f};
        require(same(gap.move(unsupported,{.4f,0,0}),unsupported),"Teleported from a gap onto a surface");
        auto stacked=supported("surface -2 -1 2 1 0\nsurface -1 -1 3 1 .16\n");
        p=stacked.move({0,0,1.55f},{.5f,0,50});
        require(std::abs(p.z-1.55f)<.0001f,"Snapped to overlapping upper platform");
        p=stacked.move({0,0,1.71f},{.5f,0,-50});
        require(std::abs(p.z-1.71f)<.0001f,"Snapped down from overlapping upper platform");
        p=stacked.move({1.8f,0,1.55f},{.5f,0,0});
        require(p.x<=2.0001f&&std::abs(p.z-1.55f)<.0001f,"Changed levels through overlapping footprints");
        auto flat=supported("surface -20 -20 20 20 0\n");
        flat.capsules={{{.013f,-2,0},{.013f,2,0},.004f}};
        p=flat.move({-2,0,1.55f},{4,0,0});
        require(p.x<.01f&&std::abs(p.z-1.55f)<.0001f,"Long movement skipped a thin capsule");
        flat.capsules.clear();flat.obstacles={{.013f,0,.004f}};
        p=flat.move({-2,0,1.55f},{4,0,0});
        require(p.x<.01f,"Long movement skipped a thin disc");
        flat.obstacles.clear();
        p=flat.move({0,0,1.55f},{0,0,4});
        require(std::abs(p.z-1.55f)<.0001f,"Zero XY input changed support level");

        SceneSettings ramp(fixture.write(
            "camera -1 0 1.35 0 0\neye_height 1.55\nstep_limits .18 .18\n"
            "ramp -10 -10 10 10 0 .2 0\nbounds -10 10 -10 10\n"));
        p=ramp.move(ramp.spawn,{8,0,0});
        require(std::abs(p.x-7)<.002f&&std::abs(p.z-2.95f)<.002f,
                "Did not follow continuous ramp height uphill");
        p=ramp.move(p,{-8,0,0});
        require(std::abs(p.z-ramp.spawn.z)<.002f,
                "Did not follow continuous ramp height downhill");
        p=ramp.move(ramp.spawn,{0,4,0});
        require(std::abs(p.z-ramp.spawn.z)<.002f,
                "Ramp changed height while moving perpendicular to its slope");

        int invalidCases=0;
        for(const std::string invalid:{
                "eye_height 0", "eye_height -1", "step_limits -.1 .2", "step_limits .2 -.1",
                "surface 0 0 0 1 0", "surface 1 0 0 1 0", "surface 0 1 1 0 0", "surface 0 0 1 1 nan",
                "surface 0 0 1 1 0", "camera inf 0 0 0 0", "fov nan", "bounds 0 0 -1 1",
                "ramp -1 -1 1 1 0 nan 0", "ramp -1 -1 1 1 0 1.1 0",
                "disc 0 0 -1", "capsule 0 0 1 1 0", "far_clip .01", "camera 0 0 1 0 0 surprise"}) {
            bool failed=false;
            try { SceneSettings bad(fixture.write(invalid+"\n")); }catch(const std::runtime_error&) {failed=true;}
            require(failed,"Invalid scene setting was accepted");invalidCases++;
        }
        bool rejected=false;
        try { flat.move(flat.spawn,{std::numeric_limits<float>::infinity(),0,0}); }
        catch(const std::runtime_error&) {rejected=true;}
        require(rejected,"Infinite movement accepted");
        rejected=false;
        try { flat.move(flat.spawn,{1e30f,0,0}); }catch(const std::runtime_error&) {rejected=true;}
        require(rejected,"Movement overflow accepted");
        SceneSettings far(fixture.write("far_clip 1000 # kitchen\n"));
        require(far.farClip==1000,"far_clip parsing regressed");

        std::filesystem::path assets=argv[1];
        legacyRegression(SceneSettings(assets/"pastel_room.scene"));
        legacyRegression(SceneSettings(assets/"atrium.scene"));
        bool actualKitchen=std::filesystem::exists(assets/"kitchen_meadow.scene");
        auto kitchenFile=actualKitchen?assets/"kitchen_meadow.scene":fixture.write(
            "camera -.35 -2.8 1.45 1.53 -.12\nfov .65\nfar_clip 1000\nbounds -1.65 1.85 -3.4 15\n"
            "capsule -1.03 -1.5 -1.03 1.63 .2\ncapsule -.3 1.8 -.3 2.3 .18\ndisc 1.2 5 .3\n");
        if(actualKitchen) {
            SceneSettings kitchen(kitchenFile);
            require(kitchen.surfaces.size()==2&&kitchen.hasSupport(kitchen.spawn),
                    "Current kitchen support surfaces are missing or do not support spawn");
        } else legacyRegression(SceneSettings(kitchenFile));
        SceneSettings tree(assets/"v51_monumental_tree.scene");
        require(tree.environment==6&&tree.surfaces.size()==1&&tree.hasSupport(tree.spawn),
                "Monumental tree scene is missing its supported analytic ramp");
        Vec3 treePosition=tree.spawn;
        for(int i=0;i<80;i++) {
            treePosition=tree.move(treePosition,{-.125f,0,0});
            require(tree.hasSupport(treePosition),"Lost support while walking uphill on the tree lawn");
            require(std::abs(treePosition.z-(tree.eyeHeight-.30f*treePosition.x))<.0001f,
                    "Tree lawn camera height diverged from its slope");
        }
        for(int i=0;i<80;i++) {
            treePosition=tree.move(treePosition,{.125f,0,0});
            require(tree.hasSupport(treePosition),"Lost support while walking downhill on the tree lawn");
        }
        require(std::abs(treePosition.x-tree.spawn.x)<.0001f&&
                std::abs(treePosition.z-tree.spawn.z)<.0001f,
                "Tree lawn round trip did not return to the original elevation");
        std::cout<<"{\"status\":\"PASS\",\"checks\":"<<checks
                 <<",\"upward_risers\":"<<upward<<",\"downward_risers\":"<<downward
                 <<",\"height_gain_m\":1.92,\"support_rectangles\":14,\"invalid_input_cases\":"<<invalidCases
                 <<",\"legacy_regression_scenes\":"<<(actualKitchen?2:3)<<",\"legacy_movement_sequences\":"<<(actualKitchen?320:480)<<",\"legacy_bit_exact\":true"
                 <<",\"kitchen_source\":\""<<(actualKitchen?"current_asset":"explicit_no_surface_fixture")
                 <<"\",\"tree_ramp_round_trip_steps\":160,\"tree_ramp_height_m\":3.0}\n";
    }catch(const std::exception& error) {
        std::cerr<<"navigation-height=FAIL: "<<error.what()<<'\n';return 1;
    }
}
