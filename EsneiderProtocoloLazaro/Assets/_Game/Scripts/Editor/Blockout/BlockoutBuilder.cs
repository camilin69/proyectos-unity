using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Esneider.Core.Data;
using Esneider.World;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Esneider.EditorTools
{
    // Genera el blockout de las seis plantas y tres conectores (sección 68) a partir de bunker_plan.json.
    // Rasteriza cada planta en celdas de 0.2 m: libre (habitación/circulación/escalera/vano), sólido (muro/estructura) o nada.
    public static class BlockoutBuilder
    {
        public const string ScenePath = "Assets/_Game/Scenes/Bunker_Blockout.unity";
        const float Cell = 0.2f;
        const float SlabThickness = 0.2f;
        const float DoorDepth = 0.6f; // profundidad del vano hacia fuera del borde (cubre muro 0.2/0.4)

        enum C : byte { None, Free, Solid }

        static Material _matFloor, _matSolid, _matStairs, _matLintel, _matPillar, _matExterior;

        [MenuItem("Esneider/Blockout/Build from bunker_plan.json")]
        public static void BuildMenu() => Build(LevelPlan.DefaultAssetPath, ScenePath);

        public static string Build(string planPath, string scenePath)
        {
            var plan = LevelPlan.FromJson(File.ReadAllText(planPath));
            var report = DataValidator.ValidatePlan(plan);
            Debug.Log(report.ToString());
            if (!report.Passed) return "Plano inválido:\n" + report;

            EnsureMaterials();
            var scene = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);
            var stats = new Dictionary<string, int>();
            var world = new GameObject("World");

            foreach (var f in plan.floors) BuildFloor(plan, f, world.transform, stats);
            foreach (var c in plan.connectors) BuildConnector(plan, c, world.transform, stats);
            BuildMarkers(plan, world.transform, stats);

            var light = GameObject.Find("Directional Light");
            if (light != null) light.transform.rotation = Quaternion.Euler(60, 30, 0);

            Directory.CreateDirectory(Path.GetDirectoryName(scenePath));
            EditorSceneManager.SaveScene(scene, scenePath);
            var summary = string.Join(", ", stats.OrderBy(k => k.Key).Select(k => $"{k.Key}={k.Value}"));
            Debug.Log("Blockout generado: " + summary);
            return summary;
        }

        // ---------- plantas ----------
        static void BuildFloor(LevelPlan plan, PlanFloor f, Transform parent, Dictionary<string, int> stats)
        {
            var root = new GameObject($"{f.id}_{f.sector}").transform;
            root.SetParent(parent);
            root.position = f.origin.ToVector3();
            var geo = new GameObject("Geometry").transform; geo.SetParent(root, false);

            float env = plan.envelopeWallThickness, wall = plan.wallThickness;
            var ext = plan.exterior != null && plan.exterior.space == f.id ? plan.exterior : null;
            float minX = -env, minZ = -env, maxX = f.w + env, maxZ = f.d + env;
            if (ext != null) { maxX = Mathf.Max(maxX, ext.x + ext.w); maxZ = Mathf.Max(maxZ, ext.z + ext.d); minZ = Mathf.Min(minZ, ext.z); }
            var grid = new Grid(minX, minZ, maxX, maxZ);

            // 1) por defecto: dentro de la envolvente = sólido (estructura), banda perimetral = sólido, fuera = nada
            grid.Fill(-env, -env, f.w + env, f.d + env, C.Solid);

            // 2) superficies libres
            foreach (var r in plan.rooms.Where(x => x.floor == f.id)) grid.Fill(r.x, r.z, r.x + r.w, r.z + r.d, C.Free);
            foreach (var c in plan.circulation.Where(x => x.floor == f.id)) grid.Fill(c.x, c.z, c.x + c.w, c.z + c.d, C.Free);
            foreach (var s in plan.stairs.Where(x => x.lowerFloor == f.id || x.upperFloor == f.id)) grid.Fill(s.x, s.z, s.x + s.w, s.z + s.d, C.Free);
            if (ext != null) grid.Fill(ext.x, ext.z, ext.x + ext.w, ext.z + ext.d, C.Free);

            // 3) muros de habitación (0.2 m hacia fuera) vuelven a ser sólidos aunque toquen circulación
            foreach (var r in plan.rooms.Where(x => x.floor == f.id))
            {
                grid.Fill(r.x - wall, r.z - wall, r.x + r.w + wall, r.z, C.Solid);                 // sur
                grid.Fill(r.x - wall, r.z + r.d, r.x + r.w + wall, r.z + r.d + wall, C.Solid);     // norte
                grid.Fill(r.x - wall, r.z, r.x, r.z + r.d, C.Solid);                               // oeste
                grid.Fill(r.x + r.w, r.z, r.x + r.w + wall, r.z + r.d, C.Solid);                   // este
            }

            // 4) vanos de puerta: libres a ambos lados del borde
            foreach (var d in plan.doors.Where(x => x.floor == f.id))
            {
                DoorRect(d, out float x0, out float z0, out float x1, out float z1);
                grid.Fill(x0, z0, x1, z1, C.Free);
            }

            // Sólidos (muros + estructura) hasta la altura útil
            int solids = 0;
            foreach (var b in grid.Merge(C.Solid))
            {
                MakeBox(geo, "Solid", _matSolid, b, 0, f.height); solids++;
            }
            stats["solid_" + f.id] = solids;

            // Losa de suelo: todo lo que no es nada, menos el hueco de escaleras que suben desde la planta inferior
            var slab = grid.Clone();
            foreach (var s in plan.stairs.Where(x => x.upperFloor == f.id)) slab.Fill(s.x, s.z, s.x + s.w, s.z + s.d, C.None);
            int slabs = 0;
            foreach (var b in slab.MergeAny()) { MakeBox(geo, "Floor", ext != null && b.x0 >= f.w ? _matExterior : _matFloor, b, -SlabThickness, 0); slabs++; }
            stats["floor_" + f.id] = slabs;

            // Techo: envolvente sin el hueco de escaleras que suben a la planta superior; sin techo en exterior
            var ceil = new Grid(-env, -env, f.w + env, f.d + env);
            ceil.Fill(-env, -env, f.w + env, f.d + env, C.Free);
            foreach (var s in plan.stairs.Where(x => x.lowerFloor == f.id)) ceil.Fill(s.x, s.z, s.x + s.w, s.z + s.d, C.None);
            foreach (var d in plan.doors.Where(x => x.floor == f.id && string.IsNullOrEmpty(x.room)))
            {
                // puertas frontera: hueco en el techo sobre el vano no hace falta; se conserva techo
            }
            foreach (var b in ceil.MergeAny()) MakeBox(geo, "Ceiling", _matSolid, b, f.height, f.height + SlabThickness);

            // Dinteles: cierran el vano por encima de la altura de puerta
            foreach (var d in plan.doors.Where(x => x.floor == f.id))
            {
                DoorRect(d, out float x0, out float z0, out float x1, out float z1);
                if (d.height < f.height) MakeBox(geo, "Lintel_" + d.id, _matLintel, new Box(x0, z0, x1, z1), d.height, f.height);
            }

            // Escaleras cuya base está en esta planta
            foreach (var s in plan.stairs.Where(x => x.lowerFloor == f.id)) BuildStairs(s, geo);

            // Pilares de arena
            foreach (var p in plan.pillars.Where(x => x.space == f.id))
                MakeBox(geo, p.id, _matPillar, new Box(p.x - p.size / 2, p.z - p.size / 2, p.x + p.size / 2, p.z + p.size / 2), 0, f.height);
        }

        static void DoorRect(PlanDoor d, out float x0, out float z0, out float x1, out float z1)
        {
            float half = d.width / 2f;
            switch (d.edge)
            {
                case "E": x0 = d.x - DoorDepth; x1 = d.x + DoorDepth; z0 = d.z - half; z1 = d.z + half; break;
                case "W": x0 = d.x - DoorDepth; x1 = d.x + DoorDepth; z0 = d.z - half; z1 = d.z + half; break;
                case "N": z0 = d.z - DoorDepth; z1 = d.z + DoorDepth; x0 = d.x - half; x1 = d.x + half; break;
                default: z0 = d.z - DoorDepth; z1 = d.z + DoorDepth; x0 = d.x - half; x1 = d.x + half; break;
            }
        }

        // ---------- escaleras como rampas de colisión (68.3) ----------
        static void BuildStairs(PlanStairs s, Transform geo)
        {
            var root = new GameObject(s.id).transform; root.SetParent(geo, false);
            bool alongZ = s.axis != "x";
            float axisLen = alongZ ? s.d : s.w;
            float crossLen = alongZ ? s.w : s.d;
            float axis0 = alongZ ? s.z : s.x;
            float cross0 = alongZ ? s.x : s.z;
            float landing = 1f;
            float run = axisLen - 2 * landing;
            float rise = s.rise / s.flights;
            float lane = crossLen / s.flights;
            int dir = s.startDir == 0 ? 1 : s.startDir;

            for (int i = 0; i < s.flights; i++)
            {
                float h0 = i * rise, h1 = (i + 1) * rise;
                float c0 = cross0 + i * lane + 0.1f, c1 = cross0 + (i + 1) * lane - 0.1f;
                float a0 = dir > 0 ? axis0 + landing : axis0 + landing + run; // inicio del tramo
                float a1 = dir > 0 ? axis0 + landing + run : axis0 + landing; // fin del tramo
                float length = Mathf.Sqrt(run * run + rise * rise);
                float angle = Mathf.Atan2(rise, run) * Mathf.Rad2Deg;
                var go = GameObject.CreatePrimitive(PrimitiveType.Cube);
                go.name = $"{s.id}_Flight{i + 1}";
                go.transform.SetParent(root, false);
                float mid = (a0 + a1) / 2f, midC = (c0 + c1) / 2f, midH = (h0 + h1) / 2f - 0.15f;
                if (alongZ)
                {
                    go.transform.localPosition = new Vector3(midC, midH, mid);
                    go.transform.localRotation = Quaternion.Euler(dir > 0 ? -angle : angle, 0, 0);
                    go.transform.localScale = new Vector3(c1 - c0, 0.3f, length);
                }
                else
                {
                    go.transform.localPosition = new Vector3(mid, midH, midC);
                    go.transform.localRotation = Quaternion.Euler(0, 0, dir > 0 ? angle : -angle);
                    go.transform.localScale = new Vector3(length, 0.3f, c1 - c0);
                }
                go.GetComponent<MeshRenderer>().sharedMaterial = _matStairs;
                go.isStatic = true;

                // descansillo al final del tramo, ancho completo
                float la0 = dir > 0 ? axis0 + landing + run : axis0;
                float la1 = la0 + landing;
                var box = alongZ ? new Box(cross0, la0, cross0 + crossLen, la1) : new Box(la0, cross0, la1, cross0 + crossLen);
                MakeBox(root, $"{s.id}_Landing{i + 1}", _matStairs, box, h1 - 0.3f, h1);
                dir = -dir;
            }
            // descansillo inicial a cota 0 (extremo de arranque)
            {
                int d0 = s.startDir == 0 ? 1 : s.startDir;
                float la0 = d0 > 0 ? axis0 : axis0 + landing + run;
                var box = alongZ ? new Box(cross0, la0, cross0 + crossLen, la0 + landing) : new Box(la0, cross0, la0 + landing, cross0 + crossLen);
                MakeBox(root, $"{s.id}_Landing0", _matStairs, box, -0.3f, 0.02f);
            }
        }

        // ---------- conectores ----------
        static void BuildConnector(LevelPlan plan, PlanConnector c, Transform parent, Dictionary<string, int> stats)
        {
            var root = new GameObject(c.id).transform; root.SetParent(parent); root.position = c.origin.ToVector3();
            var geo = new GameObject("Geometry").transform; geo.SetParent(root, false);
            float half = c.width / 2f, env = plan.envelopeWallThickness;
            float minX = c.points.Min(p => p.x) - half - env, maxX = c.points.Max(p => p.x) + half + env;
            float minZ = c.points.Min(p => p.z) - half - env, maxZ = c.points.Max(p => p.z) + half + env;
            foreach (var a in c.alcoves) { minX = Mathf.Min(minX, a.x - env); minZ = Mathf.Min(minZ, a.z - env); maxX = Mathf.Max(maxX, a.x + a.w + env); maxZ = Mathf.Max(maxZ, a.z + a.d + env); }
            var grid = new Grid(minX, minZ, maxX, maxZ);

            // banda del pasillo: segmentos ortogonales, esquinas cuadradas. El primer y último punto están sobre el
            // plano de la puerta del sector: la banda no se extiende hacia atrás de ese plano (68.5).
            var freeRects = new List<Box>();
            for (int i = 1; i < c.points.Count; i++)
            {
                var a = c.points[i - 1]; var b = c.points[i];
                bool alongX = Mathf.Approximately(a.z, b.z);
                float x0 = Mathf.Min(a.x, b.x) - half, x1 = Mathf.Max(a.x, b.x) + half, z0 = Mathf.Min(a.z, b.z) - half, z1 = Mathf.Max(a.z, b.z) + half;
                if (i == 1)
                {
                    if (alongX) { if (a.x < b.x) x0 = a.x; else x1 = a.x; }
                    else { if (a.z < b.z) z0 = a.z; else z1 = a.z; }
                }
                if (i == c.points.Count - 1)
                {
                    if (alongX) { if (b.x > a.x) x1 = b.x; else x0 = b.x; }
                    else { if (b.z > a.z) z1 = b.z; else z0 = b.z; }
                }
                freeRects.Add(new Box(x0, z0, x1, z1));
            }
            foreach (var r in freeRects) grid.Fill(r.x0 - env, r.z0 - env, r.x1 + env, r.z1 + env, C.Solid);
            foreach (var a in c.alcoves) grid.Fill(a.x - env, a.z - env, a.x + a.w + env, a.z + a.d + env, C.Solid);
            foreach (var r in freeRects) grid.Fill(r.x0, r.z0, r.x1, r.z1, C.Free);
            foreach (var a in c.alcoves) grid.Fill(a.x, a.z, a.x + a.w, a.z + a.d, C.Free);
            // extremos abiertos hacia las puertas: el primer y último punto están sobre el plano de la puerta
            var first = c.points[0]; var last = c.points[c.points.Count - 1];
            var fd = plan.Door(c.fromDoor); var td = plan.Door(c.toDoor);
            // el sólido que la expansión ±env deja justo detrás del plano de puerta se elimina: ese muro pertenece al sector
            grid.Fill(first.x - env - 0.01f, first.z - half - env, first.x, first.z + half + env, C.None);
            grid.Fill(last.x, last.z - half - env, last.x + env + 0.01f, last.z + half + env, C.None);

            int solids = 0; foreach (var b in grid.Merge(C.Solid)) { MakeBox(geo, "Solid", _matSolid, b, 0, c.height); solids++; }
            int slabs = 0; foreach (var b in grid.MergeAny()) { MakeBox(geo, "Floor", _matFloor, b, -SlabThickness, 0); slabs++; }
            foreach (var b in grid.MergeAny()) MakeBox(geo, "Ceiling", _matSolid, b, c.height, c.height + SlabThickness);
            stats["solid_" + c.id] = solids; stats["floor_" + c.id] = slabs;
        }

        // ---------- marcadores ----------
        static void BuildMarkers(LevelPlan plan, Transform parent, Dictionary<string, int> stats)
        {
            var root = new GameObject("Markers").transform; root.SetParent(parent);
            int n = 0;
            foreach (var s in plan.spawns) { Marker(plan, root, MarkerKind.Spawn, s.id, s.space, s.x, s.z, 0, s.yaw, s.kind, 0, s.note); n++; }
            foreach (var p in plan.pickups) { Marker(plan, root, MarkerKind.Pickup, p.id, p.space, p.x, p.z, p.height, 0, p.kind, p.amount, p.support); n++; }
            foreach (var d in plan.documents) { Marker(plan, root, MarkerKind.Document, d.id, d.space, d.x, d.z, 0.9f, 0, "Document", 0, d.support + " · " + d.condition); n++; }
            foreach (var cp in plan.checkpoints) { Marker(plan, root, MarkerKind.Checkpoint, cp.id, cp.space, cp.x, cp.z, 0, 0, "Checkpoint", 0, cp.activation + " · " + cp.protection); n++; }
            foreach (var m in plan.mechanisms) { Marker(plan, root, MarkerKind.Mechanism, m.id, m.space, m.x, m.z, 1.1f, 0, m.kind, 0, "opens " + m.opens); n++; }
            foreach (var d in plan.doors) { Marker(plan, root, MarkerKind.Door, d.id, d.floor, d.x, d.z, 0, EdgeYaw(d.edge), d.edge, Mathf.RoundToInt(d.width * 10), d.state); n++; }
            if (plan.exterior != null) { Marker(plan, root, MarkerKind.Victory, "VICTORY", plan.exterior.space, plan.exterior.victoryX, plan.exterior.victoryZ, 0, 0, "Victory", 0, "Trigger de victoria (97)"); n++; }
            stats["markers"] = n;
        }

        static float EdgeYaw(string e) => e == "N" ? 0 : e == "E" ? 90 : e == "S" ? 180 : 270;

        static void Marker(LevelPlan plan, Transform root, MarkerKind kind, string id, string space, float x, float z, float h, float yaw, string sub, int amount, string note)
        {
            if (!plan.TryToWorld(space, x, z, out var w)) { Debug.LogError($"Marcador {id}: espacio {space} desconocido"); return; }
            var go = new GameObject($"{kind}_{id}");
            go.transform.SetParent(root);
            go.transform.position = w + Vector3.up * h;
            go.transform.rotation = Quaternion.Euler(0, yaw, 0);
            var m = go.AddComponent<LevelMarker>();
            m.kind = kind; m.stableId = id; m.guid = LevelPlan.StableGuid(id).ToString(); m.spaceId = space; m.subKind = sub; m.yaw = yaw; m.amount = amount; m.note = note;
            var f = plan.Floor(space); var c = plan.Connector(space);
            m.regionId = f != null ? f.region : c != null ? c.region : "";
        }

        // ---------- utilidades ----------
        struct Box { public float x0, z0, x1, z1; public Box(float a, float b, float c, float d) { x0 = a; z0 = b; x1 = c; z1 = d; } }

        static void MakeBox(Transform parent, string name, Material mat, Box b, float y0, float y1)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Cube);
            go.name = name;
            go.transform.SetParent(parent, false);
            go.transform.localPosition = new Vector3((b.x0 + b.x1) / 2f, (y0 + y1) / 2f, (b.z0 + b.z1) / 2f);
            go.transform.localScale = new Vector3(b.x1 - b.x0, y1 - y0, b.z1 - b.z0);
            go.GetComponent<MeshRenderer>().sharedMaterial = mat;
            go.isStatic = true;
        }

        static void EnsureMaterials()
        {
            _matFloor = Mat("Blockout_Floor", new Color(0.45f, 0.45f, 0.47f));
            _matSolid = Mat("Blockout_Solid", new Color(0.28f, 0.29f, 0.32f));
            _matStairs = Mat("Blockout_Stairs", new Color(0.55f, 0.45f, 0.30f));
            _matLintel = Mat("Blockout_Lintel", new Color(0.35f, 0.25f, 0.25f));
            _matPillar = Mat("Blockout_Pillar", new Color(0.30f, 0.35f, 0.45f));
            _matExterior = Mat("Blockout_Exterior", new Color(0.50f, 0.55f, 0.45f));
        }

        static Material Mat(string name, Color color)
        {
            const string dir = "Assets/_Game/Art/Materials/Blockout";
            Directory.CreateDirectory(dir);
            string path = $"{dir}/{name}.mat";
            var m = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (m == null)
            {
                var shader = Shader.Find("Universal Render Pipeline/Lit");
                m = new Material(shader);
                AssetDatabase.CreateAsset(m, path);
            }
            m.SetColor("_BaseColor", color);
            EditorUtility.SetDirty(m);
            return m;
        }

        class Grid
        {
            readonly float _minX, _minZ; readonly int _nx, _nz; readonly C[] _c;
            public Grid(float minX, float minZ, float maxX, float maxZ)
            {
                _minX = minX; _minZ = minZ;
                _nx = Mathf.CeilToInt((maxX - minX) / Cell - 0.0001f); _nz = Mathf.CeilToInt((maxZ - minZ) / Cell - 0.0001f);
                _c = new C[_nx * _nz];
            }
            Grid(Grid o) { _minX = o._minX; _minZ = o._minZ; _nx = o._nx; _nz = o._nz; _c = (C[])o._c.Clone(); }
            public Grid Clone() => new Grid(this);
            public void Fill(float x0, float z0, float x1, float z1, C v)
            {
                int i0 = Mathf.Max(0, Mathf.RoundToInt((x0 - _minX) / Cell)), i1 = Mathf.Min(_nx, Mathf.RoundToInt((x1 - _minX) / Cell));
                int j0 = Mathf.Max(0, Mathf.RoundToInt((z0 - _minZ) / Cell)), j1 = Mathf.Min(_nz, Mathf.RoundToInt((z1 - _minZ) / Cell));
                for (int j = j0; j < j1; j++) for (int i = i0; i < i1; i++) _c[j * _nx + i] = v;
            }
            public List<Box> Merge(C v) => MergeWhere(c => c == v);
            public List<Box> MergeAny() => MergeWhere(c => c != C.None);
            List<Box> MergeWhere(Func<C, bool> pred)
            {
                var result = new List<Box>();
                var open = new Dictionary<(int, int), (int j0, int jEnd)>();
                for (int j = 0; j <= _nz; j++)
                {
                    var runs = new List<(int, int)>();
                    if (j < _nz)
                    {
                        int i = 0;
                        while (i < _nx)
                        {
                            if (!pred(_c[j * _nx + i])) { i++; continue; }
                            int s = i; while (i < _nx && pred(_c[j * _nx + i])) i++;
                            runs.Add((s, i));
                        }
                    }
                    var next = new Dictionary<(int, int), (int, int)>();
                    foreach (var r in runs)
                    {
                        if (open.TryGetValue(r, out var o)) next[r] = (o.j0, j + 1);
                        else next[r] = (j, j + 1);
                    }
                    foreach (var kv in open) if (!next.ContainsKey(kv.Key))
                        result.Add(new Box(_minX + kv.Key.Item1 * Cell, _minZ + kv.Value.j0 * Cell, _minX + kv.Key.Item2 * Cell, _minZ + kv.Value.jEnd * Cell));
                    open = next;
                }
                return result;
            }
        }
    }
}
