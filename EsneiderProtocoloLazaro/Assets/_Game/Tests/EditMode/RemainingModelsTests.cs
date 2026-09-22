using System.Linq;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

namespace Esneider.Tests
{
    public class RemainingModelsTests
    {
        static readonly string[] Assets = {
            "OBJ-015_PulseraLazaro", "OBJ-042_CierreContencion", "OBJ-071_EsclusaPresion",
            "OBJ-073_ConsolaPrincipal", "OBJ-075_BarandaPasarela", "OBJ-077_PanelEscape",
            "OBJ-078_CompuertaMonumental", "OBJ-080_ArchivoFisico", "ENV-EXIT_ExteriorEscape"
        };

        [Test]
        public void Ex50ModelsHaveDistinctGeometryEvidenceAndExpectedParts()
        {
            foreach (string asset in Assets)
            {
                var prefab = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Environment/" + asset + ".prefab");
                Assert.IsNotNull(prefab, asset); var root = Object.Instantiate(prefab);
                try
                {
                    int tris = root.GetComponentsInChildren<MeshFilter>(true).Sum(m => m.sharedMesh.triangles.Length / 3);
                    Assert.Greater(tris, 500, asset); Assert.Greater(root.GetComponentsInChildren<Renderer>(true).Length, 3, asset);
                    Assert.IsTrue(System.IO.File.Exists(System.IO.Path.GetFullPath(System.IO.Path.Combine(
                        Application.dataPath, "../../SourceArt/_evidence/EX-50/" + asset + "/delivery.json"))), asset);
                }
                finally { Object.DestroyImmediate(root); }
            }
        }

        [Test]
        public void Ex50FunctionalPartsAreNamed()
        {
            AssertParts("OBJ-015_PulseraLazaro", "wrist_band", "closure", "identity_plate");
            AssertParts("OBJ-042_CierreContencion", "locking_pin", "servo_actuator", "status_light");
            AssertParts("OBJ-071_EsclusaPresion", "pressure_door", "door_seal", "pressure_control");
            AssertParts("OBJ-073_ConsolaPrincipal", "screen_00", "maintenance_hinge", "cable_trunk");
            AssertParts("OBJ-075_BarandaPasarela", "walkway_deck", "handrail", "support");
            AssertParts("OBJ-077_PanelEscape", "release_button", "permission_light", "pull_handle");
            AssertParts("OBJ-078_CompuertaMonumental", "gate_leaf_L", "gate_leaf_R", "hydraulic_piston");
            AssertParts("OBJ-080_ArchivoFisico", "DOC-01", "DOC-12", "document_tray");
            AssertParts("ENV-EXIT_ExteriorEscape", "escape_platform", "safe_path", "horizon_occluder");
        }

        static void AssertParts(string asset, params string[] required)
        {
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Environment/" + asset + ".prefab");
            var names = prefab.GetComponentsInChildren<Transform>(true).Select(t => t.name).ToArray();
            foreach (string part in required) CollectionAssert.Contains(names, part, asset);
        }
    }
}
