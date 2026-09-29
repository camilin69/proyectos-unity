import type { ArenaMap, Solid } from '../../shared/world';

function Block({ x, y, z, w, h, d, color, metalness = 0.25 }: {
  x: number; y: number; z: number; w: number; h: number; d: number; color: string; metalness?: number;
}) {
  return <mesh castShadow receiveShadow position={[x, y, z]}>
    <boxGeometry args={[w, h, d]} />
    <meshStandardMaterial color={color} roughness={0.72} metalness={metalness} />
  </mesh>;
}

function Obstacle({ solid, accent }: { solid: Solid; accent: string }) {
  const { x, z, w, d, h, kind } = solid;
  const baseY = solid.y ?? 0;
  if (kind === 'roof') return <group>
    <Block x={x} y={baseY + h / 2} z={z} w={w} h={h} d={d} color="#23393e" metalness={0.6} />
    <Block x={x} y={baseY + h + 0.05} z={z} w={w + 0.16} h={0.1} d={d + 0.16} color={accent} />
  </group>;
  if (kind === 'container') return <group>
    <Block x={x} y={baseY + h / 2} z={z} w={w} h={h} d={d} color="#526270" metalness={0.55} />
    {Array.from({ length: 7 }, (_, i) => <Block key={i} x={x - w / 2 + (i + 0.5) * w / 7} y={baseY + h / 2} z={z - d / 2 - 0.035} w={0.08} h={h - 0.25} d={0.08} color="#293d45" metalness={0.65} />)}
    {Array.from({ length: 7 }, (_, i) => <Block key={`back-${i}`} x={x - w / 2 + (i + 0.5) * w / 7} y={baseY + h / 2} z={z + d / 2 + 0.035} w={0.08} h={h - 0.25} d={0.08} color="#293d45" metalness={0.65} />)}
    <Block x={x - w / 2 + 0.1} y={baseY + h / 2} z={z} w={0.16} h={h + 0.08} d={d + 0.16} color="#203139" />
    <Block x={x + w / 2 - 0.1} y={baseY + h / 2} z={z} w={0.16} h={h + 0.08} d={d + 0.16} color="#203139" />
    <Block x={x} y={baseY + h - 0.23} z={z - d / 2 - 0.05} w={w - 0.3} h={0.13} d={0.11} color={accent} />
  </group>;
  if (kind === 'crate') return <group>
    <Block x={x} y={baseY + h / 2} z={z} w={w} h={h} d={d} color="#655d50" />
    <Block x={x} y={baseY + h - 0.12} z={z} w={w + 0.14} h={0.16} d={d + 0.14} color="#a49370" />
    <Block x={x - w / 2 + 0.1} y={baseY + h / 2} z={z - d / 2 - 0.04} w={0.17} h={h} d={0.12} color="#293237" />
    <Block x={x + w / 2 - 0.1} y={baseY + h / 2} z={z - d / 2 - 0.04} w={0.17} h={h} d={0.12} color="#293237" />
    <Block x={x} y={baseY + 0.17} z={z - d / 2 - 0.04} w={w} h={0.16} d={0.12} color="#293237" />
    <Block x={x} y={baseY + h / 2} z={z - d / 2 - 0.045} w={w - 0.3} h={0.08} d={0.13} color="#b5a37e" />
    <Block x={x} y={baseY + 0.12} z={z} w={w - 0.38} h={0.15} d={d - 0.38} color="#20272b" />
  </group>;
  if (kind === 'hideout') return <group>
    <Block x={x} y={baseY + h / 2} z={z} w={w} h={h} d={d} color="#2d434a" metalness={0.55} />
    <Block x={x} y={baseY + h - 0.16} z={z} w={w + 0.12} h={0.18} d={d + 0.12} color={accent} />
    <Block x={x} y={baseY + 0.16} z={z} w={w + 0.14} h={0.25} d={d + 0.14} color="#17262d" />
  </group>;
  if (kind === 'pillar') return <group>
    <Block x={x} y={baseY + h / 2} z={z} w={w} h={h} d={d} color="#657277" metalness={0.4} />
    <Block x={x} y={baseY + 0.65} z={z} w={w + 0.04} h={0.22} d={d + 0.04} color={accent} />
  </group>;
  return <group>
    <Block x={x} y={baseY + h / 2} z={z} w={w} h={h} d={d} color="#48575e" metalness={0.3} />
    <Block x={x} y={baseY + h - 0.3} z={z} w={w + 0.06} h={0.08} d={d + 0.06} color="#172b32" />
  </group>;
}

