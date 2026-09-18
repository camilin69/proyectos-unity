using System.Collections.Generic;
using System.IO;
using System.Linq;
using Esneider.Core;
using Esneider.Core.Data;
using Esneider.World;
using UnityEditor;
using UnityEngine;

namespace Esneider.EditorTools
{
    // Vestido hero por región (44.3/59/76): sustituye placeholders por prefabs integrados en sus posiciones del plano.
    // Solo actúa cuando el prefab existe; los pendientes quedan registrados (no se declaran primitivas como finales).
    public static class HeroDressing
    {
        public static List<string> Apply(LevelPlan plan, string region, List<string> spaces, Transform ents)
        {
            var placed = new List<string>();
            GameObject P(string id) => AssetDatabase.LoadAssetAtPath<GameObject>(ShowcaseBuilder.Prefab(id));

            // OBJ-001 criocámara: S1-R01 (SCN-01), orientada al este; DOC-01 en su consola
            if (spaces.Contains("P01") && P("OBJ-001_Criocamara") != null)
            {
                var w = plan.Floor("P01").origin.ToVector3() + new Vector3(6f, 0, 8f);
                var go = Place(P("OBJ-001_Criocamara"), "OBJ-001_Criocamara", w, 90f, ents, GameLayers.WorldStatic);
                Persist(go, "OBJ-001", region, Core.Persistence.EntityKind.Breakable); placed.Add("OBJ-001");
            }
            // OBJ-029 carro físico: P03 taller (SCN-08) y sandbox de física; Rigidbody + PhysicsImpactLogger
            if (spaces.Contains("P03") && P("OBJ-029_Carro") != null)
            {
                var w = plan.Floor("P03").origin.ToVector3() + new Vector3(36f, 0, 10f);
                var go = Place(P("OBJ-029_Carro"), "OBJ-029_Carro", w, 0f, ents, GameLayers.DynamicProp);
                foreach (var c in go.GetComponentsInChildren<Collider>()) Object.DestroyImmediate(c);
                var bc = go.AddComponent<BoxCollider>(); bc.center = new Vector3(0, 0.45f, 0); bc.size = new Vector3(1.0f, 0.9f, 0.6f);
                var rb = go.AddComponent<Rigidbody>(); rb.mass = 24f; rb.centerOfMass = new Vector3(0, 0.15f, 0); rb.linearDamping = 0.4f; rb.angularDamping = 1.5f; rb.collisionDetectionMode = CollisionDetectionMode.Continuous;
                go.AddComponent<PhysicsImpactLogger>();
                Persist(go, "OBJ-029", region, Core.Persistence.EntityKind.Movable); placed.Add("OBJ-029");
            }
            // OBJ-041 jaulas: alas A/B de S3 (SCN-14/15): 4 módulos por ala en dos filas
            if (spaces.Contains("P05") && P("OBJ-041_Jaula") != null)
            {
                int k = 0;
                foreach (var (rx, rz) in new[] { (2f, 2f), (26f, 2f) })
                    for (int i = 0; i < 4; i++)
                    {
                        var w = plan.Floor("P05").origin.ToVector3() + new Vector3(rx + 3.5f + (i % 2) * 8f, 0, rz + 4f + (i / 2) * 10f);
                        var go = Place(P("OBJ-041_Jaula"), $"OBJ-041_Jaula_{k}", w, 0f, ents, GameLayers.WorldStatic);
                        Persist(go, $"OBJ-041-{k}", region, Core.Persistence.EntityKind.Breakable); k++;
                    }
                placed.Add("OBJ-041×8");
            }
            // OBJ-043 camilla: clínica S3-R03 (SCN-16) y observación
            if (spaces.Contains("P05") && P("OBJ-043_Camilla") != null)
            {
                foreach (var (x, z, yaw) in new[] { (30f, 40f, 90f), (26f, 46f, 0f), (48f, 38f, 90f) })
                    Place(P("OBJ-043_Camilla"), "OBJ-043_Camilla", plan.Floor("P05").origin.ToVector3() + new Vector3(x, 0, z), yaw, ents, GameLayers.WorldStatic);
                placed.Add("OBJ-043×3");
            }
            // OBJ-059 terminales: en los DOC de consola/terminal (68.8) y control
            if (P("OBJ-059_Terminal") != null)
            {
                var docTerminals = new Dictionary<string, string> { { "DOC-01", "P01" }, { "DOC-07", "P05" }, { "DOC-09", "P05" }, { "DOC-11", "P06" } };
                foreach (var d in plan.documents.Where(x => docTerminals.ContainsKey(x.id) && spaces.Contains(x.space)))
                {
                    plan.TryToWorld(d.space, d.x, d.z, out var w);
                    Place(P("OBJ-059_Terminal"), "OBJ-059_Terminal_" + d.id, w + new Vector3(0, 0, 0.6f), 180f, ents, GameLayers.WorldStatic);
                    var sup = ents.Find("Support_" + d.id); if (sup != null) Object.DestroyImmediate(sup.gameObject);
                    placed.Add("OBJ-059@" + d.id);
                }
            }
            // OBJ-070 puertas corredizas: todas las puertas de 2.8 m (68.4) sustituyen la hoja-caja por el modelo animado
            if (P("OBJ-070_PuertaCorrediza") != null)
            {
                var clip = AssetDatabase.LoadAllAssetsAtPath("Assets/_Game/Art/Models/OBJ-070_PuertaCorrediza.fbx").OfType<AnimationClip>().FirstOrDefault(c => c.name == "Door_Open");
                foreach (var d in plan.doors.Where(x => spaces.Contains(x.floor) && x.width >= 2.8f && x.width < 5f))
                {
                    var box = ents.Find("Door_" + d.id); if (box == null) continue;
                    var door = box.GetComponent<Door>();
                    var f = plan.Floor(d.floor); var w = f.origin.ToVector3() + new Vector3(d.x, 0, d.z);
                    bool alongX = d.edge == "N" || d.edge == "S";
                    var model = Place(P("OBJ-070_PuertaCorrediza"), "OBJ-070_" + d.id, w, alongX ? 0f : 90f, ents, GameLayers.DynamicProp);
                    foreach (var c in model.GetComponentsInChildren<Collider>()) Object.DestroyImmediate(c);
                    // hojas: collider por hoja bajo el hueso correspondiente (acompaña la animación)
                    var leafCols = new List<Collider>();
                    foreach (var leafName in new[] { "leaf_0", "leaf_1" })
                    {
                        var leaf = model.GetComponentsInChildren<Transform>().FirstOrDefault(t => t.name == leafName);
                        if (leaf == null) continue;
                        var bc = leaf.gameObject.AddComponent<BoxCollider>(); bc.center = new Vector3(0, 1.72f, 0); bc.size = new Vector3(1.5f, 3.45f, 0.14f); leafCols.Add(bc);
                        leaf.gameObject.layer = GameLayers.DynamicProp;
                    }
                    // la Door lógica pasa al modelo; la caja placeholder desaparece (68.4: el estado lo conserva PersistentEntity)
                    var newDoor = model.AddComponent<Door>(); newDoor.doorId = door.doorId; newDoor.isOpen = door.isOpen; newDoor.locked = door.locked; newDoor.requiresPermission = door.requiresPermission; newDoor.openSeconds = 2.0f; newDoor.leaf = model.transform; newDoor.openOffset = Vector3.zero;
                    var pe = box.GetComponent<PersistentEntity>(); var npe = model.AddComponent<PersistentEntity>(); npe.stableId = pe.stableId; npe.guid = pe.guid; npe.regionId = pe.regionId; npe.prefabId = "OBJ-070"; npe.kind = pe.kind;
                    var da = model.AddComponent<DoorAnimated>(); da.door = newDoor; da.animator = model.GetOrAdd<Animator>(); da.openClip = clip; da.leafColliders = leafCols.ToArray();
                    var obs = model.AddComponent<UnityEngine.AI.NavMeshObstacle>(); obs.carving = true; obs.carveOnlyStationary = false; obs.center = new Vector3(0, 1.75f, 0); obs.size = new Vector3(3.0f, 3.5f, 0.3f);
                    Object.DestroyImmediate(box.gameObject);
                    placed.Add("OBJ-070@" + d.id);
                }
            }
            // pickups de armas y consumibles con su modelo (38): el Pickup conserva ID/GUID; el visual cambia
            var visual = new Dictionary<string, string> { { "Crowbar", "WPN-01_Crowbar" }, { "Pistol", "WPN-02_Pistol" }, { "Shotgun", "WPN-03_Shotgun" }, { "Flashlight", "WPN-04_Flashlight" }, { "Syringe", "PRP-Syringe" }, { "Ration", "PRP-Ration" } };
            foreach (var pk in ents.GetComponentsInChildren<Pickup>(true))
            {
                if (!visual.TryGetValue(pk.kind.ToString(), out var id) || P(id) == null) continue;
                var mr = pk.GetComponent<MeshRenderer>(); if (mr != null) mr.enabled = false;
                var v = (GameObject)PrefabUtility.InstantiatePrefab(P(id), pk.transform); v.name = "Visual"; v.transform.localPosition = Vector3.zero; v.transform.localRotation = Quaternion.Euler(0, 0, 90f); v.transform.localScale = Vector3.one * 4f; // compensa la escala 0.25 del pickup esférico
                foreach (var c in v.GetComponentsInChildren<Collider>()) Object.DestroyImmediate(c);
                foreach (var t in v.GetComponentsInChildren<Transform>()) t.gameObject.layer = GameLayers.Interactable;
            }
            return placed;
        }

        static GameObject Place(GameObject prefab, string name, Vector3 pos, float yaw, Transform parent, int layer)
        {
            var go = (GameObject)PrefabUtility.InstantiatePrefab(prefab); go.name = name; go.transform.SetParent(parent); go.transform.position = pos; go.transform.rotation = Quaternion.Euler(0, yaw, 0);
            foreach (var t in go.GetComponentsInChildren<Transform>()) t.gameObject.layer = layer;
            return go;
        }

        static void Persist(GameObject go, string id, string region, Core.Persistence.EntityKind kind) => SandboxFactory.Persist(go, id, region, kind);
    }
}
