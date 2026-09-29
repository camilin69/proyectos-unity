import { randomUUID } from 'node:crypto';
import { WebSocket, WebSocketServer } from 'ws';
import { CHARACTER_IDS, EMPTY_INPUT, MAPS, type ClientMessage, type InputState, type LobbyState, type MapId, type PlayerState, type ServerMessage, type TeamId } from '../shared/world.ts';
import { resolveShot, safeSpawn, stepPlayer } from './simulation.ts';

interface Connection {
  socket: WebSocket;
  room: Room;
  player: PlayerState | null;
  input: InputState;
  lastShot: number;
  lastShotId: number;
}

interface Room {
  code: string;
  members: Set<Connection>;
  hostId: string;
  phase: LobbyState['phase'];
  map: MapId;
  votes: Map<string, MapId>;
  roundSeconds: number;
  matchMinutes: number;
  targetScore: number;
  scores: Record<TeamId, number>;
  round: number;
  endsAt: number;
  matchEndsAt: number;
  nextAt: number;
  winner: LobbyState['winner'];
  announcement: string;
}

const PORT = Number(process.env.PORT ?? 2567);
const server = new WebSocketServer({ host: '0.0.0.0', port: PORT, maxPayload: 1024 });
const rooms = new Map<string, Room>();

function playersIn(room: Room): PlayerState[] {
  return [...room.members].flatMap((member) => member.player ? [member.player] : []);
}

function send(member: Connection, message: ServerMessage): void {
  if (member.socket.readyState === WebSocket.OPEN) member.socket.send(JSON.stringify(message));
}

function broadcast(room: Room, message: ServerMessage): void {
  for (const member of room.members) send(member, message);
}

function stateOf(room: Room): LobbyState {
  const votes = { delta: 0, terminal: 0 };
  const playerVotes: Record<string, MapId> = {};
  for (const [id, map] of room.votes) {
    playerVotes[id] = map;
    votes[map]++;
  }
  return {
    code: room.code, hostId: room.hostId, phase: room.phase, map: room.map,
    votes, playerVotes, players: playersIn(room), roundSeconds: room.roundSeconds, matchMinutes: room.matchMinutes,
    targetScore: room.targetScore, scores: { ...room.scores }, round: room.round,
    endsAt: room.endsAt, matchEndsAt: room.matchEndsAt, nextAt: room.nextAt, winner: room.winner,
    announcement: room.announcement,
  };
}

function announce(room: Room): void {
  broadcast(room, { type: 'lobby', state: stateOf(room) });
}

function roomFor(code: string): Room {
  const existing = rooms.get(code);
  if (existing) return existing;
  const room: Room = {
    code, members: new Set(), hostId: '', phase: 'lobby', map: 'delta', votes: new Map(),
    roundSeconds: 120, matchMinutes: 15, targetScore: 3, scores: { intrusos: 0, custodios: 0 },
    round: 0, endsAt: 0, matchEndsAt: 0, nextAt: 0, winner: null, announcement: 'Esperando jugadores',
  };
  rooms.set(code, room);
  return room;
}

function chooseTeam(room: Room): TeamId {
  const players = playersIn(room);
  return players.filter((player) => player.team === 'intrusos').length <= players.filter((player) => player.team === 'custodios').length ? 'intrusos' : 'custodios';
}

function handleJoin(member: Connection, message: Extract<ClientMessage, { type: 'join' }>): void {
  const room = member.room;
  if (member.player) return;
  if (room.phase !== 'lobby') {
    send(member, { type: 'error', message: 'La partida ya comenzó. Entra cuando vuelva al lobby.' });
    member.socket.close();
    return;
  }
  if (playersIn(room).length >= 10) {
    send(member, { type: 'error', message: 'La sala está llena.' });
    member.socket.close();
    return;
  }
  const character = CHARACTER_IDS.includes(message.character) ? message.character : 'kira';
  const name = typeof message.name === 'string' ? message.name.trim().slice(0, 18) || 'Operador' : 'Operador';
  const team = chooseTeam(room);
  const slot = playersIn(room).filter((p) => p.team === team).length;
  const [x, y, z] = safeSpawn(MAPS[room.map], team, slot);
  member.player = { id: randomUUID(), name, character, team, x, y, z, yaw: team === 'intrusos' ? -Math.PI / 2 : Math.PI / 2, pitch: 0, hp: 100, kills: 0, deaths: 0 };
  if (!room.hostId) room.hostId = member.player.id;
  send(member, { type: 'welcome', id: member.player.id, code: room.code, team });
  announce(room);
}

