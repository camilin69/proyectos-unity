import { Suspense, useEffect, useMemo, useRef } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import * as THREE from 'three';
import { MAPS, type GameMode, type MapId, type PlayerState } from '../../shared/world';
import { Avatar, RemoteAvatar, type HitReaction } from './Avatar';
import { World } from './World';

export interface VisualShot {
  id: string;
  shooterId: string;
  from: [number, number, number];
  to: [number, number, number];
  hit: boolean;
}

function CameraRig({ player, yaw, pitch, damageFlash }: { player: PlayerState | undefined; yaw: number; pitch: number; damageFlash: number }) {
  const { camera } = useThree();
  const target = useMemo(() => new THREE.Vector3(), []);
  const shake = useRef(0);
  useEffect(() => { if (damageFlash) shake.current = 0.2; }, [damageFlash]);
  useFrame((_, delta) => {
    if (!player) return;
    camera.position.lerp(target.set(player.x, player.y + (player.crouching ? 1.06 : 1.58), player.z), Math.min(1, delta * 18));
    camera.rotation.set(pitch, yaw, 0, 'YXZ');
    if (shake.current > 0) {
      camera.rotateZ(Math.sin(shake.current * 65) * shake.current * 0.13);
      shake.current = Math.max(0, shake.current - delta);
    }
  });
  return null;
}

function PerformanceProbe() {
  const sample = useRef({ frames: 0, seconds: 0, calls: 0, triangles: 0 });
  useFrame(({ gl }, delta) => {
    sample.current.frames++;
    sample.current.seconds += delta;
    sample.current.calls += gl.info.render.calls;
    sample.current.triangles += gl.info.render.triangles;
    if (sample.current.seconds < 1) return;
    const { frames, seconds, calls, triangles } = sample.current;
    (window as Window & { __strikePerf?: { fps: number; drawCalls: number; triangles: number } }).__strikePerf = {
      fps: Math.round(frames / seconds),
      drawCalls: Math.round(calls / frames),
      triangles: Math.round(triangles / frames),
    };
    sample.current = { frames: 0, seconds: 0, calls: 0, triangles: 0 };
  });
  return null;
}

function ViewWeapon({ character, fireToken, damageFlash }: { character: PlayerState['character']; fireToken?: string; damageFlash: number }) {
  const { camera } = useThree();
  const group = useRef<THREE.Group>(null);
  const recoil = useRef(0);
  const flinch = useRef(0);
  useEffect(() => { if (fireToken) recoil.current = 0.16; }, [fireToken]);
  useEffect(() => { if (damageFlash) flinch.current = 0.22; }, [damageFlash]);
  useFrame(({ clock }, delta) => {
    if (!group.current) return;
    recoil.current = Math.max(0, recoil.current - delta);
    flinch.current = Math.max(0, flinch.current - delta);
    const kick = Math.sin((recoil.current / 0.16) * Math.PI) * 0.09;
    const hurt = Math.sin((flinch.current / 0.22) * Math.PI) * 0.08;
    group.current.position.set(0.31 + hurt, -0.31 - kick + Math.sin(clock.elapsedTime * 2) * 0.004, -0.58 + kick * 1.7);
    group.current.rotation.set(-0.04 + kick * 2.2, -0.08, 0.02 + hurt);
  });
  const color = character === 'kira' ? '#528d8d' : character === 'vektor' ? '#b18150' : '#889299';
  return <primitive object={camera}>
    <group ref={group}>
      <mesh position={[0.02, -0.12, 0.15]} rotation={[-0.18, 0, 0]}>
        <boxGeometry args={[0.21, 0.34, 0.16]} />
        <meshStandardMaterial color={color} />
      </mesh>
      <mesh position={[-0.06, 0, -0.15]}>
        <boxGeometry args={[0.22, 0.17, 0.58]} />
        <meshStandardMaterial color="#1c252a" metalness={0.72} roughness={0.32} />
      </mesh>
      <mesh position={[-0.06, 0.12, -0.34]}>
        <boxGeometry args={[0.13, 0.04, 0.21]} />
        <meshStandardMaterial color="#81989c" metalness={0.9} roughness={0.3} />
      </mesh>
      <mesh position={[-0.06, 0, -0.49]} rotation={[Math.PI / 2, 0, 0]}>
        <cylinderGeometry args={[0.065, 0.065, 0.23, 12]} />
        <meshStandardMaterial color="#0e161a" metalness={0.8} />
      </mesh>
    </group>
  </primitive>;
}

