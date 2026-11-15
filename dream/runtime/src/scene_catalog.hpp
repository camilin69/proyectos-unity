#pragma once
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

// This catalog is CPU-only: listing and validating scenes never initialize GLFW.
struct SceneProfile {
    inline static const std::array<std::string,9> roles={"sky","plaid","ceramic_normal","ceramic_roughness","leaf","globe","floor_surface","floor_flow","probe"};
    std::string id;
    int environment=-1;
    bool available=false;
    std::array<std::filesystem::path,9> textures{};
};
struct SceneEntry {
    std::string id,alias,profile,label;
    bool available=false,visuallyAccepted=false;
    std::filesystem::path settings,mesh;
};
struct SceneCatalog {
    std::filesystem::path root;
    std::vector<SceneEntry> scenes;
    std::map<std::string,SceneProfile> profiles;

    static bool state(const std::string& text) {
        if(text=="available")return true;
        if(text=="planned")return false;
        throw std::runtime_error("Catalog state must be planned or available: "+text);
    }
    static bool identifier(const std::string& s) {
        return !s.empty()&&s!="-"&&std::all_of(s.begin(),s.end(),[](unsigned char c){return (c>='a'&&c<='z')||(c>='0'&&c<='9')||c=='_'||c=='-'||c=='/';});
    }
    static std::filesystem::path relativePath(const std::string& value) {
        std::filesystem::path p(value);
        if(p.empty()||p.is_absolute()||p.has_root_name())throw std::runtime_error("Catalog path must be relative: "+value);
        for(const auto& part:p)if(part==".."||part==".")throw std::runtime_error("Invalid catalog path: "+value);
        return p;
    }
    explicit SceneCatalog(const std::filesystem::path& base):root(base) {
        std::ifstream file(root/"assets/scene_catalog.cat");
        if(!file)throw std::runtime_error("Cannot read scene catalog: "+(root/"assets/scene_catalog.cat").string());
        std::string line;bool header=false;int lineNumber=0;std::set<std::string> names;
        while(std::getline(file,line)) {
            ++lineNumber;std::istringstream in(line);std::string command,extra;
            if(!(in>>command)||command[0]=='#')continue;
            try {
                if(!header) {
                    int version=0;in>>version;
                    if(command!="DREAM_SCENE_CATALOG"||version!=1)throw std::runtime_error("Unsupported scene catalog header");
                    header=true;
                } else if(command=="profile") {
                    SceneProfile p;std::string availability;in>>p.id>>p.environment>>availability;
                    if(!identifier(p.id)||p.environment<0||p.environment>6)throw std::runtime_error("Unknown profile/environment; supported IDs are 0=room, 1=atrium, 2=kitchen, 3=stair_sky, 4=wave_corridor, 5=ocean_exit, 6=monumental_tree");
                    p.available=state(availability);
                    if(!profiles.emplace(p.id,p).second)throw std::runtime_error("Duplicate profile: "+p.id);
                } else if(command=="texture") {
                    std::string profile,role,path;in>>profile>>role>>path;
                    auto p=profiles.find(profile);auto r=std::find(SceneProfile::roles.begin(),SceneProfile::roles.end(),role);
                    if(p==profiles.end()||r==SceneProfile::roles.end())throw std::runtime_error("Unknown texture profile/role");
                    auto& slot=p->second.textures[size_t(r-SceneProfile::roles.begin())];
                    if(!slot.empty())throw std::runtime_error("Duplicate texture role: "+profile+"/"+role);
                    slot=relativePath(path);
                } else if(command=="scene") {
                    SceneEntry s;std::string availability,visual,settings,mesh;
                    in>>s.id>>s.alias>>availability>>visual>>s.profile>>settings>>mesh>>std::quoted(s.label);
                    if(!identifier(s.id)||!identifier(s.alias)||s.label.empty())throw std::runtime_error("Invalid scene identifier/label");
                    if(visual!="pending"&&visual!="accepted")throw std::runtime_error("Visual state must be pending or accepted");
                    s.available=state(availability);s.visuallyAccepted=visual=="accepted";
                    s.settings=relativePath(settings);s.mesh=relativePath(mesh);
                    if(s.settings.extension()!=".scene"||s.mesh.extension()!=".dreammesh")throw std::runtime_error("Invalid scene asset extensions");
                    if(!names.insert(s.id).second||!names.insert(s.alias).second)throw std::runtime_error("Duplicate scene ID/alias");
                    scenes.push_back(s);
                } else throw std::runtime_error("Unknown catalog command: "+command);
                if(!in||in>>extra)throw std::runtime_error("Malformed catalog record or trailing fields");
            } catch(const std::exception& e) {
                throw std::runtime_error("Scene catalog line "+std::to_string(lineNumber)+": "+e.what());
            }
        }
        if(!header||scenes.empty())throw std::runtime_error("Empty scene catalog");
        for(const auto& pair:profiles)if(pair.second.available)for(size_t i=0;i<SceneProfile::roles.size();i++) {
            const auto& path=pair.second.textures[i];
            if(path.empty()||!std::filesystem::is_regular_file(root/path))throw std::runtime_error("Missing texture for profile "+pair.first+" role "+SceneProfile::roles[i]);
        }
        for(const auto& s:scenes) {
            if(s.profile!="-"&&profiles.find(s.profile)==profiles.end())throw std::runtime_error("Unknown scene profile: "+s.profile);
            if(s.available)requireAvailable(s);
        }
    }
    const SceneEntry& find(const std::string& name)const {
        auto it=std::find_if(scenes.begin(),scenes.end(),[&](const auto& s){return name==s.id||name==s.alias;});
        if(it==scenes.end())throw std::runtime_error("Unknown scene: "+name+". Use --list-scenes.");
        return *it;
    }
    void requireAvailable(const SceneEntry& s)const {
        if(!s.available)throw std::runtime_error("Scene is planned, not available: "+s.id+". Use --list-scenes.");
        auto p=profiles.find(s.profile);
        if(p==profiles.end()||!p->second.available)throw std::runtime_error("Scene profile is not available: "+s.id);
        if(!std::filesystem::is_regular_file(root/s.settings)||!std::filesystem::is_regular_file(root/s.mesh))throw std::runtime_error("Available scene is missing its .scene or .dreammesh: "+s.id);
    }
    const SceneProfile& profile(const SceneEntry& s)const {requireAvailable(s);return profiles.at(s.profile);}
    std::vector<const SceneEntry*> available()const {
        std::vector<const SceneEntry*> out;for(const auto& s:scenes)if(s.available)out.push_back(&s);return out;
    }
    const SceneEntry& adjacent(const std::string& current,int direction)const {
        auto all=available();if(all.empty())throw std::runtime_error("No available scenes");
        auto it=std::find_if(all.begin(),all.end(),[&](const auto* s){return s->id==current||s->alias==current;});
        if(it==all.end())throw std::runtime_error("Current scene is not available");
        auto n=static_cast<int>(all.size()),i=static_cast<int>(it-all.begin());return *all[size_t((i+(direction<0?-1:1)+n)%n)];
    }
    void print(std::ostream& out)const {
        out<<"DREAM scenes: "<<scenes.size()<<" total, "<<available().size()<<" available; visual acceptance is independent.\n";
        for(const auto& s:scenes)out<<s.id<<" | alias="<<s.alias<<" | "<<(s.available?"available":"planned")<<" | visual="<<(s.visuallyAccepted?"accepted":"pending")<<" | profile="<<s.profile<<" | "<<s.label<<"\n";
    }
    // Validate binary payload sizes without constructing a GL Mesh.
    void validateMesh(const SceneEntry& s)const {
        requireAvailable(s);std::ifstream f(root/s.mesh,std::ios::binary);char magic[8]{};uint32_t materials=0,vertices=0;
        f.read(magic,8);f.read(reinterpret_cast<char*>(&materials),4);f.read(reinterpret_cast<char*>(&vertices),4);
        if(!f||std::memcmp(magic,"DREAMM02",8)||materials==0||materials>32||vertices==0||vertices>3000000||vertices%3)throw std::runtime_error("Invalid dreammesh header: "+s.id);
        uint64_t expected=16+uint64_t(materials)*32+uint64_t(vertices)*40;
        if(std::filesystem::file_size(root/s.mesh)!=expected)throw std::runtime_error("Invalid dreammesh payload size: "+s.id);
        bool transparent=false;
        for(uint32_t i=0;i<materials;i++) {float material[8]{};f.read(reinterpret_cast<char*>(material),sizeof(material));int kind=int(material[5]+.1f);transparent|=kind==6||kind==9;}
        auto ranges=root/s.mesh;ranges.replace_extension(".draws");std::ifstream rf(ranges);std::string line;int count=0;
        while(std::getline(rf,line)) {
            std::istringstream in(line);long long first=0,n=0;float x=0,y=0,z=0;std::string extra;
            in>>std::ws;if(in.eof()||in.peek()=='#')continue;
            if(!(in>>first))throw std::runtime_error("Invalid transparent draw group: "+s.id);
            if(!(in>>n>>x>>y>>z)||in>>extra||first<0||n<=0||first%3||n%3||uint64_t(first+n)>vertices)throw std::runtime_error("Invalid transparent draw group: "+s.id);
            ++count;
        }
        if(transparent&&!count)throw std::runtime_error("Missing transparent draw groups: "+s.id);
    }
    void validateTextures(const SceneProfile& p)const {
        for(const auto& path:p.textures) {
            std::ifstream f(root/path,std::ios::binary);unsigned char h[54]{};f.read(reinterpret_cast<char*>(h),54);
            auto u32=[&](int at){uint32_t v=0;std::memcpy(&v,h+at,4);return v;};
            uint32_t w=u32(18),height=u32(22);uint64_t stride=(uint64_t(w)*3+3)&~uint64_t(3);
            if(!f||h[0]!='B'||h[1]!='M'||h[28]!=24||h[29]!=0||u32(30)!=0||w==0||height==0||w>8192||height>8192||u32(10)<54||std::filesystem::file_size(root/path)<u32(10)+stride*height)throw std::runtime_error("Invalid RGB24 texture: "+path.string());
        }
    }
};