function validInput(value: InputState): value is InputState {
  return value && ['forward', 'back', 'left', 'right', 'crouch', 'walk'].every((key) => typeof value[key as keyof InputState] === 'boolean') &&
    Number.isFinite(value.yaw) && Math.abs(value.yaw) <= Math.PI * 10_000 && Number.isFinite(value.pitch) && Math.abs(value.pitch) <= 1.4;
}

function electedMap(room: Room): MapId {
  const votes = [...room.votes.values()];
  const delta = votes.filter((vote) => vote === 'delta').length;
  const terminal = votes.length - delta;
  if (delta === terminal) return room.votes.get(room.hostId) ?? 'delta';
  return terminal > delta ? 'terminal' : 'delta';
}

function beginRound(room: Room): void {
  if (room.matchEndsAt && Date.now() >= room.matchEndsAt) { finishMatch(room, 'Tiempo total agotado'); return; }
  room.round++;
  room.phase = 'playing';
  room.endsAt = Math.min(Date.now() + room.roundSeconds * 1000, room.matchEndsAt);
  room.nextAt = 0;
  room.announcement = `Ronda ${room.round}`;
  const slots = { intrusos: 0, custodios: 0 };
  for (const member of room.members) {
    if (!member.player) continue;
    const player = member.player;
    [player.x, player.y, player.z] = safeSpawn(MAPS[room.map], player.team, slots[player.team]++);
    player.yaw = player.team === 'intrusos' ? -Math.PI / 2 : Math.PI / 2;
    player.pitch = 0;
    player.hp = 100;
    member.input = { ...EMPTY_INPUT, yaw: player.yaw };
  }
  announce(room);
  broadcast(room, { type: 'snapshot', players: playersIn(room), at: Date.now() });
}

function finishMatch(room: Room, reason: string): void {
  room.phase = 'finished';
  room.endsAt = 0;
  room.nextAt = 0;
  room.winner = room.scores.intrusos === room.scores.custodios ? 'empate' : room.scores.intrusos > room.scores.custodios ? 'intrusos' : 'custodios';
  room.announcement = reason;
  announce(room);
}

function finishRound(room: Room, winner: TeamId | null, reason: string): void {
  if (room.phase !== 'playing') return;
  if (winner) room.scores[winner]++;
  room.endsAt = 0;
  room.announcement = reason;
  const maxRounds = room.targetScore * 2 - 1;
  const teamsPresent = new Set(playersIn(room).map((player) => player.team));
  if (room.scores.intrusos >= room.targetScore || room.scores.custodios >= room.targetScore || room.round >= maxRounds || teamsPresent.size < 2 || Date.now() >= room.matchEndsAt) {
    finishMatch(room, reason);
  } else {
    room.phase = 'intermission';
    room.nextAt = Date.now() + 4000;
    announce(room);
  }
}

function checkElimination(room: Room): void {
  if (room.phase !== 'playing') return;
  const players = playersIn(room);
  const intrusos = players.filter((player) => player.team === 'intrusos' && player.hp > 0).length;
  const custodios = players.filter((player) => player.team === 'custodios' && player.hp > 0).length;
  if (intrusos && custodios) return;
  const winner = intrusos ? 'intrusos' : custodios ? 'custodios' : null;
  finishRound(room, winner, winner ? `${winner.toUpperCase()} gana la ronda` : 'Ronda empatada');
}

function handleFire(member: Connection, message: Extract<ClientMessage, { type: 'fire' }>): void {
  const room = member.room;
  const shooter = member.player;
  if (room.phase !== 'playing' || !shooter || shooter.hp <= 0 || !Number.isSafeInteger(message.shotId)) return;
  if (message.shotId <= member.lastShotId) return;
  const now = Date.now();
  if (now - member.lastShot < 190) return;
  member.lastShot = now;
  member.lastShotId = message.shotId;
  const result = resolveShot(MAPS[room.map], shooter, playersIn(room));
  broadcast(room, { type: 'shot', shooterId: shooter.id, hitId: result.hitId, x: result.position[0], y: result.position[1], z: result.position[2], shotId: message.shotId });
  if (!result.hitId) return;
  const target = [...room.members].find((connection) => connection.player?.id === result.hitId)?.player;
  if (!target) return;
  target.hp = Math.max(0, target.hp - result.damage);
  if (target.hp === 0) {
    target.deaths++;
    shooter.kills++;
    broadcast(room, { type: 'elimination', killerId: shooter.id, victimId: target.id });
    checkElimination(room);
  }
}

