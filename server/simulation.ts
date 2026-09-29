import { groundHeight, insideSolid, moveWithCollision, type ArenaMap, type InputState, type PlayerState } from '../shared/world.ts';

export function stepPlayer(map: ArenaMap, player: PlayerState, input: InputState, seconds: number): void {
  if (player.hp <= 0) return;
  const f = Number(input.forward) - Number(input.back);
  const r = Number(input.right) - Number(input.left);
  const length = Math.hypot(f, r) || 1;
  const speed = input.crouch ? 2.1 : input.walk ? 3.1 : 5.2;
  const dx = ((-Math.sin(input.yaw) * f + Math.cos(input.yaw) * r) / length) * speed * seconds;
  const dz = ((-Math.cos(input.yaw) * f - Math.sin(input.yaw) * r) / length) * speed * seconds;
  const [x, y, z] = moveWithCollision(map, player.x, player.z, dx, dz);
  player.x = x;
  player.y = y;
  player.z = z;
  player.yaw = input.yaw;
  player.pitch = input.pitch;
}

type Vec3 = [number, number, number];

function rayBox(origin: Vec3, direction: Vec3, min: Vec3, max: Vec3): number | null {
  let near = 0;
  let far = 55;
  for (let axis = 0; axis < 3; axis++) {
    if (Math.abs(direction[axis]) < 1e-8) {
      if (origin[axis] < min[axis] || origin[axis] > max[axis]) return null;
      continue;
    }
    const a = (min[axis] - origin[axis]) / direction[axis];
    const b = (max[axis] - origin[axis]) / direction[axis];
    near = Math.max(near, Math.min(a, b));
    far = Math.min(far, Math.max(a, b));
    if (near > far) return null;
  }
  return near;
}

function raySphere(origin: Vec3, direction: Vec3, center: Vec3, radius: number): number | null {
  const ox = origin[0] - center[0];
  const oy = origin[1] - center[1];
  const oz = origin[2] - center[2];
  const b = ox * direction[0] + oy * direction[1] + oz * direction[2];
  const c = ox * ox + oy * oy + oz * oz - radius * radius;
  const discriminant = b * b - c;
  if (discriminant < 0) return null;
  const distance = -b - Math.sqrt(discriminant);
  return distance >= 0 ? distance : null;
}

export interface ShotResult {
  hitId: string | null;
  position: Vec3;
  damage: number;
}

export function resolveShot(map: ArenaMap, shooter: PlayerState, players: Iterable<PlayerState>): ShotResult {
  const origin: Vec3 = [shooter.x, shooter.y + 1.5, shooter.z];
  const cosine = Math.cos(shooter.pitch);
  const direction: Vec3 = [-Math.sin(shooter.yaw) * cosine, Math.sin(shooter.pitch), -Math.cos(shooter.yaw) * cosine];
  let nearest = 50;
  let hitId: string | null = null;

  for (const solid of map.solids) {
    const y = solid.y ?? 0;
    const distance = rayBox(
      origin,
      direction,
      [solid.x - solid.w / 2, y, solid.z - solid.d / 2],
      [solid.x + solid.w / 2, y + solid.h, solid.z + solid.d / 2],
    );
    if (distance !== null) nearest = Math.min(nearest, distance);
  }
  for (const platform of map.platforms) {
    const distance = rayBox(
      origin, direction,
      [platform.x - platform.w / 2, platform.h - 0.22, platform.z - platform.d / 2],
      [platform.x + platform.w / 2, platform.h, platform.z + platform.d / 2],
    );
    if (distance !== null) nearest = Math.min(nearest, distance);
  }
  for (const target of players) {
    if (target.id === shooter.id || target.team === shooter.team || target.hp <= 0) continue;
    const body = raySphere(origin, direction, [target.x, target.y + 0.95, target.z], 0.53);
    const head = raySphere(origin, direction, [target.x, target.y + 1.62, target.z], 0.25);
    const distance = Math.min(body ?? Infinity, head ?? Infinity);
    if (distance < nearest) {
      nearest = distance;
      hitId = target.id;
    }
  }
  return {
    hitId,
    damage: 34,
    position: [origin[0] + direction[0] * nearest, origin[1] + direction[1] * nearest, origin[2] + direction[2] * nearest],
  };
}

export function safeSpawn(map: ArenaMap, team: PlayerState['team'], slot: number): [number, number, number] {
  const [baseX, baseZ] = map.spawns[team];
  for (let offset = 0; offset < 8; offset++) {
    const x = baseX + (slot % 2) * 1.5 + offset * 0.45;
    const z = baseZ + (Math.floor(slot / 2) % 3) * 1.7;
    const y = groundHeight(map, x, z);
    if (!insideSolid(map, x, z, y)) return [x, y, z];
  }
  return [baseX, groundHeight(map, baseX, baseZ), baseZ];
}
