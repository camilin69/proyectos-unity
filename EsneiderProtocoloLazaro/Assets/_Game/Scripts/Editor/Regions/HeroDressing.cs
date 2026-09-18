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

            // Criocámaras (M001, M008–M011), carros (M007/M015/M026/M035), jaulas (M040–M048) y mesas quirúrgicas (M056/M057)
            // los coloca FurnitureBuilder desde el plano 76.2 (EX-06); aquí solo terminales, puertas y pickups.
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