server.on('connection', (socket, request) => {
  const url = new URL(request.url || '/', `http://${request.headers.host || 'localhost'}`);
  const code = (url.searchParams.get('room') || 'ALFA').toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 8) || 'ALFA';
  const room = roomFor(code);
  const member: Connection = { socket, room, player: null, input: { ...EMPTY_INPUT }, lastShot: 0, lastShotId: -1 };
  room.members.add(member);
  socket.on('message', (raw) => {
    let message: ClientMessage;
    try { message = JSON.parse(raw.toString()) as ClientMessage; } catch { return; }
    if (!message || typeof message !== 'object') return;
    if (message.type === 'join') handleJoin(member, message);
    else if (message.type === 'input' && room.phase === 'playing' && member.player && validInput(message.input)) member.input = message.input;
    else if (message.type === 'fire') handleFire(member, message);
    else if (message.type === 'vote' && room.phase === 'lobby' && member.player && (message.map === 'delta' || message.map === 'terminal')) {
      room.votes.set(member.player.id, message.map);
      announce(room);
    } else if (message.type === 'configure' && room.phase === 'lobby' && member.player?.id === room.hostId &&
      Number.isInteger(message.roundSeconds) && message.roundSeconds >= 60 && message.roundSeconds <= 300 &&
      Number.isInteger(message.matchMinutes) && message.matchMinutes >= 5 && message.matchMinutes <= 30 &&
      Number.isInteger(message.targetScore) && message.targetScore >= 1 && message.targetScore <= 9) {
      room.roundSeconds = message.roundSeconds;
      room.matchMinutes = message.matchMinutes;
      room.targetScore = message.targetScore;
      announce(room);
    } else if (message.type === 'start' && room.phase === 'lobby' && member.player?.id === room.hostId) {
      const teams = new Set(playersIn(room).map((player) => player.team));
      if (teams.size < 2) { send(member, { type: 'error', message: 'Se necesita al menos un jugador por equipo.' }); return; }
      room.map = electedMap(room);
      room.scores = { intrusos: 0, custodios: 0 };
      room.round = 0;
      room.winner = null;
      room.matchEndsAt = Date.now() + room.matchMinutes * 60_000;
      beginRound(room);
    } else if (message.type === 'rematch' && room.phase === 'finished' && member.player?.id === room.hostId) {
      room.phase = 'lobby';
      room.round = 0;
      room.scores = { intrusos: 0, custodios: 0 };
      room.votes.clear();
      room.winner = null;
      room.matchEndsAt = 0;
      room.announcement = 'Nueva votación de mapa';
      announce(room);
    }
  });
  const disconnect = () => {
    if (!room.members.delete(member)) return;
    if (member.player) room.votes.delete(member.player.id);
    if (!room.members.size) { rooms.delete(room.code); return; }
    if (member.player?.id === room.hostId) room.hostId = playersIn(room)[0]?.id ?? '';
    checkElimination(room);
    announce(room);
  };
  socket.on('close', disconnect);
  socket.on('error', disconnect);
});

let lastTick = performance.now();
setInterval(() => {
  const now = performance.now();
  const dt = Math.min((now - lastTick) / 1000, 0.07);
  lastTick = now;
  for (const room of rooms.values()) {
    if (room.phase === 'intermission' && Date.now() >= room.nextAt) beginRound(room);
    if (room.phase !== 'playing') continue;
    if (Date.now() >= room.matchEndsAt) { finishMatch(room, 'Tiempo total agotado'); continue; }
    if (Date.now() >= room.endsAt) {
      const players = playersIn(room);
      const intrusos = players.filter((player) => player.team === 'intrusos' && player.hp > 0).length;
      const custodios = players.filter((player) => player.team === 'custodios' && player.hp > 0).length;
      const winner = intrusos === custodios ? null : intrusos > custodios ? 'intrusos' : 'custodios';
      finishRound(room, winner, winner ? `${winner.toUpperCase()} gana por supervivencia` : 'Tiempo agotado: empate');
      continue;
    }
    for (const member of room.members) if (member.player) stepPlayer(MAPS[room.map], member.player, member.input, dt);
  }
}, 1000 / 30);

setInterval(() => {
  for (const room of rooms.values()) {
    if (room.phase === 'playing' || room.phase === 'intermission') {
      broadcast(room, { type: 'snapshot', players: playersIn(room), at: Date.now() });
    }
  }
}, 50);

server.on('listening', () => console.log(`Mantenimiento Strike escuchando en ws://0.0.0.0:${PORT}`));
