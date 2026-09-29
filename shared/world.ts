export type CharacterId = 'kira' | 'vektor' | 'atlas';
export type TeamId = 'intrusos' | 'custodios';
export type MapId = 'delta' | 'terminal';

export interface Solid {
  id: string;
  kind: 'wall' | 'crate' | 'container' | 'hideout' | 'pillar' | 'roof';
  x: number;
  z: number;
  w: number;
  d: number;
  h: number;
  y?: number;
}

export interface Stair {
  id: string;
  x: number;
  z: number;
  w: number;
  d: number;
  h: number;
  direction: 1 | -1;
}

export interface Platform {
  id: string;
  x: number;
  z: number;
  w: number;
  d: number;
  h: number;
}

export interface ArenaMap {
  id: MapId;
  name: string;
  subtitle: string;
  width: number;
  depth: number;
  ground: string;
  accent: string;
  fog: string;
  solids: Solid[];
  stairs: Stair[];
  platforms: Platform[];
  spawns: Record<TeamId, [number, number]>;
}

const box = (id: string, kind: Solid['kind'], x: number, z: number, w: number, d: number, h: number, y = 0): Solid => ({ id, kind, x, z, w, d, h, y });

const delta: ArenaMap = {
  id: 'delta', name: 'DEPÓSITO DELTA', subtitle: 'Almacén ferroviario · 02:14',
  width: 64, depth: 46, ground: '#505c5e', accent: '#f1b861', fog: '#17242a',
  spawns: { intrusos: [-26, 0], custodios: [26, 0] },
  solids: [
    box('d-w1', 'wall', -8, -8, 1.2, 18, 4), box('d-w2', 'wall', 8, 8, 1.2, 18, 4),
    box('d-w3', 'wall', -19, 13, 11, 1.2, 3.8), box('d-w4', 'wall', 19, -13, 11, 1.2, 3.8),
    box('d-c1', 'container', -18, -9, 7, 3.5, 2.5), box('d-c2', 'container', 17, 10, 7, 3.5, 2.5),
    box('d-c3', 'container', 1, -14, 6, 3, 2.5), box('d-c4', 'container', -1, 14, 6, 3, 2.5),
    box('d-b1', 'crate', -3, -3, 2.4, 2.4, 1.7), box('d-b2', 'crate', 4, 2, 2.4, 2.4, 1.7),
    box('d-b3', 'crate', -23, 11, 2.4, 2.4, 1.7), box('d-b4', 'crate', 23, -10, 2.4, 2.4, 1.7),
    box('d-p1', 'pillar', -13, 3, 1.4, 1.4, 5), box('d-p2', 'pillar', 13, -3, 1.4, 1.4, 5),
    // Cabinas en U: su hueco central se puede ocupar y solo se accede por un lado.
    box('d-h1a', 'hideout', -26, -16, 0.6, 6, 2.8), box('d-h1b', 'hideout', -22.5, -19, 7, 0.6, 2.8), box('d-h1c', 'hideout', -19, -16, 0.6, 6, 2.8),
    box('d-h2a', 'hideout', 19, 16, 0.6, 6, 2.8), box('d-h2b', 'hideout', 22.5, 19, 7, 0.6, 2.8), box('d-h2c', 'hideout', 26, 16, 0.6, 6, 2.8),
    box('d-h1roof', 'roof', -22.5, -16, 7.6, 6.6, 0.24, 2.8),
    box('d-h2roof', 'roof', 22.5, 16, 7.6, 6.6, 0.24, 2.8),
  ],
  stairs: [{ id: 'd-s1', x: 8, z: -17, w: 6, d: 3, h: 2.8, direction: 1 }],
  platforms: [{ id: 'd-pl1', x: 17, z: -17, w: 12, d: 6, h: 2.8 }],
};

const terminal: ArenaMap = {
  id: 'terminal', name: 'TERMINAL NOCTURNA', subtitle: 'Nodo de carga · 23:41',
  width: 68, depth: 48, ground: '#414b58', accent: '#6ed6ca', fog: '#121c2f',
  spawns: { intrusos: [-28, -2], custodios: [28, 2] },
  solids: [
    box('t-w1', 'wall', -12, 7, 1.1, 20, 5), box('t-w2', 'wall', 12, -7, 1.1, 20, 5),
    box('t-w3', 'wall', 0, -10, 11, 1.1, 3.7), box('t-w4', 'wall', 0, 10, 11, 1.1, 3.7),
    box('t-c1', 'container', -20, -10, 6, 3.2, 2.6), box('t-c2', 'container', 20, 10, 6, 3.2, 2.6),
    box('t-c3', 'container', -1, -18, 7, 3, 2.6), box('t-c4', 'container', 1, 18, 7, 3, 2.6),
    box('t-b1', 'crate', -5, 2, 2.4, 2.4, 1.7), box('t-b2', 'crate', 5, -2, 2.4, 2.4, 1.7),
    box('t-b3', 'crate', -22, 12, 2.4, 2.4, 1.7), box('t-b4', 'crate', 22, -12, 2.4, 2.4, 1.7),
    box('t-p1', 'pillar', -3, -3, 1.5, 1.5, 5.5), box('t-p2', 'pillar', 3, 3, 1.5, 1.5, 5.5),
    box('t-h1a', 'hideout', -28, 16, 0.6, 6, 2.8), box('t-h1b', 'hideout', -24.5, 19, 7, 0.6, 2.8), box('t-h1c', 'hideout', -21, 16, 0.6, 6, 2.8),
    box('t-h2a', 'hideout', 21, -16, 0.6, 6, 2.8), box('t-h2b', 'hideout', 24.5, -19, 7, 0.6, 2.8), box('t-h2c', 'hideout', 28, -16, 0.6, 6, 2.8),
    box('t-h1roof', 'roof', -24.5, 16, 7.6, 6.6, 0.24, 2.8),
    box('t-h2roof', 'roof', 24.5, -16, 7.6, 6.6, 0.24, 2.8),
  ],
  stairs: [{ id: 't-s1', x: -14, z: -18, w: 6, d: 3, h: 3.2, direction: -1 }],
  platforms: [{ id: 't-pl1', x: -23, z: -18, w: 12, d: 6, h: 3.2 }],
};

