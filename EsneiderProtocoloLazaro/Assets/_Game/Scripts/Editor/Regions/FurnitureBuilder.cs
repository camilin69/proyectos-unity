using System.Collections.Generic;
using System.Linq;
using Esneider.Core;
using Esneider.Core.Data;
using Esneider.World;
using UnityEditor;
using UnityEngine;

namespace Esneider.EditorTools
{
    // 76: mobiliario y cobertura por sala desde el plano (M001–M081). Kit opaco con collider sólido; familias hero usan su prefab
    // (crio→OBJ-001, carro→OBJ-029, mesa quirúrgica→OBJ-043, consola/terminal→OBJ-059). Jaulas: conjuntos 5×6×3 de barrotes con hueco de puerta.
    // Antes de instanciar valida reservas (76.1): disco 0.65 m por pickup/documento, 0.6 m por spawn, 1.2 m de aproximación a paneles,
    // 1.5 m en checkpoints y el vano de cada puerta; si una huella invade, la desplaza (≤2.5 m) y registra la corrección.
    public static class FurnitureBuilder
    {
        public static List<string> Apply(LevelPlan plan, string region, List<string> spaces, Transform ents, List<string> corrections)
        {
            var placed = new List<string>();
            var root = new GameObject("Furniture").transform; root.SetParent(ents);
            GameObject P(string id) => AssetDatabase.LoadAssetAtPath<GameObject>(ShowcaseBuilder.Prefab(id));

            foreach (var f in plan.furniture.Where(x => spaces.Contains(x.space)))
            {
                var floor = plan.Floor(f.space); if (floor == null) continue;
                var room = plan.Room(f.room);
                bool swap = Mathf.Abs(Mathf.Repeat(f.yaw, 180f) - 90f) < 1f;
                float w = swap ? f.d : f.w, d = swap ? f.w : f.d;
                float cx = f.x, cz = f.z;

                // 1) contención en la sala (la geometría puede sobresalir; la huella no)
                if (room != null)
                {
                    float nx = Mathf.Clamp(cx, room.x + w / 2f + 0.1f, room.x + room.w - w / 2f - 0.1f), nz = Mathf.Clamp(cz, room.z + d / 2f + 0.1f, room.z + room.d - d / 2f - 0.1f);
                    if (Mathf.Abs(nx - cx) > 0.01f || Mathf.Abs(nz - cz) > 0.01f) { corrections.Add($"FUR-{f.id}-ROOM: centro ({cx},{cz}) → ({nx:F2},{nz:F2}) para caber en {f.room}"); cx = nx; cz = nz; }
                }
                // 2) reservas
                var reserves = new List<(string who, float x, float z, float r)>();
                // una jaula abierta (76.2: mantenimiento, puerta permanente) es transitable por dentro: sus pickups/spawns interiores son alcanzables
                bool openCage = f.family == "jaula" && !string.IsNullOrEmpty(f.doorSide);
                if (!openCage) foreach (var p in plan.pickups.Where(p => p.space == f.space)) reserves.Add((p.id, p.x, p.z, 0.65f));
                if (!openCage) foreach (var p in plan.documents.Where(p => p.space == f.space)) reserves.Add((p.id, p.x, p.z, 0.65f));
                if (f.family != "jaula") foreach (var s in plan.spawns.Where(s => s.space == f.space)) reserves.Add((s.id, s.x, s.z, 0.6f));
                if (f.id != "M067") foreach (var m in plan.mechanisms.Where(m => m.space == f.space)) reserves.Add((m.id, m.x, m.z, 1.2f));
                foreach (var c in plan.checkpoints.Where(c => c.space == f.space)) reserves.Add((c.id, c.x, c.z, 1.5f));
                foreach (var dr in plan.doors.Where(dr => dr.floor == f.space)) reserves.Add((dr.id, dr.x, dr.z, dr.width / 2f + 0.6f));
                var log = new Dictionary<string, string>(); float ox = cx, oz = cz;
                for (int iter = 0; iter < 4; iter++)
                {
                    bool moved = false;
                    foreach (var r in reserves)
                    {
                        if (!Overlaps(cx, cz, w, d, r.x, r.z, r.r)) continue;
                        float ax = r.x >= cx ? (r.x - r.r - w / 2f) : (r.x + r.r + w / 2f), az = r.z >= cz ? (r.z - r.r - d / 2f) : (r.z + r.r + d / 2f);
                        float mx = Mathf.Abs(ax - cx), mz = Mathf.Abs(az - cz);
                        float best = Mathf.Min(mx, mz);
                        if (best < 0.01f) continue;
                        if (best > 2.5f) { log[r.who] = $"FUR-{f.id}-{r.who}: huella invade la reserva ({best:F2} m) SIN CORRECCIÓN automática; revisar composición"; continue; }
                        if (mx <= mz) cx = ax + (r.x >= cx ? -0.02f : 0.02f); else cz = az + (r.z >= cz ? -0.02f : 0.02f);
                        log[r.who] = $"FUR-{f.id}-{r.who}: desplazado para liberar la reserva de {r.who}";
                        moved = true;
                    }
                    if (!moved) break;
                }
                foreach (var r in reserves) if (Overlaps(cx, cz, w, d, r.x, r.z, r.r) && !log.ContainsKey(r.who)) log[r.who] = $"FUR-{f.id}-{r.who}: sigue invadiendo la reserva tras 4 pasadas SIN CORRECCIÓN estable (reservas opuestas); revisar composición";
                if (log.Count > 0) corrections.Add(string.Join("; ", log.Values) + $" → ({ox},{oz}) ⇒ ({cx:F2},{cz:F2})");

                var world = floor.origin.ToVector3() + new Vector3(cx, f.yOff, cz);
                switch (f.family)
                {
                    case "crio" when P("OBJ-001_Criocamara") != null:
                    {
                        var go = Place(P("OBJ-001_Criocamara"), f.id + "_OBJ-001", world, f.yaw + 90f, root, GameLayers.WorldStatic);
                        SandboxFactory.Persist(go, f.id, region, Core.Persistence.EntityKind.Breakable); placed.Add(f.id + ":OBJ-001"); break;
                    }
                    case "carro" when P("OBJ-029_Carro") != null:
                    {
                        var go = Place(P("OBJ-029_Carro"), f.id + "_OBJ-029", world, f.yaw, root, f.physics ? GameLayers.DynamicProp : GameLayers.WorldStatic);
                        if (f.physics)
                        {
                            foreach (var c in go.GetComponentsInChildren<Collider>()) Object.DestroyImmediate(c);
                            var bc = go.AddComponent<BoxCollider>(); bc.center = new Vector3(0, 0.45f, 0); bc.size = new Vector3(1.0f, 0.9f, 0.6f);
                            var rb = go.AddComponent<Rigidbody>(); rb.mass = 24f; rb.centerOfMass = new Vector3(0, 0.15f, 0); rb.linearDamping = 0.4f; rb.angularDamping = 1.5f; rb.collisionDetectionMode = CollisionDetectionMode.Continuous;
                            go.AddComponent<PhysicsImpactLogger>();
                            SandboxFactory.Persist(go, f.id, region, Core.Persistence.EntityKind.Movable);
                        }
                        placed.Add(f.id + ":OBJ-029"); break;
                    }
                    case "mesaq" when P("OBJ-043_Camilla") != null:
                        Place(P("OBJ-043_Camilla"), f.id + "_OBJ-043", world, f.yaw, root, GameLayers.WorldStatic); placed.Add(f.id + ":OBJ-043"); break;
                    case "consola": case "terminal":
                        if (f.w * f.d > 2.5f) Box(f, world, w, d, root); // consola central: mueble + terminal encima
                        if (P("OBJ-059_Terminal") != null) { var t = Place(P("OBJ-059_Terminal"), f.id + "_OBJ-059", world + (f.w * f.d > 2.5f ? Vector3.up * f.h : Vector3.zero), f.yaw, root, GameLayers.WorldStatic); placed.Add(f.id + ":OBJ-059"); }
                        else Box(f, world, w, d, root);
                        break;
                    case "jaula": BuildCage(f, world, root); placed.Add(f.id + ":jaula-kit"); break;
                    default: Box(f, world, w, d, root); placed.Add(f.id); break;
                }
            }
            return placed;
        }