function EnvironmentalDetails({ map }: { map: ArenaMap }) {
  const isDepot = map.id === 'delta';
  return <>
    {Array.from({ length: 7 }, (_, i) => <group key={`beam-${i}`}>
      <Block x={-map.width / 2 + 5 + i * 9} y={6.8} z={0} w={0.22} h={0.25} d={map.depth - 1.5} color="#304249" metalness={0.7} />
      <Block x={-map.width / 2 + 5 + i * 9} y={6.4} z={-map.depth / 2 + 4} w={2.6} h={0.08} d={0.38} color="#a7d8d6" metalness={0.3} />
      <Block x={-map.width / 2 + 5 + i * 9} y={6.4} z={map.depth / 2 - 4} w={2.6} h={0.08} d={0.38} color="#a7d8d6" metalness={0.3} />
    </group>)}
    {Array.from({ length: 9 }, (_, i) => <group key={`floor-${i}`}>
      <Block x={-map.width / 2 + (i + 1) * map.width / 10} y={0.004} z={0} w={0.035} h={0.008} d={map.depth - 1.8} color="#6b7370" metalness={0.1} />
    </group>)}
    {[-1, 1].map((side) => <group key={side}>
      <Block x={0} y={0.012} z={side * (map.depth / 2 - 2)} w={map.width - 2} h={0.025} d={0.1} color={map.accent} />
      <Block x={0} y={3.3} z={side * (map.depth / 2 - 0.45)} w={map.width - 1.5} h={0.12} d={0.08} color="#78898a" metalness={0.6} />
    </group>)}
    {isDepot ? <>
      {[-10, 10].map((track) => <group key={track}>
        <Block x={0} y={0.025} z={track - 0.72} w={map.width - 4} h={0.05} d={0.12} color="#a4aaa5" metalness={0.75} />
        <Block x={0} y={0.025} z={track + 0.72} w={map.width - 4} h={0.05} d={0.12} color="#a4aaa5" metalness={0.75} />
        {Array.from({ length: 15 }, (_, i) => <Block key={i} x={-map.width / 2 + 3 + i * 4} y={0.018} z={track} w={0.24} h={0.036} d={2} color="#806c50" />)}
      </group>)}
      {[-1, 1].map((side) => <group key={`hook-${side}`}>
        <Block x={side * 2} y={5.7} z={0} w={0.08} h={2} d={0.08} color="#c0a36d" />
        <Block x={side * 2} y={4.8} z={0} w={0.9} h={0.18} d={0.2} color="#e6b666" />
      </group>)}
    </> : <>
      {[-14, 0, 14].map((lane) => <group key={lane}>
        <Block x={0} y={0.017} z={lane} w={map.width - 4} h={0.035} d={0.14} color="#75c8c0" />
        {Array.from({ length: 8 }, (_, i) => <Block key={i} x={-map.width / 2 + 5 + i * 8} y={0.02} z={lane + 1.2} w={2.5} h={0.04} d={0.18} color="#a3a8a6" />)}
      </group>)}
      {[-1, 1].map((side) => <group key={`terminal-${side}`}>
        <Block x={side * 27} y={2.8} z={0} w={0.12} h={1.8} d={2.8} color="#385962" />
        <Block x={side * 27.07} y={2.8} z={0} w={0.06} h={1.3} d={2.3} color="#80c8c6" />
        <Block x={side * 27} y={3.7} z={0} w={0.2} h={0.18} d={3} color="#d9eee6" />
      </group>)}
    </>}
  </>;
}

