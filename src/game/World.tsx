import { memo, useLayoutEffect, useMemo, useRef } from 'react';
import * as THREE from 'three';
import type { ArenaMap, Solid } from '../../shared/world';

type Finish = 'matte' | 'metal' | 'light';

interface BoxSpec {
  x: number; y: number; z: number;
  w: number; h: number; d: number;
  color: string;
  finish: Finish;
}

function buildWorld(map: ArenaMap): Record<Finish, BoxSpec[]> {
  const boxes: Record<Finish, BoxSpec[]> = { matte: [], metal: [], light: [] };
  const add = (x: number, y: number, z: number, w: number, h: number, d: number, color: string, finish: Finish = 'matte') => {
    boxes[finish].push({ x, y, z, w, h, d, color, finish });
  };

  add(0, -0.22, 0, map.width, 0.42, map.depth, map.ground);
  add(0, 2.5, -map.depth / 2, map.width, 5, 0.9, '#23383f');
  add(0, 2.5, map.depth / 2, map.width, 5, 0.9, '#23383f');
  add(-map.width / 2, 2.5, 0, 0.9, 5, map.depth, '#23383f');
  add(map.width / 2, 2.5, 0, 0.9, 5, map.depth, '#23383f');

  const obstacle = (solid: Solid) => {
    const { x, z, w, d, h, kind } = solid;
    const y = solid.y ?? 0;
    if (kind === 'roof') {
      add(x, y + h / 2, z, w, h, d, '#23393e', 'metal');
      add(x, y + h + 0.05, z, w + 0.16, 0.1, d + 0.16, map.accent, 'light');
    } else if (kind === 'container') {
      add(x, y + h / 2, z, w, h, d, '#526270', 'metal');
      for (let i = 0; i < 7; i++) {
        const ribX = x - w / 2 + (i + 0.5) * w / 7;
        add(ribX, y + h / 2, z - d / 2 - 0.035, 0.08, h - 0.25, 0.08, '#293d45', 'metal');
        add(ribX, y + h / 2, z + d / 2 + 0.035, 0.08, h - 0.25, 0.08, '#293d45', 'metal');
      }
      add(x - w / 2 + 0.1, y + h / 2, z, 0.16, h + 0.08, d + 0.16, '#203139', 'metal');
      add(x + w / 2 - 0.1, y + h / 2, z, 0.16, h + 0.08, d + 0.16, '#203139', 'metal');
      add(x, y + h - 0.23, z - d / 2 - 0.05, w - 0.3, 0.13, 0.11, map.accent, 'light');
    } else if (kind === 'crate') {
      add(x, y + h / 2, z, w, h, d, '#655d50');
      add(x, y + h - 0.12, z, w + 0.14, 0.16, d + 0.14, '#a49370');
      add(x - w / 2 + 0.1, y + h / 2, z - d / 2 - 0.04, 0.17, h, 0.12, '#293237', 'metal');
      add(x + w / 2 - 0.1, y + h / 2, z - d / 2 - 0.04, 0.17, h, 0.12, '#293237', 'metal');
      add(x, y + 0.17, z - d / 2 - 0.04, w, 0.16, 0.12, '#293237', 'metal');
      add(x, y + h / 2, z - d / 2 - 0.045, w - 0.3, 0.08, 0.13, '#b5a37e');
      add(x, y + 0.12, z, w - 0.38, 0.15, d - 0.38, '#20272b');
    } else if (kind === 'hideout') {
      add(x, y + h / 2, z, w, h, d, '#2d434a', 'metal');
      add(x, y + h - 0.16, z, w + 0.12, 0.18, d + 0.12, map.accent, 'light');
      add(x, y + 0.16, z, w + 0.14, 0.25, d + 0.14, '#17262d', 'metal');
    } else if (kind === 'pillar') {
      add(x, y + h / 2, z, w, h, d, '#657277', 'metal');
      add(x, y + 0.65, z, w + 0.04, 0.22, d + 0.04, map.accent, 'light');
    } else {
      add(x, y + h / 2, z, w, h, d, '#48575e');
      add(x, y + h - 0.3, z, w + 0.06, 0.08, d + 0.06, '#172b32', 'metal');
    }
  };
  map.solids.forEach(obstacle);

  for (const stair of map.stairs) {
    for (let i = 0; i < 12; i++) {
      const progress = stair.direction === 1 ? i : 11 - i;
      const x = stair.x - stair.w / 2 + (i + 0.5) * stair.w / 12;
      const h = stair.h * (progress + 1) / 12;
      add(x, h / 2, stair.z, stair.w / 12 + 0.012, h, stair.d, i % 2 ? '#647579' : '#536268', 'metal');
    }
    add(stair.x, 0.18, stair.z - stair.d / 2 - 0.07, stair.w, 0.18, 0.14, map.accent, 'light');
  }
  for (const platform of map.platforms) {
    add(platform.x, platform.h - 0.14, platform.z, platform.w, 0.28, platform.d, '#6c7a7d', 'metal');
    for (let i = 0; i < 7; i++) add(platform.x - platform.w / 2 + (i + 0.5) * platform.w / 7, platform.h / 2, platform.z, 0.13, platform.h - 0.3, 0.13, '#40575d', 'metal');
    for (const side of [-1, 1]) {
      const edgeZ = platform.z + side * (platform.d / 2 - 0.1);
      add(platform.x, platform.h + 0.9, edgeZ, platform.w, 0.13, 0.12, '#829b9b', 'metal');
      for (let i = 0; i < 5; i++) add(platform.x - platform.w / 2 + (i + 0.5) * platform.w / 5, platform.h + 0.46, edgeZ, 0.12, 0.87, 0.12, '#829b9b', 'metal');
    }
  }

  for (let i = 0; i < 7; i++) {
    const beamX = -map.width / 2 + 5 + i * 9;
    add(beamX, 6.8, 0, 0.22, 0.25, map.depth - 1.5, '#304249', 'metal');
    add(beamX, 6.4, -map.depth / 2 + 4, 2.6, 0.08, 0.38, '#a7d8d6', 'light');
    add(beamX, 6.4, map.depth / 2 - 4, 2.6, 0.08, 0.38, '#a7d8d6', 'light');
    add(-map.width / 2 + 4 + i * 9, 4.3, -map.depth / 2 + 0.5, 4.2, 0.32, 0.32, '#788991', 'metal');
    add(-map.width / 2 + 4 + i * 9, 3.9, -map.depth / 2 + 1.1, 1.6, 0.09, 0.12, map.accent, 'light');
  }
  for (let i = 0; i < 9; i++) add(-map.width / 2 + (i + 1) * map.width / 10, 0.004, 0, 0.035, 0.008, map.depth - 1.8, '#6b7370');
  for (const side of [-1, 1]) {
    add(0, 0.012, side * (map.depth / 2 - 2), map.width - 2, 0.025, 0.1, map.accent, 'light');
    add(0, 3.3, side * (map.depth / 2 - 0.45), map.width - 1.5, 0.12, 0.08, '#78898a', 'metal');
  }
  if (map.id === 'delta') {
    for (const track of [-10, 10]) {
      add(0, 0.025, track - 0.72, map.width - 4, 0.05, 0.12, '#a4aaa5', 'metal');
      add(0, 0.025, track + 0.72, map.width - 4, 0.05, 0.12, '#a4aaa5', 'metal');
      for (let i = 0; i < 15; i++) add(-map.width / 2 + 3 + i * 4, 0.018, track, 0.24, 0.036, 2, '#806c50');
    }
    for (const side of [-1, 1]) {
      add(side * 2, 5.7, 0, 0.08, 2, 0.08, '#c0a36d', 'metal');
      add(side * 2, 4.8, 0, 0.9, 0.18, 0.2, '#e6b666', 'metal');
    }
  } else {
    for (const lane of [-14, 0, 14]) {
      add(0, 0.017, lane, map.width - 4, 0.035, 0.14, '#75c8c0', 'light');
      for (let i = 0; i < 8; i++) add(-map.width / 2 + 5 + i * 8, 0.02, lane + 1.2, 2.5, 0.04, 0.18, '#a3a8a6');
    }
    for (const side of [-1, 1]) {
      add(side * 27, 2.8, 0, 0.12, 1.8, 2.8, '#385962', 'metal');
      add(side * 27.07, 2.8, 0, 0.06, 1.3, 2.3, '#80c8c6', 'light');
      add(side * 27, 3.7, 0, 0.2, 0.18, 3, '#d9eee6', 'light');
    }
  }
  return boxes;
}