function Tracer({ shot }: { shot: VisualShot }) {
  const beam = useRef<THREE.Group>(null);
  const flash = useRef<THREE.Mesh>(null);
  const impact = useRef<THREE.Group>(null);
  const age = useRef(0);
  const { from, to, direction, length, rotation } = useMemo(() => {
    const source = new THREE.Vector3(...shot.from);
    const to = new THREE.Vector3(...shot.to);
    const aim = to.clone().sub(source).normalize();
    const right = new THREE.Vector3(-aim.z, 0, aim.x).normalize();
    const from = source.addScaledVector(aim, 0.45).addScaledVector(right, 0.2);
    from.y -= 0.16;
    const vector = to.clone().sub(from);
    const length = vector.length();
    const direction = vector.normalize();
    const rotation = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), direction);
    return { from, to, direction, length, rotation };
  }, [shot.from, shot.to]);
  useFrame((_, delta) => {
    age.current += delta;
    const travelled = Math.min(length, age.current * 190);
    const tail = Math.max(0, travelled - 2.7);
    if (beam.current) {
      beam.current.visible = travelled > tail && age.current < length / 190 + 0.06;
      beam.current.position.copy(from).addScaledVector(direction, (travelled + tail) / 2);
      beam.current.quaternion.copy(rotation);
      beam.current.scale.y = Math.max(0.01, travelled - tail);
    }
    if (flash.current) {
      flash.current.visible = age.current < 0.075;
      flash.current.scale.setScalar(Math.max(0.01, 1 - age.current / 0.075));
    }
    if (impact.current) {
      const sinceImpact = age.current - length / 190;
      impact.current.visible = sinceImpact >= 0 && sinceImpact < 0.24;
      impact.current.scale.setScalar(0.25 + Math.max(0, sinceImpact) * 4);
    }
  });
  return <group>
    <group ref={beam} visible={false}>
      <mesh><cylinderGeometry args={[0.014, 0.014, 1, 6]} /><meshBasicMaterial color="#fff8cf" toneMapped={false} /></mesh>
      <mesh><cylinderGeometry args={[0.05, 0.05, 1, 6]} /><meshBasicMaterial color="#ffb654" transparent opacity={0.25} depthWrite={false} blending={THREE.AdditiveBlending} toneMapped={false} /></mesh>
    </group>
    <mesh ref={flash} position={from} visible={false}><sphereGeometry args={[0.18, 8, 6]} /><meshBasicMaterial color="#ffe3a0" transparent opacity={0.8} depthWrite={false} blending={THREE.AdditiveBlending} toneMapped={false} /></mesh>
    <group ref={impact} position={to} quaternion={rotation} visible={false}>
      <mesh rotation={[Math.PI / 2, 0, 0]}><torusGeometry args={[0.17, 0.026, 5, 16]} /><meshBasicMaterial color={shot.hit ? '#ff6654' : '#ffd291'} transparent opacity={0.86} depthWrite={false} toneMapped={false} /></mesh>
      <mesh><sphereGeometry args={[0.07, 8, 6]} /><meshBasicMaterial color={shot.hit ? '#ff8a6f' : '#fff0bb'} transparent opacity={0.9} depthWrite={false} toneMapped={false} /></mesh>
    </group>
  </group>;
}

export function GameScene({ mapId, mode, players, ownId, yaw, pitch, shots, reactions, damageFlash }: {
  mapId: MapId; mode: GameMode; players: PlayerState[]; ownId: string; yaw: number; pitch: number; shots: VisualShot[];
  reactions: Record<string, HitReaction>; damageFlash: number;
}) {
  const own = players.find((player) => player.id === ownId);
  const ownShot = shots.filter((shot) => shot.shooterId === ownId).at(-1)?.id;
  return <Canvas dpr={1} camera={{ fov: 72, near: 0.04, far: 110, position: [0, 1.6, 0] }} gl={{ antialias: true }}>
    <Suspense fallback={null}>
      <World map={MAPS[mapId]} />
      {players.filter((player) => player.id !== ownId).map((player) => <RemoteAvatar key={player.id} player={player} reaction={reactions[player.id]} mode={mode} />)}
      <CameraRig player={own} yaw={yaw} pitch={pitch} damageFlash={damageFlash} />
      {import.meta.env.DEV && <PerformanceProbe />}
      {own && own.hp > 0 && <ViewWeapon character={own.character} fireToken={ownShot} damageFlash={damageFlash} />}
      {shots.map((shot) => <Tracer key={shot.id} shot={shot} />)}
    </Suspense>
  </Canvas>;
}

export function CharacterPreview({ character }: { character: PlayerState['character'] }) {
  return <Canvas camera={{ position: [0, 1.15, 4.3], fov: 43 }} onCreated={({ camera }) => camera.lookAt(0, 1.05, 0)} dpr={1} frameloop="demand">
    <color attach="background" args={['#132329']} />
    <ambientLight intensity={1.1} />
    <directionalLight position={[3, 6, 4]} color="#ffd5a0" intensity={2.5} />
    <pointLight position={[-3, 2, -2]} color="#6ad7d6" intensity={12} />
    <mesh position={[0, -0.06, 0]} rotation={[-Math.PI / 2, 0, 0]}>
      <circleGeometry args={[1.2, 48]} />
      <meshStandardMaterial color="#263b40" />
    </mesh>
    <PreviewTurn character={character} />
  </Canvas>;
}

function PreviewTurn({ character }: { character: PlayerState['character'] }) {
  return <group rotation={[0, 0.28, 0]}>
    <Avatar character={character} team="intrusos" name="" position={[0, 0, 0]} label={false} />
  </group>;
}
