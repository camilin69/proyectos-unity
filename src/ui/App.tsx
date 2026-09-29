import { useCallback, useEffect, useRef, useState } from 'react';
import { CHARACTER_IDS, EMPTY_INPUT, MAPS, MAX_TARGET_SCORE, type CharacterId, type ClientMessage, type GameMode, type InputState, type LobbyState, type MapId, type PlayerState, type ServerMessage, type TeamId } from '../../shared/world';
import { CharacterPreview, GameScene, type VisualShot } from '../game/GameScene';
import type { HitReaction } from '../game/Avatar';
import './lobby.css';
import '../game/effects.css';

type Phase = 'menu' | 'connecting' | 'lobby' | 'playing' | 'finished' | 'error';

const CHARACTER_INFO: Record<CharacterId, { label: string; role: string; description: string; code: string }> = {
  kira: { label: 'KIRA', role: 'RECONOCIMIENTO', description: 'Perfil ágil. Visor turquesa y equipo ligero.', code: '01' },
  vektor: { label: 'VEKTOR', role: 'ASALTO', description: 'Armadura de campo y señal ámbar.', code: '02' },
  atlas: { label: 'ATLAS', role: 'CONTENCIÓN', description: 'Silueta robusta y casco reforzado.', code: '03' },
};
const TARGET_SCORE_OPTIONS = Array.from({ length: MAX_TARGET_SCORE }, (_, index) => index + 1);

function socketUrl(code: string): string {
  const specified = import.meta.env.VITE_WS_URL as string | undefined;
  const root = specified || `${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.hostname}:2567`;
  return `${root.replace(/\/$/, '')}/?room=${encodeURIComponent(code)}`;
}

