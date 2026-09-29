import test from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { createServer } from 'node:net';
import WebSocket from 'ws';
import type { ServerMessage } from '../shared/world.ts';

async function freePort(): Promise<number> {
  const server = createServer();
  await new Promise<void>((resolve) => server.listen(0, '127.0.0.1', resolve));
  const address = server.address();
  if (!address || typeof address === 'string') throw new Error('Sin puerto de prueba');
  const port = address.port;
  await new Promise<void>((resolve) => server.close(() => resolve()));
  return port;
}

function connect(port: number, code: string): Promise<WebSocket> {
  return new Promise((resolve, reject) => {
    const socket = new WebSocket(`ws://127.0.0.1:${port}/?room=${code}`);
    socket.once('open', () => resolve(socket));
    socket.once('error', reject);
  });
}

function waitFor(socket: WebSocket, predicate: (message: ServerMessage) => boolean, timeout = 3500): Promise<ServerMessage> {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => { socket.off('message', onMessage); reject(new Error('Sin mensaje esperado')); }, timeout);
    const onMessage = (raw: WebSocket.RawData) => {
      const message = JSON.parse(raw.toString()) as ServerMessage;
      if (predicate(message)) {
        clearTimeout(timer);
        socket.off('message', onMessage);
        resolve(message);
      }
    };
    socket.on('message', onMessage);
  });
}

test('lobby separa salas, vota mapa, configura puntos y comienza partida', { timeout: 12000 }, async () => {
  const port = await freePort();
  const server = spawn(process.execPath, ['--import', 'tsx', 'server/index.ts'], {
    cwd: process.cwd(), env: { ...process.env, PORT: String(port) }, stdio: ['ignore', 'pipe', 'pipe'],
  });
  const sockets: WebSocket[] = [];
  try {
    await new Promise<void>((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error('Servidor no arrancó')), 5000);
      server.stdout!.on('data', (data) => { if (data.toString().includes('escuchando')) { clearTimeout(timer); resolve(); } });
      server.once('exit', (code) => { clearTimeout(timer); reject(new Error(`Servidor terminó: ${code}`)); });
    });
    const a = await connect(port, 'ALFA');
    const b = await connect(port, 'ALFA');
    const c = await connect(port, 'BETA');
    sockets.push(a, b, c);
    const wa = waitFor(a, (m) => m.type === 'welcome');
    const wb = waitFor(b, (m) => m.type === 'welcome');
    const wc = waitFor(c, (m) => m.type === 'welcome');
    const joined = waitFor(a, (m) => m.type === 'lobby' && m.state.players.length === 2);
    a.send(JSON.stringify({ type: 'join', name: 'Uno', character: 'kira' }));
    b.send(JSON.stringify({ type: 'join', name: 'Dos', character: 'atlas' }));
    c.send(JSON.stringify({ type: 'join', name: 'Tres', character: 'vektor' }));
    const [ma, mb, mc, initial] = await Promise.all([wa, wb, wc, joined]);
    assert.equal(ma.type, 'welcome');
    assert.equal(mb.type, 'welcome');
    assert.equal(mc.type, 'welcome');
    assert.equal(initial.type, 'lobby');
    if (ma.type !== 'welcome' || mb.type !== 'welcome' || mc.type !== 'welcome' || initial.type !== 'lobby') return;
    assert.notEqual(ma.team, mb.team);
    assert.equal(mc.code, 'BETA');
    assert.equal(initial.state.hostId, ma.id);
    assert.deepEqual(new Set(initial.state.players.map((p) => p.character)), new Set(['kira', 'atlas']));

    const voting = waitFor(a, (m) => m.type === 'lobby' && m.state.votes.delta === 1 && m.state.votes.terminal === 1);
    a.send(JSON.stringify({ type: 'vote', map: 'terminal' }));
    b.send(JSON.stringify({ type: 'vote', map: 'delta' }));
    await voting;

    const configured = waitFor(b, (m) => m.type === 'lobby' && m.state.roundSeconds === 60 && m.state.matchMinutes === 5 && m.state.targetScore === 1);
    b.send(JSON.stringify({ type: 'configure', roundSeconds: 300, matchMinutes: 30, targetScore: 9 }));
    a.send(JSON.stringify({ type: 'configure', roundSeconds: 60, matchMinutes: 5, targetScore: 1 }));
    await configured;

    const started = waitFor(b, (m) => m.type === 'lobby' && m.state.phase === 'playing');
    a.send(JSON.stringify({ type: 'start' }));
    const play = await started;
    assert.equal(play.type, 'lobby');
    if (play.type !== 'lobby') return;
    assert.equal(play.state.map, 'terminal'); // Empate: decide el voto del anfitrión.
    assert.equal(play.state.round, 1);
    assert.equal(play.state.targetScore, 1);
    assert.equal(play.state.matchMinutes, 5);

    const isolated = waitFor(c, (m) => m.type === 'lobby' && m.state.players.length === 1);
    c.send(JSON.stringify({ type: 'vote', map: 'delta' }));
    const beta = await isolated;
    assert.equal(beta.type, 'lobby');
    if (beta.type === 'lobby') assert.equal(beta.state.phase, 'lobby');

    const shot = waitFor(a, (m) => m.type === 'shot' && m.shotId === 1);
    b.send(JSON.stringify({ type: 'fire', shotId: 1, yaw: 0, pitch: 0 }));
    await shot;

    const final = waitFor(a, (m) => m.type === 'lobby' && m.state.phase === 'finished');
    b.close();
    const result = await final;
    assert.equal(result.type, 'lobby');
    if (result.type === 'lobby') {
      assert.equal(result.state.scores.intrusos, 1);
      assert.equal(result.state.winner, 'intrusos');
    }
  } finally {
    for (const socket of sockets) socket.close();
    server.kill();
  }
});
