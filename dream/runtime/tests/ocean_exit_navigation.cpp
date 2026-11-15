#include "../src/scene.hpp"
#include <cmath>
#include <iostream>
#include <stdexcept>

int main(int argc, char** argv) {
    if (argc != 2) throw std::runtime_error("Usage: ocean_exit_navigation <scene-file>");
    const SceneSettings scene(argv[1]);

    Vec3 forward = scene.spawn;
    const float step = 1.6f / 60.0f;
    for (int frame = 0; frame < 300; ++frame)
        forward = scene.move(forward, {std::cos(scene.yaw) * step,
                                       std::sin(scene.yaw) * step, 0.0f});
    if (forward.y < 7.0f || forward.y > 8.5f || !scene.hasSupport(forward))
        throw std::runtime_error("The player cannot walk through the exit and onto the ocean support");

    Vec3 rail = scene.spawn;
    for (int frame = 0; frame < 240; ++frame)
        rail = scene.move(rail, {-step, 0.0f, 0.0f});
    if (rail.x > -0.61f || rail.x < -0.67f || !scene.hasSupport(rail))
        throw std::runtime_error("The left low border does not block the player at its calibrated edge");

    std::cout << "navigation=PASS exit_y=" << forward.y << " rail_edge_x=" << rail.x << '\n';
}
