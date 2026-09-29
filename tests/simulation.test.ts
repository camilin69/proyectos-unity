import test from 'node:test';
import assert from 'node:assert/strict';
import { EMPTY_INPUT, MAPS, groundHeight, insideSolid, moveWithCollision, type PlayerState } from '../shared/world.ts';
import { resolveShot, safeSpawn, stepPlayer } from '../server/simulation.ts';

const player = (id: string, x: number, z: number, team: PlayerState['team']): PlayerState => ({
  id, name: id, character: 'kira', team, x, y: 0, vy: 0, z, yaw: -Math.PI / 2, pitch: 0, hp: 100, crouching: false, kills: 0, deaths: 0,
});

test('las escaleras llegan a la plataforma en ambos escenarios', () => {
  for (const map of Object.values(MAPS)) {
    const stair = map.stairs[0];
    const lowerX = stair.direction === 1 ? stair.x - stair.w / 2 : stair.x + stair.w / 2;
    const upperX = stair.direction === 1 ? stair.x + stair.w / 2 : stair.x - stair.w / 2;
    assert.ok(groundHeight(map, lowerX, stair.z) < 0.01);
    assert.ok(Math.abs(groundHeight(map, upperX, stair.z) - stair.h) < 0.01);
    const platform = map.platforms[0];
    assert.equal(groundHeight(map, platform.x, platform.z), stair.h);
  }
});

test('la colisión detiene al jugador ante una caja pero conserva deslizamiento lateral', () => {
  const [x] = moveWithCollision(MAPS.delta, -3, 0, 0, -2);
  const [, , z] = moveWithCollision(MAPS.delta, -3, 0, 1, 0);
  assert.equal(x, -3);
  assert.equal(z, 0);
  const mover = player('mover', -5, -3, 'intrusos');
  stepPlayer(MAPS.delta, mover, { ...EMPTY_INPUT, left: true, yaw: 0 }, 0.1);
  assert.ok(mover.x < -5);
});

test('la carrera acelera, agacharse reduce velocidad y el salto aterriza con gravedad', () => {
  const normal = player('normal', -26, 0, 'intrusos');
  const runner = player('runner', -26, 0, 'intrusos');
  const croucher = player('croucher', -26, 0, 'intrusos');
  stepPlayer(MAPS.delta, normal, { ...EMPTY_INPUT, forward: true, yaw: -Math.PI / 2 }, 0.1);
  stepPlayer(MAPS.delta, runner, { ...EMPTY_INPUT, forward: true, sprint: true, yaw: -Math.PI / 2 }, 0.1);
  stepPlayer(MAPS.delta, croucher, { ...EMPTY_INPUT, forward: true, crouch: true, yaw: -Math.PI / 2 }, 0.1);
  assert.ok(runner.x > normal.x && normal.x > croucher.x);
  assert.equal(croucher.crouching, true);
  const jumper = player('jumper', -26, 0, 'intrusos');
  stepPlayer(MAPS.delta, jumper, { ...EMPTY_INPUT, jump: true }, 1 / 30);
  assert.ok(jumper.y > 0 && jumper.vy > 0);
  for (let index = 0; index < 80; index++) stepPlayer(MAPS.delta, jumper, EMPTY_INPUT, 1 / 30);
  assert.equal(jumper.y, 0);
  assert.equal(jumper.vy, 0);
});

test('el servidor distingue impacto libre, cobertura y equipo aliado', () => {
  const shooter = player('shooter', -3, 0, 'intrusos');
  const target = player('target', 3, 0, 'custodios');
  assert.equal(resolveShot(MAPS.delta, shooter, [shooter, target]).hitId, 'target');
  target.z = -3;
  shooter.z = -3;
  assert.equal(resolveShot(MAPS.delta, shooter, [shooter, target]).hitId, null);
  target.z = 0;
  shooter.z = 0;
  target.team = 'intrusos';
  assert.equal(resolveShot(MAPS.delta, shooter, [shooter, target]).hitId, null);
});

test('cabeza, torso, brazos y piernas reciben daños diferentes según la trayectoria', () => {
  const shooter = player('shooter', -3, 0, 'intrusos');
  const target = player('target', 3, 0, 'custodios');
  target.yaw = Math.PI / 2;
  const aim = (pitch: number) => resolveShot(MAPS.delta, shooter, [shooter, target], -Math.PI / 2, pitch);
  assert.deepEqual([aim(0).zone, aim(0).damage], ['head', 85]);
  assert.deepEqual([aim(-0.09).zone, aim(-0.09).damage], ['torso', 34]);
  shooter.z = -0.16;
  assert.deepEqual([aim(-0.19).zone, aim(-0.19).damage], ['leg', 18]);
  shooter.z = -0.45;
  assert.deepEqual([aim(-0.09).zone, aim(-0.09).damage], ['arm', 22]);
});

test('todos contra todos permite impacto entre jugadores asignados al mismo equipo', () => {
  const shooter = player('shooter', -3, 0, 'intrusos');
  const target = player('target', 3, 0, 'intrusos');
  assert.equal(resolveShot(MAPS.delta, shooter, [shooter, target]).hitId, null);
  const shot = resolveShot(MAPS.delta, shooter, [shooter, target], shooter.yaw, 0, 'ffa');
  assert.equal(shot.hitId, 'target');
  assert.ok(shot.damage > 0);
  target.crouching = true;
  assert.equal(resolveShot(MAPS.delta, shooter, [shooter, target], shooter.yaw, 0, 'ffa').hitId, null);
  assert.equal(resolveShot(MAPS.delta, shooter, [shooter, target], shooter.yaw, -0.08, 'ffa').hitId, 'target');
});

test('los puntos de aparición varían y separan a los jugadores sin atravesar obstáculos', () => {
  let seed = 7;
  const random = () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 2 ** 32);
  for (const map of Object.values(MAPS)) {
    const occupied: PlayerState[] = [];
    for (let index = 0; index < 10; index++) {
      const team = index % 2 ? 'custodios' : 'intrusos';
      const [x, y, z] = safeSpawn(map, team, occupied, random);
      assert.equal(insideSolid(map, x, z, y, 0.75), false);
      for (const other of occupied) assert.ok(Math.hypot(x - other.x, z - other.z) >= 6);
      occupied.push({ ...player(String(index), x, z, team), y });
    }
    assert.ok(new Set(occupied.map(({ x, z }) => `${x.toFixed(2)},${z.toFixed(2)}`)).size === 10);
  }
});

test('todos contra todos reparte apariciones por todo el mapa y lejos de otros jugadores', () => {
  let seed = 19;
  const random = () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 2 ** 32);
  for (const map of Object.values(MAPS)) {
    const occupied: PlayerState[] = [];
    for (let index = 0; index < 10; index++) {
      const [x, y, z] = safeSpawn(map, 'intrusos', occupied, random, 'ffa');
      assert.equal(insideSolid(map, x, z, y, 0.75), false);
      for (const other of occupied) assert.ok(Math.hypot(x - other.x, z - other.z) >= 8);
      occupied.push({ ...player(String(index), x, z, 'intrusos'), y });
    }
    assert.ok(occupied.some((entry) => entry.x < 0));
    assert.ok(occupied.some((entry) => entry.x > 0));
  }
});