function Batch({ specs, finish }: { specs: BoxSpec[]; finish: Finish }) {
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
      position.set(spec.x, spec.y, spec.z);
      scale.set(spec.w, spec.h, spec.d);
      matrix.compose(position, rotation, scale);
      mesh.setMatrixAt(index, matrix);
      mesh.setColorAt(index, color.set(spec.color));
    });
    mesh.instanceMatrix.needsUpdate = true;
    if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
  }, [specs]);
  return <instancedMesh ref={ref} args={[undefined, undefined, specs.length]} frustumCulled={false}>
    <boxGeometry args={[1, 1, 1]} />
    {finish === 'light'
      ? <meshBasicMaterial color="#ffffff" />
      : <meshStandardMaterial color="#ffffff" roughness={finish === 'metal' ? 0.48 : 0.76} metalness={finish === 'metal' ? 0.58 : 0.12} />}
  </instancedMesh>;
}

export const World = memo(function World({ map }: { map: ArenaMap }) {
  const boxes = useMemo(() => buildWorld(map), [map]);
  return <>
    <color attach="background" args={[map.fog]} />
    <fog attach="fog" args={[map.fog, 24, 82]} />
    <hemisphereLight intensity={2.0} color="#c7e4e5" groundColor="#435258" />
    <directionalLight position={[11, 19, 8]} intensity={2.7} color="#cfdee0" />
    <Batch specs={boxes.matte} finish="matte" />
    <Batch specs={boxes.metal} finish="metal" />
    <Batch specs={boxes.light} finish="light" />
  </>;
});
