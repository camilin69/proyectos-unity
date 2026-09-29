import test from 'node:test';
import assert from 'node:assert/strict';
import { MAPS, groundHeight, moveWithCollision, type PlayerState } from '../shared/world.ts';
import { resolveShot, stepPlayer } from '../server/simulation.ts';

const player = (id: string, x: number, z: number, team: PlayerState['team']): PlayerState => ({
  id, name: id, character: 'kira', team, x, y: 0, z, yaw: -Math.PI / 2, pitch: 0, hp: 100, kills: 0, deaths: 0,
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
  stepPlayer(MAPS.delta, mover, { forward: false, back: false, left: true, right: false, crouch: false, walk: false, yaw: 0, pitch: 0 }, 0.1);
  assert.ok(mover.x < -5);
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