export function World({ map }: { map: ArenaMap }) {
  return <>
    <color attach="background" args={[map.fog]} />
    <fog attach="fog" args={[map.fog, 24, 82]} />
    <hemisphereLight intensity={1.7} color="#c7e4e5" groundColor="#435258" />
    <ambientLight intensity={0.65} />
    <directionalLight position={[11, 19, 8]} intensity={2.7} color="#cfdee0" />
    <pointLight position={[-21, 6, -14]} intensity={20} distance={16} color={map.accent} />
    <pointLight position={[21, 6, 14]} intensity={20} distance={16} color="#7ed9da" />
    <Block x={0} y={-0.22} z={0} w={map.width} h={0.42} d={map.depth} color={map.ground} />
    <EnvironmentalDetails map={map} />
    <Block x={0} y={2.5} z={-map.depth / 2} w={map.width} h={5} d={0.9} color="#23383f" />
    <Block x={0} y={2.5} z={map.depth / 2} w={map.width} h={5} d={0.9} color="#23383f" />
    <Block x={-map.width / 2} y={2.5} z={0} w={0.9} h={5} d={map.depth} color="#23383f" />
    <Block x={map.width / 2} y={2.5} z={0} w={0.9} h={5} d={map.depth} color="#23383f" />
    {map.solids.map((solid) => <Obstacle key={solid.id} solid={solid} accent={map.accent} />)}
    {map.stairs.map((stair) => <group key={stair.id}>
      {Array.from({ length: 12 }, (_, i) => {
        const progress = stair.direction === 1 ? i : 11 - i;
        const x = stair.x - stair.w / 2 + (i + 0.5) * stair.w / 12;
        const h = stair.h * (progress + 1) / 12;
        return <Block key={i} x={x} y={h / 2} z={stair.z} w={stair.w / 12 + 0.012} h={h} d={stair.d} color={i % 2 ? '#647579' : '#536268'} metalness={0.5} />;
      })}
      <Block x={stair.x} y={0.18} z={stair.z - stair.d / 2 - 0.07} w={stair.w} h={0.18} d={0.14} color={map.accent} />
    </group>)}
    {map.platforms.map((platform) => <group key={platform.id}>
      <Block x={platform.x} y={platform.h - 0.14} z={platform.z} w={platform.w} h={0.28} d={platform.d} color="#6c7a7d" metalness={0.58} />
      {Array.from({ length: 7 }, (_, i) => <Block key={i} x={platform.x - platform.w / 2 + (i + 0.5) * platform.w / 7} y={platform.h / 2} z={platform.z} w={0.13} h={platform.h - 0.3} d={0.13} color="#40575d" />)}
      {[-1, 1].map((side) => <group key={side}>
        <Block x={platform.x} y={platform.h + 0.9} z={platform.z + side * (platform.d / 2 - 0.1)} w={platform.w} h={0.13} d={0.12} color="#829b9b" />
        {Array.from({ length: 5 }, (_, i) => <Block key={i} x={platform.x - platform.w / 2 + (i + 0.5) * platform.w / 5} y={platform.h + 0.46} z={platform.z + side * (platform.d / 2 - 0.1)} w={0.12} h={0.87} d={0.12} color="#829b9b" />)}
      </group>)}
    </group>)}
    {Array.from({ length: 7 }, (_, i) => <group key={i}>
      <mesh position={[-map.width / 2 + 4 + i * 9, 4.3, -map.depth / 2 + 0.5]} rotation={[0, 0, Math.PI / 2]}>
        <cylinderGeometry args={[0.16, 0.16, 4.2, 10]} />
        <meshStandardMaterial color="#788991" metalness={0.8} roughness={0.45} />
      </mesh>
      <mesh position={[-map.width / 2 + 4 + i * 9, 3.9, -map.depth / 2 + 1.1]}>
        <boxGeometry args={[1.6, 0.09, 0.12]} />
        <meshStandardMaterial color={map.accent} emissive={map.accent} emissiveIntensity={1.4} />
      </mesh>
    </group>)}
  </>;
}
