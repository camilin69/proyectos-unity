import { Suspense, useMemo, useRef } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import * as THREE from 'three';
import { MAPS, type MapId, type PlayerState } from '../../shared/world';
import { Avatar, RemoteAvatar } from './Avatar';
import { World } from './World';

export interface VisualShot {
  id: string;
  from: [number, number, number];
  to: [number, number, number];
}

function CameraRig({ player, yaw, pitch }: { player: PlayerState | undefined; yaw: number; pitch: number }) {
  const { camera } = useThree();
  const target = useMemo(() => new THREE.Vector3(), []);
  useFrame((_, delta) => {
    if (!player) return;
    camera.position.lerp(target.set(player.x, player.y + 1.58, player.z), Math.min(1, delta * 18));
    camera.rotation.set(pitch, yaw, 0, 'YXZ');
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

function ViewWeapon({ character }: { character: PlayerState['character'] }) {
  const { camera } = useThree();
  const group = useRef<THREE.Group>(null);
  useFrame(({ clock }) => {
    if (!group.current) return;
    group.current.position.set(0.31, -0.31 + Math.sin(clock.elapsedTime * 2) * 0.004, -0.58);
    group.current.rotation.set(-0.04, -0.08, 0.02);
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
  const from = new THREE.Vector3(...shot.from);
  const to = new THREE.Vector3(...shot.to);
  const mid = from.clone().add(to).multiplyScalar(0.5);
  const length = from.distanceTo(to);
  const rotation = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), to.clone().sub(from).normalize());
  return <mesh position={mid} quaternion={rotation}>
    <cylinderGeometry args={[0.013, 0.013, length, 6]} />
    <meshBasicMaterial color="#ffe4a4" transparent opacity={0.82} />
  </mesh>;
}

export function GameScene({ mapId, players, ownId, yaw, pitch, shots }: {
  mapId: MapId; players: PlayerState[]; ownId: string; yaw: number; pitch: number; shots: VisualShot[];
}) {
  const own = players.find((player) => player.id === ownId);
  return <Canvas dpr={1} camera={{ fov: 72, near: 0.04, far: 110, position: [0, 1.6, 0] }} gl={{ antialias: true }}>
    <Suspense fallback={null}>
      <World map={MAPS[mapId]} />
      {players.filter((player) => player.id !== ownId && player.hp > 0).map((player) => <RemoteAvatar key={player.id} player={player} />)}
      <CameraRig player={own} yaw={yaw} pitch={pitch} />
      {import.meta.env.DEV && <PerformanceProbe />}
      {own && own.hp > 0 && <ViewWeapon character={own.character} />}
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
