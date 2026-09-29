import { useEffect, useLayoutEffect, useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import type { CharacterId, GameMode, HitZone, PlayerState, TeamId } from '../../shared/world';

export interface HitReaction { id: string; zone: HitZone }

const STYLE: Record<CharacterId, { visor: string; body: string; shoulder: number; helmet: number }> = {
  kira: { visor: '#85d6c7', body: '#263c42', shoulder: 0.32, helmet: 0.38 },
  vektor: { visor: '#ffc481', body: '#353e47', shoulder: 0.39, helmet: 0.42 },
  atlas: { visor: '#d7e1e6', body: '#43494f', shoulder: 0.46, helmet: 0.46 },
};

interface PartSpec {
  position: [number, number, number];
  scale: [number, number, number];
  color: string;
}

function Parts({ specs }: { specs: PartSpec[] }) {
  const ref = useRef<THREE.InstancedMesh>(null);
  useLayoutEffect(() => {
    const mesh = ref.current;
    if (!mesh) return;
    const matrix = new THREE.Matrix4();
    const position = new THREE.Vector3();
    const scale = new THREE.Vector3();
    const rotation = new THREE.Quaternion();
    const color = new THREE.Color();
    specs.forEach((spec, index) => {
      position.set(...spec.position);
      scale.set(...spec.scale);
      mesh.setMatrixAt(index, matrix.compose(position, rotation, scale));
      mesh.setColorAt(index, color.set(spec.color));
    });
    mesh.instanceMatrix.needsUpdate = true;
    if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
  }, [specs]);
  return <instancedMesh ref={ref} args={[undefined, undefined, specs.length]} frustumCulled={false}>
    <boxGeometry args={[1, 1, 1]} />
    <meshStandardMaterial color="#ffffff" metalness={0.3} roughness={0.62} />
  </instancedMesh>;
}

function Tag({ name, team, solo }: { name: string; team: TeamId; solo: boolean }) {
  const texture = useMemo(() => {
    const canvas = document.createElement('canvas');
    canvas.width = 512;
    canvas.height = 96;
    const ctx = canvas.getContext('2d')!;
    ctx.fillStyle = solo ? '#b8c7a4' : team === 'intrusos' ? '#d99c56' : '#58c6bf';
    ctx.fillRect(0, 0, 512, 80);
    ctx.fillStyle = '#102026';
    ctx.font = 'bold 39px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(name.toUpperCase().slice(0, 18), 256, 54, 480);
    return new THREE.CanvasTexture(canvas);
  }, [name, team, solo]);
  useEffect(() => () => texture.dispose(), [texture]);
  return <sprite position={[0, 2.28, 0]} scale={[2.2, 0.42, 1]}>
    <spriteMaterial map={texture} transparent depthTest={false} />
  </sprite>;
}

export function Avatar({ character, team, name, position, yaw = 0, walking = false, label = true, reaction, dead = false, crouching = false, solo = false }: {
  character: CharacterId; team: TeamId; name: string; position: [number, number, number]; yaw?: number; walking?: boolean; label?: boolean;
  reaction?: HitReaction; dead?: boolean; crouching?: boolean; solo?: boolean;
}) {
  const group = useRef<THREE.Group>(null);
  const pose = useRef<THREE.Group>(null);
  const leftArm = useRef<THREE.Group>(null);
  const rightArm = useRef<THREE.Group>(null);
  const leftLeg = useRef<THREE.Group>(null);
  const rightLeg = useRef<THREE.Group>(null);
  const target = useMemo(() => new THREE.Vector3(), []);
  const hitMotion = useRef({ remaining: 0, zone: 'torso' as HitZone });
  const fall = useRef(0);
  useEffect(() => {
    if (reaction) hitMotion.current = { remaining: 0.4, zone: reaction.zone };
  }, [reaction?.id]);
  const variant = STYLE[character];
  const accent = solo ? '#a6bfa9' : team === 'intrusos' ? '#e8a34e' : '#55c7c3';

  const core = useMemo<PartSpec[]>(() => {
    const parts: PartSpec[] = [
      { position: [0, 0.99, 0], scale: [0.65, 0.73, 0.33], color: variant.body },
      { position: [0, 1.03, 0.19], scale: [0.52, 0.48, 0.13], color: accent },
      { position: [0, 1.32, 0.25], scale: [0.42, 0.1, 0.08], color: '#0e2026' },
      { position: [-0.23, 0.98, 0.26], scale: [0.09, 0.34, 0.07], color: '#17282e' },
      { position: [0.23, 0.98, 0.26], scale: [0.09, 0.34, 0.07], color: '#17282e' },
      { position: [0, 0.66, 0.1], scale: [0.67, 0.14, 0.39], color: '#17262b' },
      { position: [0, 0.96, -0.23], scale: [0.49, 0.52, 0.2], color: '#192b31' },
      { position: [0, 1.47, 0.29], scale: [0.45, 0.17, 0.17], color: '#151f26' },
      { position: [0, 1.7, -0.3], scale: [0.55, 0.16, 0.09], color: variant.visor },
      { position: [0, 1.7, 0.34], scale: [variant.helmet * 1.45, 0.16, 0.06], color: variant.visor },
      { position: [0.19, 1.01, -0.32], scale: [0.14, 0.2, 0.75], color: '#12191d' },
      { position: [0.19, 0.89, -0.15], scale: [0.12, 0.22, 0.13], color: '#252d31' },
    ];
    if (character === 'atlas') parts.push({ position: [0, 1.9, 0], scale: [0.56, 0.12, 0.56], color: '#677278' });
    if (character === 'vektor') parts.push({ position: [0.34, 1.66, 0], scale: [0.16, 0.28, 0.25], color: '#d3a75e' });
    if (character === 'kira') parts.push({ position: [0, 1.99, 0.12], scale: [0.1, 0.18, 0.17], color: '#5ecab9' });
    return parts;
  }, [accent, character, variant]);
  const armParts = useMemo<PartSpec[]>(() => [
    { position: [0, 0, 0], scale: [0.36, 0.3, 0.36], color: accent },
    { position: [0, -0.27, 0], scale: [0.19, 0.48, 0.22], color: '#26383d' },
    { position: [0, -0.5, -0.025], scale: [0.22, 0.18, 0.24], color: '#101f25' },
    { position: [0, -0.68, -0.03], scale: [0.14, 0.26, 0.16], color: '#687779' },
  ], [accent]);
  const legParts = useMemo<PartSpec[]>(() => [
    { position: [0, -0.19, 0], scale: [0.24, 0.39, 0.28], color: '#202d34' },
    { position: [0, -0.41, 0.15], scale: [0.25, 0.14, 0.11], color: accent },
    { position: [0, -0.53, 0], scale: [0.21, 0.23, 0.24], color: '#27363b' },
    { position: [0, -0.62, 0.12], scale: [0.29, 0.13, 0.45], color: '#10191e' },
  ], [accent]);

  useFrame(({ clock }, delta) => {
    if (!group.current) return;
    const distance = Math.hypot(group.current.position.x - position[0], group.current.position.z - position[2]);
    const moving = walking || (distance > 0.015 && distance < 3);
    const phase = clock.elapsedTime * 9;
    group.current.position.lerp(target.set(position[0], position[1], position[2]), Math.min(1, delta * 14));
    group.current.position.y += moving ? Math.abs(Math.sin(phase)) * 0.015 : 0;
    group.current.rotation.y = yaw;
    const swing = moving ? Math.sin(phase) * 0.42 : Math.sin(clock.elapsedTime * 1.8) * 0.012;
    if (leftArm.current) leftArm.current.rotation.x = -swing * 0.65 - 0.22;
    if (rightArm.current) rightArm.current.rotation.x = swing * 0.65 - 0.22;
    if (leftLeg.current) leftLeg.current.rotation.x = swing;
    if (rightLeg.current) rightLeg.current.rotation.x = -swing;
    if (pose.current) {
      pose.current.scale.y = THREE.MathUtils.damp(pose.current.scale.y, crouching ? 0.68 : 1, 15, delta);
      hitMotion.current.remaining = Math.max(0, hitMotion.current.remaining - delta);
      fall.current = THREE.MathUtils.damp(fall.current, dead ? 1 : 0, dead ? 5 : 12, delta);
      const pulse = Math.sin((1 - hitMotion.current.remaining / 0.4) * Math.PI) * (hitMotion.current.remaining > 0 ? 1 : 0);
      const zone = hitMotion.current.zone;
      pose.current.rotation.x = fall.current * 1.42 + pulse * (zone === 'head' ? -0.25 : zone === 'leg' ? 0.09 : -0.15);
      pose.current.rotation.z = pulse * (zone === 'arm' ? 0.2 : zone === 'head' ? 0.17 : 0.11);
      pose.current.position.y = -fall.current * 0.24 - pulse * (zone === 'leg' ? 0.14 : 0.025);
    }
  });

  return <group ref={group} position={position}>
    <group ref={pose}>
      <Parts specs={core} />
      {([-1, 1] as const).map((side) => <group key={`arm-${side}`} ref={side < 0 ? leftArm : rightArm} position={[side * (variant.shoulder + 0.08), 1.31, 0]}><Parts specs={armParts} /></group>)}
      {([-1, 1] as const).map((side) => <group key={`leg-${side}`} ref={side < 0 ? leftLeg : rightLeg} position={[side * 0.18, 0.65, 0]}><Parts specs={legParts} /></group>)}
      <mesh position={[0, 1.68, 0]}>
        <sphereGeometry args={[variant.helmet, 16, 10]} />
        <meshStandardMaterial color="#243138" metalness={0.45} roughness={0.54} />
      </mesh>
    </group>
    {label && !dead && <Tag name={name} team={team} solo={solo} />}
  </group>;
}

export function RemoteAvatar({ player, reaction, mode }: { player: PlayerState; reaction?: HitReaction; mode: GameMode }) {
  return <Avatar character={player.character} team={player.team} name={player.name}
    position={[player.x, player.y, player.z]} yaw={player.yaw} reaction={reaction} dead={player.hp <= 0}
    crouching={player.crouching} solo={mode === 'ffa'} />;
}
