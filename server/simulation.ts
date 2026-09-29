import { groundHeight, insideSolid, moveWithCollision, type ArenaMap, type GameMode, type HitZone, type InputState, type PlayerState } from '../shared/world.ts';

export function stepPlayer(map: ArenaMap, player: PlayerState, input: InputState, seconds: number): void {
  if (player.hp <= 0) return;
  const f = Number(input.forward) - Number(input.back);
  const r = Number(input.right) - Number(input.left);
  const length = Math.hypot(f, r) || 1;
  const speed = input.crouch ? 2.1 : input.sprint ? 8.2 : 5.2;
  const dx = ((-Math.sin(input.yaw) * f + Math.cos(input.yaw) * r) / length) * speed * seconds;
  const dz = ((-Math.cos(input.yaw) * f - Math.sin(input.yaw) * r) / length) * speed * seconds;
  const grounded = player.y <= groundHeight(map, player.x, player.z) + 0.02 && player.vy <= 0;
  const [x, ground, z] = moveWithCollision(map, player.x, player.z, dx, dz);
  player.x = x;
  player.z = z;
  player.crouching = input.crouch;
  if (grounded && input.jump && !input.crouch) player.vy = 7.4;
  player.vy = Math.max(-25, player.vy - 21 * seconds);
  const nextY = player.y + player.vy * seconds;
  player.y = Math.max(ground, nextY);
  if (player.y === ground) player.vy = 0;
  if (player.vy > 0) {
    const height = input.crouch ? 1.18 : 1.8;
    for (const solid of map.solids) {
      const ceiling = solid.y ?? 0;
      if (ceiling <= ground || Math.abs(x - solid.x) >= solid.w / 2 + 0.34 || Math.abs(z - solid.z) >= solid.d / 2 + 0.34) continue;
      if (player.y + height > ceiling && nextY - player.vy * seconds + height <= ceiling) {
        player.y = ceiling - height;
        player.vy = 0;
        break;
      }
    }
  }
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
  const root = Math.sqrt(discriminant);
  const entry = -b - root;
  if (entry >= 0) return entry;
  const exit = -b + root;
  return exit >= 0 ? exit : null;
}

export interface ShotResult {
  hitId: string | null;
  zone: HitZone | null;
  origin: Vec3;
  position: Vec3;
  damage: number;
}

const ZONE_DAMAGE: Record<HitZone, number> = { head: 85, torso: 34, arm: 22, leg: 18 };

export function resolveShot(map: ArenaMap, shooter: PlayerState, players: Iterable<PlayerState>, yaw = shooter.yaw, pitch = shooter.pitch, mode: GameMode = 'teams'): ShotResult {
  const origin: Vec3 = [shooter.x, shooter.y + (shooter.crouching ? 1.04 : 1.5), shooter.z];
  const cosine = Math.cos(pitch);
  const direction: Vec3 = [-Math.sin(yaw) * cosine, Math.sin(pitch), -Math.cos(yaw) * cosine];
  let nearest = 50;
  let hitId: string | null = null;
  let zone: HitZone | null = null;

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
    if (target.id === shooter.id || (mode === 'teams' && target.team === shooter.team) || target.hp <= 0) continue;
    const sine = Math.sin(target.yaw);
    const cosine = Math.cos(target.yaw);
    const dx = origin[0] - target.x;
    const dz = origin[2] - target.z;
    const heightScale = target.crouching ? 0.68 : 1;
    const localOrigin: Vec3 = [cosine * dx - sine * dz, (origin[1] - target.y) / heightScale, sine * dx + cosine * dz];
    const localDirection: Vec3 = [cosine * direction[0] - sine * direction[2], direction[1] / heightScale, sine * direction[0] + cosine * direction[2]];
    const hitboxes: [HitZone, number | null][] = [
      ['head', raySphere(localOrigin, localDirection, [0, 1.72, 0], 0.24)],
      ['torso', rayBox(localOrigin, localDirection, [-0.32, 0.76, -0.24], [0.32, 1.44, 0.24])],
      ['arm', rayBox(localOrigin, localDirection, [-0.62, 0.67, -0.23], [-0.33, 1.39, 0.23])],
      ['arm', rayBox(localOrigin, localDirection, [0.33, 0.67, -0.23], [0.62, 1.39, 0.23])],
      ['leg', rayBox(localOrigin, localDirection, [-0.33, 0.07, -0.22], [-0.02, 0.75, 0.22])],
      ['leg', rayBox(localOrigin, localDirection, [0.02, 0.07, -0.22], [0.33, 0.75, 0.22])],
    ];
    for (const [part, distance] of hitboxes) {
      if (distance !== null && distance < nearest) {
        nearest = distance;
        hitId = target.id;
        zone = part;
      }
    }
  }
  return {
    hitId,
    zone,
    origin,
    damage: zone ? ZONE_DAMAGE[zone] : 0,
    position: [origin[0] + direction[0] * nearest, origin[1] + direction[1] * nearest, origin[2] + direction[2] * nearest],
  };
}

export function safeSpawn(
  map: ArenaMap,
  team: PlayerState['team'],
  occupied: Pick<PlayerState, 'x' | 'z'>[],
  random: () => number = Math.random,
  mode: GameMode = 'teams',
): [number, number, number] {
  const side = team === 'intrusos' ? -1 : 1;
  const minX = map.width * 0.17;
  const maxX = map.width / 2 - 2.3;
  const maxZ = map.depth / 2 - 2.3;
  const minDistance = mode === 'ffa' ? 8 : 6;
  let best: [number, number, number] | null = null;
  let bestDistance = -1;
  const consider = (x: number, z: number): boolean => {
    const y = groundHeight(map, x, z);
    if (y > 0.1 || insideSolid(map, x, z, y, 0.75)) return false;
    const distance = occupied.length ? Math.min(...occupied.map((player) => Math.hypot(x - player.x, z - player.z))) : Infinity;
    if (distance > bestDistance) { bestDistance = distance; best = [x, y, z]; }
    return distance >= minDistance;
  };
  for (let attempt = 0; attempt < 100; attempt++) {
    const x = mode === 'ffa' ? (random() * 2 - 1) * maxX : side * (minX + random() * (maxX - minX));
    const z = (random() * 2 - 1) * maxZ;
    if (consider(x, z)) return [x, groundHeight(map, x, z), z];
  }
  for (let x = mode === 'ffa' ? -maxX : minX; x <= maxX; x += 2.5) for (let z = -maxZ; z <= maxZ; z += 2.5) consider(mode === 'ffa' ? x : side * x, z);
  if (best) return best;
  const [baseX, baseZ] = map.spawns[team];
  return [baseX, groundHeight(map, baseX, baseZ), baseZ];
}