        static bool Overlaps(float cx, float cz, float w, float d, float px, float pz, float r)
        {
            float nx = Mathf.Clamp(px, cx - w / 2f, cx + w / 2f), nz = Mathf.Clamp(pz, cz - d / 2f, cz + d / 2f);
            float dx = px - nx, dz = pz - nz; return dx * dx + dz * dz < (r - 0.01f) * (r - 0.01f);
        }

        static void Box(PlanFurniture f, Vector3 world, float w, float d, Transform root)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Cube); go.name = f.id + "_" + f.family; go.transform.SetParent(root);
            go.transform.position = world + Vector3.up * f.h / 2f; go.transform.rotation = Quaternion.Euler(0, f.yaw, 0); go.transform.localScale = new Vector3(f.w, f.h, f.d);
            go.layer = GameLayers.WorldStatic; go.isStatic = true;
            go.GetComponent<MeshRenderer>().sharedMaterial = MaterialFor(f.family);
            go.GetOrAdd<SurfaceTag>().surfaceId = f.family == "banco" || f.family == "mesa" || f.family == "escritorio" || f.family == "silla" || f.family == "sillas" ? "SUR-FAB" : f.family == "vidrio" || f.family == "mampara" ? "SUR-GLS" : f.family == "cascote" || f.family == "viga" ? "SUR-RUB" : "SUR-MET";
        }

        // 76.2: barrotes ≥0.12 m cada 0.35 m, riel superior, hueco de puerta de 2 m; sujeto placeholder inerte en jaulas cerradas (37: no final)
        static void BuildCage(PlanFurniture f, Vector3 world, Transform root)
        {
            var cage = new GameObject(f.id + "_jaula").transform; cage.SetParent(root); cage.position = world;
            var mat = MaterialFor("jaula");
            float hw = f.w / 2f, hd = f.d / 2f, h = f.h;
            void Bar(Vector3 local, Vector3 scale) { var b = GameObject.CreatePrimitive(PrimitiveType.Cube); b.name = "bar"; b.transform.SetParent(cage); b.transform.localPosition = local; b.transform.localScale = scale; b.layer = GameLayers.WorldStatic; b.isStatic = true; b.GetComponent<MeshRenderer>().sharedMaterial = mat; }
            foreach (var side in new[] { "N", "S", "E", "W" })
            {
                bool alongX = side == "N" || side == "S"; float len = alongX ? f.w : f.d; int n = Mathf.FloorToInt(len / 0.35f);
                for (int i = 0; i <= n; i++)
                {
                    float t = -len / 2f + i * (len / n);
                    float coord = alongX ? f.x + t : f.z + t; // coordenada local de planta a lo largo del lado
                    if (f.doorSide == side && Mathf.Abs(coord - f.doorAt) < 1.0f) continue; // hueco útil 2 m
                    var local = alongX ? new Vector3(t, h / 2f, side == "N" ? hd : -hd) : new Vector3(side == "E" ? hw : -hw, h / 2f, t);
                    Bar(local, new Vector3(0.12f, h, 0.12f));
                }
                var rail = alongX ? new Vector3(0, h - 0.06f, side == "N" ? hd : -hd) : new Vector3(side == "E" ? hw : -hw, h - 0.06f, 0);
                Bar(rail, alongX ? new Vector3(f.w + 0.12f, 0.12f, 0.12f) : new Vector3(0.12f, 0.12f, f.d + 0.12f));
            }
            if (string.IsNullOrEmpty(f.doorSide))
            {
                var s = GameObject.CreatePrimitive(PrimitiveType.Capsule); s.name = "Sujeto_placeholder_" + f.id; s.transform.SetParent(cage);
                s.transform.localPosition = new Vector3(0, 0.3f, 0.6f); s.transform.localRotation = Quaternion.Euler(90f, 0, 0); s.transform.localScale = new Vector3(0.45f, 0.85f, 0.45f);
                s.layer = GameLayers.WorldStatic; s.isStatic = true; s.GetComponent<MeshRenderer>().sharedMaterial = MaterialFor("sujeto");
            }
        }

        static Material MaterialFor(string family)
        {
            switch (family)
            {
                case "banco": case "mesa": case "escritorio": case "silla": case "sillas": case "asiento": case "mostrador": return RegionSceneBuilder.BlockoutMat("Kit_Wood", new Color(0.40f, 0.30f, 0.20f));
                case "cascote": case "viga": case "archivos": case "palet": return RegionSceneBuilder.BlockoutMat("Kit_Rubble", new Color(0.36f, 0.34f, 0.31f));
                case "vidrio": case "mampara": return RegionSceneBuilder.BlockoutMat("Kit_Glass", new Color(0.62f, 0.72f, 0.76f));
                case "jaula": return RegionSceneBuilder.BlockoutMat("Kit_Bars", new Color(0.22f, 0.23f, 0.25f));
                case "sujeto": return RegionSceneBuilder.BlockoutMat("Kit_Subject", new Color(0.55f, 0.45f, 0.40f));
                case "panel": case "tablero": case "mapa": case "biomonitor": return RegionSceneBuilder.BlockoutMat("Kit_Panel", new Color(0.25f, 0.30f, 0.34f));
                default: return RegionSceneBuilder.BlockoutMat("Kit_Metal", new Color(0.35f, 0.37f, 0.40f));
            }
        }

        static GameObject Place(GameObject prefab, string name, Vector3 pos, float yaw, Transform parent, int layer)
        {
            var go = (GameObject)PrefabUtility.InstantiatePrefab(prefab); go.name = name; go.transform.SetParent(parent); go.transform.position = pos; go.transform.rotation = Quaternion.Euler(0, yaw, 0);
            foreach (var t in go.GetComponentsInChildren<Transform>()) t.gameObject.layer = layer;
            return go;
        }
    }
}