export const MAPS: Record<MapId, ArenaMap> = { delta, terminal };
export const CHARACTER_IDS: CharacterId[] = ['kira', 'vektor', 'atlas'];

export interface PlayerState {
  id: string;
  name: string;
  character: CharacterId;
  team: TeamId;
  x: number;
  y: number;
  z: number;
  yaw: number;
  pitch: number;
  hp: number;
  kills: number;
  deaths: number;
}

export interface LobbyState {
  code: string;
  hostId: string;
  phase: 'lobby' | 'playing' | 'intermission' | 'finished';
  map: MapId;
  votes: Record<MapId, number>;
  playerVotes: Record<string, MapId>;
  players: PlayerState[];
  roundSeconds: number;
  matchMinutes: number;
  targetScore: number;
  scores: Record<TeamId, number>;
  round: number;
  endsAt: number;
  matchEndsAt: number;
  nextAt: number;
  winner: TeamId | 'empate' | null;
  announcement: string;
}

export interface InputState {
  forward: boolean;
  back: boolean;
  left: boolean;
  right: boolean;
  crouch: boolean;
  walk: boolean;
  yaw: number;
  pitch: number;
}

export type ClientMessage =
  | { type: 'join'; name: string; character: CharacterId }
  | { type: 'input'; input: InputState }
  | { type: 'fire'; shotId: number; yaw: number; pitch: number }
  | { type: 'vote'; map: MapId }
  | { type: 'configure'; roundSeconds: number; matchMinutes: number; targetScore: number }
  | { type: 'start' }
  | { type: 'rematch' };

export type ServerMessage =
  | { type: 'welcome'; id: string; code: string; team: TeamId }
  | { type: 'lobby'; state: LobbyState }
  | { type: 'snapshot'; players: PlayerState[]; at: number }
  | { type: 'shot'; shooterId: string; hitId: string | null; x: number; y: number; z: number; shotId: number }
  | { type: 'elimination'; killerId: string; victimId: string }
  | { type: 'error'; message: string };

export const EMPTY_INPUT: InputState = { forward: false, back: false, left: false, right: false, crouch: false, walk: false, yaw: 0, pitch: 0 };

export function groundHeight(map: ArenaMap, x: number, z: number): number {
  for (const platform of map.platforms) {
    if (Math.abs(x - platform.x) <= platform.w / 2 && Math.abs(z - platform.z) <= platform.d / 2) return platform.h;
  }
  for (const stair of map.stairs) {
    if (Math.abs(x - stair.x) <= stair.w / 2 && Math.abs(z - stair.z) <= stair.d / 2) {
      const progress = (x - (stair.x - stair.w / 2)) / stair.w;
      return stair.h * (stair.direction === 1 ? progress : 1 - progress);
    }
  }
  return 0;
}

export function insideSolid(map: ArenaMap, x: number, z: number, footY: number, radius = 0.38): boolean {
  if (Math.abs(x) > map.width / 2 - radius - 0.6 || Math.abs(z) > map.depth / 2 - radius - 0.6) return true;
  return map.solids.some((s) =>
    Math.abs(x - s.x) < s.w / 2 + radius &&
    Math.abs(z - s.z) < s.d / 2 + radius &&
    footY < (s.y ?? 0) + s.h && footY + 1.7 > (s.y ?? 0),
  );
}

export function moveWithCollision(map: ArenaMap, x: number, z: number, dx: number, dz: number): [number, number, number] {
  let nx = x;
  let nz = z;
  const oldY = groundHeight(map, x, z);
  const canEnter = (tx: number, tz: number) => {
    const h = groundHeight(map, tx, tz);
    if (h > oldY + 0.65) return false;
    return !insideSolid(map, tx, tz, h);
  };
  if (canEnter(x + dx, z)) nx += dx;
  if (canEnter(nx, z + dz)) nz += dz;
  return [nx, groundHeight(map, nx, nz), nz];
}