export function App() {
  const [phase, setPhase] = useState<Phase>('menu');
  const [alias, setAlias] = useState('Operador');
  const [character, setCharacter] = useState<CharacterId>('kira');
  const [mapId, setMapId] = useState<MapId>('delta');
  const [roomCode, setRoomCode] = useState(() => new URLSearchParams(location.search).get('room')?.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 8) || Math.random().toString(36).slice(2, 6).toUpperCase());
  const [lobby, setLobby] = useState<LobbyState | null>(null);
  const [now, setNow] = useState(Date.now());
  const [ownId, setOwnId] = useState('');
  const [players, setPlayers] = useState<PlayerState[]>([]);
  const [error, setError] = useState('');
  const [locked, setLocked] = useState(false);
  const [fullscreen, setFullscreen] = useState(false);
  const [sprintActive, setSprintActive] = useState(false);
  const [shots, setShots] = useState<VisualShot[]>([]);
  const [reactions, setReactions] = useState<Record<string, HitReaction>>({});
  const [damageFlash, setDamageFlash] = useState(0);
  const [hit, setHit] = useState(false);
  const [feed, setFeed] = useState('');
  const [look, setLook] = useState({ yaw: -Math.PI / 2, pitch: 0 });
  const socket = useRef<WebSocket | null>(null);
  const gameArea = useRef<HTMLDivElement>(null);
  const input = useRef<InputState>({ ...EMPTY_INPUT });
  const desiredConfig = useRef({ roundSeconds: 120, matchMinutes: 15, targetScore: 3, mode: 'teams' as GameMode });
  const shotCounter = useRef(0);

  const send = useCallback((message: ClientMessage) => {
    if (socket.current?.readyState === WebSocket.OPEN) socket.current.send(JSON.stringify(message));
  }, []);

  const leave = useCallback(() => {
    document.exitPointerLock?.();
    if (gameArea.current && document.fullscreenElement === gameArea.current) void document.exitFullscreen();
    socket.current?.close();
    socket.current = null;
    input.current = { ...EMPTY_INPUT };
    setSprintActive(false);
    setPlayers([]);
    setLobby(null);
    setOwnId('');
    setPhase('menu');
  }, []);

  const connect = useCallback(() => {
    setError('');
    setPhase('connecting');
    const ws = new WebSocket(socketUrl(roomCode));
    socket.current = ws;
    ws.onopen = () => send({ type: 'join', name: alias, character });
    ws.onmessage = (event) => {
      let message: ServerMessage;
      try { message = JSON.parse(event.data) as ServerMessage; } catch { return; }
      if (message.type === 'welcome') {
        setOwnId(message.id);
        const yaw = message.team === 'intrusos' ? -Math.PI / 2 : Math.PI / 2;
        input.current.yaw = yaw;
        input.current.pitch = 0;
        setLook({ yaw, pitch: 0 });
        setPhase('lobby');
        send({ type: 'vote', map: mapId });
      } else if (message.type === 'lobby') {
        setLobby(message.state);
        desiredConfig.current = { roundSeconds: message.state.roundSeconds, matchMinutes: message.state.matchMinutes, targetScore: message.state.targetScore, mode: message.state.mode };
        setPlayers(message.state.players);
        setMapId(message.state.map);
        if (message.state.phase === 'playing') {
          const self = message.state.players.find((player) => player.id === ownIdRef.current);
          if (self) {
            input.current.yaw = self.yaw;
            input.current.pitch = self.pitch;
            setLook({ yaw: self.yaw, pitch: self.pitch });
          }
        }
        setPhase(message.state.phase === 'lobby' ? 'lobby' : message.state.phase === 'finished' ? 'finished' : 'playing');
      } else if (message.type === 'snapshot') {
        setPlayers(message.players);
      } else if (message.type === 'shot') {
        const key = `${message.shooterId}-${message.shotId}`;
        setShots((current) => [...current.slice(-7), { id: key, shooterId: message.shooterId, from: message.from, to: [message.x, message.y, message.z], hit: !!message.hitId }]);
        window.setTimeout(() => setShots((current) => current.filter((shot) => shot.id !== key)), 420);
        const { hitId, zone, remainingHp } = message;
        if (hitId && zone && remainingHp !== null) {
          setPlayers((current) => current.map((player) => player.id === hitId ? { ...player, hp: remainingHp } : player));
          setReactions((current) => ({ ...current, [hitId]: { id: key, zone } }));
          if (hitId === ownIdRef.current) setDamageFlash((current) => current + 1);
        }
        if (message.shooterId === ownIdRef.current && message.hitId) {
          setHit(true);
          window.setTimeout(() => setHit(false), 170);
        }
      } else if (message.type === 'elimination') {
        const killer = playersRef.current.find((p) => p.id === message.killerId)?.name || 'Operador';
        const victim = playersRef.current.find((p) => p.id === message.victimId)?.name || 'Operador';
        setFeed(`${killer} eliminó a ${victim}`);
        window.setTimeout(() => setFeed(''), 3000);
      } else if (message.type === 'error') {
        setError(message.message);
        if (!ownIdRef.current) setPhase('error');
      }
    };
    ws.onerror = () => { setError('No se pudo conectar al servidor. Ejecuta npm run dev.'); setPhase('error'); };
    ws.onclose = () => {
      if (socket.current === ws) {
        socket.current = null;
        setError('Se perdió la conexión con la sala.');
        setPhase('error');
      }
    };
  }, [alias, character, mapId, roomCode, send]);

  useEffect(() => {
    if (phase === 'menu' || phase === 'error') return;
    const timer = window.setInterval(() => setNow(Date.now()), 250);
    return () => window.clearInterval(timer);
  }, [phase]);

  const playersRef = useRef(players);
  const ownIdRef = useRef(ownId);
  useEffect(() => { playersRef.current = players; }, [players]);
  useEffect(() => { ownIdRef.current = ownId; }, [ownId]);

  useEffect(() => {
    if (phase !== 'playing') return;
    const keys: Record<string, keyof Pick<InputState, 'forward' | 'back' | 'left' | 'right' | 'crouch' | 'sprint' | 'jump'>> = {
      KeyW: 'forward', KeyS: 'back', KeyA: 'left', KeyD: 'right',
      KeyF: 'sprint', ShiftLeft: 'crouch', ShiftRight: 'crouch', Space: 'jump',
    };
    const onKey = (event: KeyboardEvent) => {
      const action = keys[event.code];
      if (action) {
        input.current[action] = event.type === 'keydown';
        event.preventDefault();
        if (action === 'sprint') setSprintActive(input.current.sprint);
        if (action === 'jump' && event.type === 'keydown' && !event.repeat) send({ type: 'input', input: { ...input.current } });
      }
    };
    const onLook = (event: MouseEvent) => {
      if (document.pointerLockElement !== gameArea.current) return;
      input.current.yaw -= event.movementX * 0.0022;
      input.current.pitch = Math.max(-1.25, Math.min(1.25, input.current.pitch - event.movementY * 0.0022));
      setLook({ yaw: input.current.yaw, pitch: input.current.pitch });
    };
    const onLock = () => setLocked(document.pointerLockElement === gameArea.current);
    const onBlur = () => {
      for (const key of Object.values(keys)) input.current[key] = false;
      setSprintActive(false);
    };
    window.addEventListener('keydown', onKey);
    window.addEventListener('keyup', onKey);
    window.addEventListener('mousemove', onLook);
    window.addEventListener('blur', onBlur);
    document.addEventListener('pointerlockchange', onLock);
    const timer = window.setInterval(() => send({ type: 'input', input: { ...input.current } }), 50);
    return () => {
      window.clearInterval(timer);
      window.removeEventListener('keydown', onKey);
      window.removeEventListener('keyup', onKey);
      window.removeEventListener('mousemove', onLook);
      window.removeEventListener('blur', onBlur);
      document.removeEventListener('pointerlockchange', onLock);
    };
  }, [phase, send]);

  useEffect(() => {
    const onFullscreenChange = () => setFullscreen(!!gameArea.current && document.fullscreenElement === gameArea.current);
    document.addEventListener('fullscreenchange', onFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', onFullscreenChange);
  }, []);

  const toggleFullscreen = async () => {
    try {
      if (gameArea.current && document.fullscreenElement === gameArea.current) await document.exitFullscreen();
      else await gameArea.current?.requestFullscreen();
    } catch { setFullscreen(false); }
  };

  const own = players.find((player) => player.id === ownId);
  const team = own?.team ?? '';
  const mode = lobby?.mode ?? 'teams';
  const leader = [...players].sort((a, b) => b.kills - a.kills)[0];
  const teamCounts = { intrusos: players.filter((player) => player.team === 'intrusos').length, custodios: players.filter((player) => player.team === 'custodios').length };
  const canStart = players.length >= 2 && (mode === 'ffa' || (teamCounts.intrusos > 0 && teamCounts.custodios > 0));
  const winnerName = lobby?.winnerId ? players.find((player) => player.id === lobby.winnerId)?.name : null;
  const host = lobby?.hostId === ownId;
  const secondsLeft = lobby?.endsAt ? Math.max(0, Math.ceil((lobby.endsAt - now) / 1000)) : 0;
  const minuteClock = `${Math.floor(secondsLeft / 60).toString().padStart(2, '0')}:${(secondsLeft % 60).toString().padStart(2, '0')}`;
  const matchSecondsLeft = lobby?.matchEndsAt ? Math.max(0, Math.ceil((lobby.matchEndsAt - now) / 1000)) : 0;
  const matchClock = `${Math.floor(matchSecondsLeft / 60).toString().padStart(2, '0')}:${(matchSecondsLeft % 60).toString().padStart(2, '0')}`;

  if ((phase === 'lobby' || phase === 'finished') && lobby) return <main className="menu-shell lobby-shell">
    <div className="menu-grid" />
    <header className="topbar"><span className="logo-mark">M<span>／</span>S</span><span className="topbar-right">SALA {lobby.code} <b>● {phase === 'finished' ? 'RESULTADO' : 'LOBBY'}</b></span></header>
    <div className="lobby-content">
      <section className="lobby-lead">
        <div className="eyebrow">OPERACIÓN MULTIJUGADOR // SALA {lobby.code}</div>
        <h1>{phase === 'finished' ? 'FIN DE LA' : 'PREPARA LA'}<br /><em>{phase === 'finished' ? 'PARTIDA' : 'OPERACIÓN'}</em></h1>
        <p>{phase === 'finished' ? (lobby.winner === 'empate' ? 'La partida terminó en empate.' : mode === 'ffa' ? `Ganó ${winnerName ?? 'un operador'}.` : `Ganó ${lobby.winner?.toUpperCase()}.`) : 'Comparte el código, voten el mapa y elijan cómo competir.'}</p>
        <div className="room-code"><span>CÓDIGO DE SALA</span><strong>{lobby.code}</strong><button onClick={() => navigator.clipboard?.writeText(lobby.code)}>COPIAR CÓDIGO</button></div>
        {phase === 'lobby' && <p className="lan-note">En otro computador, abre la IP LAN de este equipo en el puerto 5173 e ingresa el código.</p>}
        <div className="lobby-score">{mode === 'ffa' ? <><span>TODOS CONTRA TODOS</span><i>·</i><span>PRIMERO A <b>{lobby.targetScore}</b> BAJAS</span></> : <><span>INTRUSOS <b>{lobby.scores.intrusos}</b></span><i>:</i><span><b>{lobby.scores.custodios}</b> CUSTODIOS</span></>}</div>
      </section>
      <section className="setup-panel lobby-panel">
        <div className="panel-head"><span>{phase === 'finished' ? 'RESULTADO DE LA PARTIDA' : 'VOTACIÓN Y CONFIGURACIÓN'}</span><strong>{lobby.players.length} / 10</strong></div>
        <div className="field-label">PARTICIPANTES <span>{host ? 'ERES ANFITRIÓN' : 'ANFITRIÓN: ' + (lobby.players.find((p) => p.id === lobby.hostId)?.name ?? '—')}</span></div>
        <div className="lobby-roster">{[...lobby.players].sort((a, b) => mode === 'ffa' ? b.kills - a.kills : 0).map((player) => <div key={player.id} className="lobby-member"><span>{mode === 'ffa' ? '◈' : player.team === 'intrusos' ? '◆' : '◇'}</span><strong>{player.name}{player.id === ownId ? ' (TÚ)' : ''}</strong><small>{mode === 'ffa' ? `${player.kills} BAJAS · ${player.deaths} MUERTES` : player.team.toUpperCase()}{player.id === lobby.hostId ? ' · HOST' : ''}</small></div>)}</div>
        {phase === 'lobby' ? <>
          {mode === 'teams' ? <><div className="field-label map-label">ELIGE TU EQUIPO <span>Máximo cinco por equipo</span></div>
            <div className="team-row">{(['intrusos', 'custodios'] as TeamId[]).map((choice) => <button key={choice} className={`team-option ${team === choice ? 'selected' : ''}`} aria-pressed={team === choice} disabled={team !== choice && teamCounts[choice] >= 5} onClick={() => { setError(''); send({ type: 'selectTeam', team: choice }); }}><strong>{choice.toUpperCase()}</strong><span>{teamCounts[choice]} / 5</span></button>)}</div></> : <p className="setup-note">Cada jugador combate por su cuenta. Una baja da un punto y reapareces tras tres segundos.</p>}
          <div className="field-label map-label">VOTA POR EL ESCENARIO <span>Un voto por jugador</span></div>
          <div className="map-row">{(Object.keys(MAPS) as MapId[]).map((id) => <button key={id} className={`map-option ${lobby.playerVotes[ownId] === id ? 'selected' : ''}`} onClick={() => send({ type: 'vote', map: id })}><strong>{MAPS[id].name}</strong><span>{lobby.votes[id]} VOTOS · {MAPS[id].subtitle}</span></button>)}</div>
          <div className="lobby-settings">
            <label>MODO DE JUEGO<select value={lobby.mode} disabled={!host} onChange={(event) => { desiredConfig.current.mode = event.target.value as GameMode; send({ type: 'configure', ...desiredConfig.current }); }}><option value="teams">POR EQUIPOS</option><option value="ffa">TODOS CONTRA TODOS</option></select></label>
            {mode === 'teams' && <label>DURACIÓN DE RONDA<select value={lobby.roundSeconds} disabled={!host} onChange={(event) => { desiredConfig.current.roundSeconds = Number(event.target.value); send({ type: 'configure', ...desiredConfig.current }); }}>{[60, 90, 120, 180, 300].map((value) => <option key={value} value={value}>{Math.floor(value / 60)}:{(value % 60).toString().padStart(2, '0')} MIN</option>)}</select></label>}
            <label>DURACIÓN DE PARTIDA<select value={lobby.matchMinutes} disabled={!host} onChange={(event) => { desiredConfig.current.matchMinutes = Number(event.target.value); send({ type: 'configure', ...desiredConfig.current }); }}>{[5, 10, 15, 20, 30].map((value) => <option key={value} value={value}>{value} MIN</option>)}</select></label>
            <label>PUNTOS PARA GANAR<select value={lobby.targetScore} disabled={!host} onChange={(event) => { desiredConfig.current.targetScore = Number(event.target.value); send({ type: 'configure', ...desiredConfig.current }); }}>{TARGET_SCORE_OPTIONS.map((value) => <option key={value} value={value}>{value} {value === 1 ? 'PUNTO' : 'PUNTOS'}</option>)}</select></label>
          </div>
          {host ? <><button className="deploy-button" disabled={!canStart} onClick={() => send({ type: 'start' })}>INICIAR PARTIDA <span>↗</span></button>{!canStart && <p className="setup-note">{mode === 'ffa' ? 'Se necesitan al menos dos jugadores.' : 'Se necesita al menos una persona por equipo.'}</p>}</> : <p className="setup-note">Esperando a que el anfitrión inicie la partida.</p>}
        </> : <>
          <p className="result-note">{lobby.announcement}{mode === 'teams' ? ` · ${lobby.round} ${lobby.round === 1 ? 'RONDA' : 'RONDAS'} JUGADAS` : ''}</p>
          {host ? <button className="deploy-button" onClick={() => send({ type: 'rematch' })}>NUEVA VOTACIÓN <span>↗</span></button> : <p className="setup-note">El anfitrión puede abrir una revancha.</p>}
        </>}
        {error && <div className="error-banner" role="alert">{error}</div>}
        <button className="text-exit" onClick={leave}>SALIR DE LA SALA ×</button>
      </section>
    </div>
  </main>;

  if (phase !== 'playing') return <main className="menu-shell">
    <div className="menu-grid" />
    <header className="topbar"><span className="logo-mark">M<span>／</span>S</span><span className="topbar-right">OPERACIÓN MULTIJUGADOR <b>● EN DESARROLLO</b></span></header>
    <div className="menu-content">
      <section className="intro">
        <div className="eyebrow">TACTICAL WEBGL // BUILD 001</div>
        <h1>MANTENIMIENTO<br /><em>STRIKE</em></h1>
        <p>Un complejo. Dos equipos o todos contra todos. Cada ángulo cuenta.</p>
        <div className="intro-rule" />
        <div className="intro-mini"><span>01</span><span>ELIGE OPERADOR</span><span>02</span><span>ENTRA A LA SALA</span><span>03</span><span>CONTROLA EL SECTOR</span></div>
      </section>
      <section className="setup-panel">
        <div className="panel-head"><span>CONFIGURACIÓN DE DESPLIEGUE</span><strong>01 / 03</strong></div>
        <label className="field-label" htmlFor="alias">ALIAS DE OPERADOR</label>
        <input id="alias" className="alias-input" maxLength={18} value={alias} onChange={(event) => setAlias(event.target.value)} placeholder="Tu alias" />
        <div className="field-label character-label">SELECCIONA PERSONAJE <span>Aspecto visual · mismas estadísticas</span></div>
        <div className="character-row">
          {CHARACTER_IDS.map((id) => <button key={id} className={`character-option ${character === id ? 'selected' : ''}`} onClick={() => setCharacter(id)}>
            <small>{CHARACTER_INFO[id].code}</small><strong>{CHARACTER_INFO[id].label}</strong><span>{CHARACTER_INFO[id].role}</span>
          </button>)}
        </div>
        <div className="preview-box"><CharacterPreview character={character} /><div className="preview-overlay"><span>MODELO WEBGL // {CHARACTER_INFO[character].role}</span><strong>{CHARACTER_INFO[character].label}</strong><p>{CHARACTER_INFO[character].description}</p></div></div>
        <div className="field-label map-label">PREFERENCIA INICIAL DE MAPA</div>
        <div className="map-row">{(Object.keys(MAPS) as MapId[]).map((id) => <button key={id} className={`map-option ${mapId === id ? 'selected' : ''}`} onClick={() => setMapId(id)}><strong>{MAPS[id].name}</strong><span>{MAPS[id].subtitle}</span></button>)}</div>
        <label className="field-label map-label" htmlFor="room-code">CÓDIGO DE SALA <span>Compártelo para jugar desde otra máquina</span></label>
        <input id="room-code" className="alias-input" maxLength={8} value={roomCode} onChange={(event) => setRoomCode(event.target.value.toUpperCase().replace(/[^A-Z0-9]/g, ''))} />
        <button className="deploy-button" onClick={connect} disabled={phase === 'connecting'}>{phase === 'connecting' ? 'CONECTANDO…' : 'ENTRAR A LA SALA'} <span>↗</span></button>
        {phase === 'error' && <div className="error-banner" role="alert">{error}</div>}
        <p className="setup-note">Entra con el mismo código desde otra máquina para compartir sala y votar el mapa.</p>
      </section>
    </div>
    <footer className="menu-footer"><span>WASD MOVER · RATÓN MIRAR · CLIC DISPARAR · F CORRER · SHIFT AGACHARSE · ESPACIO SALTAR</span><span>PROTOCOLO / 001</span></footer>
  </main>;

  return <div className="game-shell" ref={gameArea} onPointerDown={(event) => {
    if ((event.target as HTMLElement).closest('button')) return;
    if (document.pointerLockElement !== gameArea.current) gameArea.current?.requestPointerLock();
    else if (event.button === 0 && lobby?.phase === 'playing' && own && own.hp > 0) send({ type: 'fire', shotId: ++shotCounter.current, yaw: input.current.yaw, pitch: input.current.pitch });
  }}>
    <GameScene mapId={lobby?.map ?? mapId} mode={mode} players={players} ownId={ownId} yaw={look.yaw} pitch={look.pitch} shots={shots} reactions={reactions} damageFlash={damageFlash} />
    <div className="game-vignette" />
    {damageFlash > 0 && <div key={damageFlash} className="damage-flash" />}
    <div className="hud-top"><div className="hud-brand"><b>M/S</b><span>{MAPS[lobby?.map ?? mapId].name}<small>SALA {lobby?.code} · {mode === 'ffa' ? 'TODOS CONTRA TODOS' : `RONDA ${lobby?.round} · ${team.toUpperCase()}`}</small></span></div><div className="hud-scores">{mode === 'ffa' ? <><span>LÍDER {leader?.name ?? '—'} · {leader?.kills ?? 0}</span><i>{matchClock}<small>PRIMERO A {lobby?.targetScore}</small></i><span>TÚ · {own?.kills ?? 0} BAJAS</span></> : <><span>INTRUSOS {lobby?.scores.intrusos ?? 0}</span><i>{lobby?.phase === 'playing' ? minuteClock : 'PAUSA'} <small>TOTAL {matchClock}</small></i><span>{lobby?.scores.custodios ?? 0} CUSTODIOS</span></>}</div><div className="hud-actions"><button onClick={toggleFullscreen}>{fullscreen ? 'SALIR PANTALLA' : 'PANTALLA COMPLETA'}</button><button onClick={leave}>SALIR ×</button></div></div>
    <div className="hud-roster">{[...players].sort((a, b) => mode === 'ffa' ? b.kills - a.kills : 0).map((player) => <div key={player.id} className={`roster-player ${mode === 'teams' && player.team === team ? 'ally' : 'enemy'} ${player.hp <= 0 ? 'down' : ''}`}><span>{mode === 'ffa' ? '◈' : player.team === team ? '◆' : '◇'}</span><strong>{player.name}{player.id === ownId ? ' (TÚ)' : ''}</strong><small>{mode === 'ffa' ? `${player.kills} / ${player.deaths}` : CHARACTER_INFO[player.character].label}</small></div>)}</div>
    {feed && <div className="kill-feed">{feed}</div>}
    <div className={`crosshair ${hit ? 'hit' : ''}`}><i /><i /><i /><i /></div>
    {lobby?.phase === 'intermission' ? <div className="game-prompt"><strong>{lobby.announcement}</strong><span>Siguiente ronda en {Math.max(0, Math.ceil((lobby.nextAt - now) / 1000))} s</span></div> : !locked && <div className="game-prompt"><strong>HAZ CLIC PARA JUGAR</strong><span>WASD mover · Mantén F para correr · Shift agacharse · Espacio saltar · Clic disparar · ESC libera cursor</span></div>}
    {own?.hp === 0 && lobby?.phase === 'playing' && <div className="death-overlay"><strong>ELIMINADO</strong><span>{mode === 'ffa' ? 'Reaparecerás en tres segundos' : 'Espera a la siguiente ronda'}</span></div>}
    <div className="hud-bottom"><div className="hud-health"><small>SALUD</small><strong>{own?.hp ?? 100}</strong><div className="health-track"><span style={{ width: `${own?.hp ?? 100}%` }} /></div></div><div className="hud-center">{CHARACTER_INFO[character].label}<span>{sprintActive ? 'CORRIENDO' : 'OPERADOR ACTIVO'} · F PARA CORRER</span></div><div className="hud-weapon"><small>ARMA DE PRUEBA</small><strong>RIFLE / ∞</strong><span>Servidor valida impactos y cadencia</span></div></div>
  </div>;
}
