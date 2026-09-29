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

function waitFor(socket: WebSocket, predicate: (message: ServerMessage) => boolean, timeout = 6000, label = 'mensaje'): Promise<ServerMessage> {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => { socket.off('message', onMessage); reject(new Error(`Sin ${label} esperado`)); }, timeout);
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

test('lobby separa salas, vota mapa, configura puntos y comienza partida', { timeout: 20000 }, async () => {
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
    a.send(JSON.stringify({ type: 'join', name: 'Uno', character: 'kira' }));
    const ma = await wa;
    const wb = waitFor(b, (m) => m.type === 'welcome');
    const wc = waitFor(c, (m) => m.type === 'welcome');
    const joined = waitFor(a, (m) => m.type === 'lobby' && m.state.players.length === 2);
    b.send(JSON.stringify({ type: 'join', name: 'Dos', character: 'atlas' }));
    c.send(JSON.stringify({ type: 'join', name: 'Tres', character: 'vektor' }));
    const [mb, mc, initial] = await Promise.all([wb, wc, joined]);
    assert.equal(ma.type, 'welcome');
    assert.equal(mb.type, 'welcome');
    assert.equal(mc.type, 'welcome');
    assert.equal(initial.type, 'lobby');
    if (ma.type !== 'welcome' || mb.type !== 'welcome' || mc.type !== 'welcome' || initial.type !== 'lobby') return;
    assert.notEqual(ma.team, mb.team);
    assert.equal(mc.code, 'BETA');
    assert.equal(initial.state.hostId, ma.id);
    assert.deepEqual(new Set(initial.state.players.map((p) => p.character)), new Set(['kira', 'atlas']));

    const sameTeam = waitFor(a, (m) => m.type === 'lobby' && m.state.players.length === 2 && m.state.players.every((player) => player.team === 'intrusos'));
    b.send(JSON.stringify({ type: 'selectTeam', team: 'intrusos' }));
    await sameTeam;
    const refused = waitFor(a, (m) => m.type === 'error' && m.message.includes('equipo'));
    a.send(JSON.stringify({ type: 'start' }));
    await refused;
    const restoredTeams = waitFor(a, (m) => m.type === 'lobby' && m.state.players.some((player) => player.id === mb.id && player.team === 'custodios'));
    b.send(JSON.stringify({ type: 'selectTeam', team: 'custodios' }));
    await restoredTeams;

    const voting = waitFor(a, (m) => m.type === 'lobby' && m.state.votes.delta === 1 && m.state.votes.terminal === 1);
    a.send(JSON.stringify({ type: 'vote', map: 'terminal' }));
    b.send(JSON.stringify({ type: 'vote', map: 'delta' }));
    await voting;

    const maxConfigured = waitFor(b, (m) => m.type === 'lobby' && m.state.targetScore === 50);
    a.send(JSON.stringify({ type: 'configure', roundSeconds: 120, matchMinutes: 15, targetScore: 50 }));
    await maxConfigured;

    const rejected = waitFor(b, (m) => m.type === 'lobby' && m.state.votes.terminal === 2);
    a.send(JSON.stringify({ type: 'configure', roundSeconds: 120, matchMinutes: 15, targetScore: 51 }));
    b.send(JSON.stringify({ type: 'vote', map: 'terminal' }));
    const unchanged = await rejected;
    assert.equal(unchanged.type, 'lobby');
    if (unchanged.type === 'lobby') assert.equal(unchanged.state.targetScore, 50);

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

test('todos contra todos inicia con jugadores del mismo equipo y decide ganador individual', { timeout: 20000 }, async () => {
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
    const a = await connect(port, 'LIBRE');
    const b = await connect(port, 'LIBRE');
    sockets.push(a, b);
    const welcome = waitFor(a, (m) => m.type === 'welcome', 6000, 'bienvenida');
    a.send(JSON.stringify({ type: 'join', name: 'Anfitrión', character: 'kira' }));
    const ma = await welcome;
    const joined = waitFor(a, (m) => m.type === 'lobby' && m.state.players.length === 2, 6000, 'lobby de dos');
    b.send(JSON.stringify({ type: 'join', name: 'Rival', character: 'atlas' }));
    await joined;
    assert.equal(ma.type, 'welcome');
    if (ma.type !== 'welcome') return;
    const sameTeam = waitFor(a, (m) => m.type === 'lobby' && m.state.players.every((player) => player.team === 'intrusos'), 6000, 'cambio de equipo');
    b.send(JSON.stringify({ type: 'selectTeam', team: 'intrusos' }));
    await sameTeam;
    const configured = waitFor(b, (m) => m.type === 'lobby' && m.state.mode === 'ffa' && m.state.targetScore === 2, 6000, 'configuración FFA');
    a.send(JSON.stringify({ type: 'configure', roundSeconds: 120, matchMinutes: 5, targetScore: 2, mode: 'ffa' }));
    await configured;
    const started = waitFor(a, (m) => m.type === 'lobby' && m.state.phase === 'playing', 6000, 'inicio FFA');
    a.send(JSON.stringify({ type: 'start' }));
    const play = await started;
    assert.equal(play.type, 'lobby');
    if (play.type !== 'lobby') return;
    assert.equal(play.state.mode, 'ffa');
    assert.equal(play.state.round, 1);
    assert.equal(play.state.endsAt, play.state.matchEndsAt);
    const finished = waitFor(a, (m) => m.type === 'lobby' && m.state.phase === 'finished', 6000, 'final FFA');
    b.close();
    const result = await finished;
    assert.equal(result.type, 'lobby');
    if (result.type === 'lobby') assert.equal(result.state.winnerId, ma.id);
  } finally {
    for (const socket of sockets) socket.close();
    server.kill();
  }
});
