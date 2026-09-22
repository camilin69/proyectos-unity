using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using Esneider.Core.Persistence;
using Esneider.World;
#if UNITY_EDITOR
using UnityEditor;
#endif

namespace Esneider.Tests
{
    public class PreservationConsolePlayTests
    {
        [UnityTest]
        public IEnumerator ReadoutFollowsOpeningAndRestoredConfirmationWithoutRepeatingIt()
        {
#if UNITY_EDITOR
            var previous = WorldStateRegistry.Session.Snapshot(); GameObject root = null;
            try
            {
                WorldStateRegistry.ResetSession();
                var prefab = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Environment/OBJ-003_ConsolaPreservacion.prefab");
                root = Object.Instantiate(prefab); var console = root.GetComponent<PreservationConsole>();
                yield return null;
                StringAssert.Contains("DIAGNÓSTICO", console.display.text); Assert.IsFalse(console.CanInteract(root));
                console.Interact(root); Assert.IsFalse(WorldStateRegistry.Session.HasFlag(PreservationConsole.ConfirmedFlag));
                WorldStateRegistry.Session.SetFlag("OPENING_DONE"); yield return null;
                StringAssert.Contains("2000 AÑOS", console.display.text); StringAssert.Contains("ESNEIDER", console.display.text); Assert.IsTrue(console.CanInteract(root));
                console.Interact(root); var sequence = WorldStateRegistry.Session.Sequence;
                console.Interact(root); Assert.AreEqual(sequence, WorldStateRegistry.Session.Sequence);
                Assert.IsFalse(console.CanInteract(root)); StringAssert.Contains("REGISTRO CONFIRMADO", console.display.text);
                var checkpoint = WorldStateRegistry.Session.Snapshot();
                Object.Destroy(root); yield return null; WorldStateRegistry.ResetSession(); WorldStateRegistry.Session.Restore(checkpoint);
                root = Object.Instantiate(prefab); console = root.GetComponent<PreservationConsole>(); yield return null;
                StringAssert.Contains("2000 AÑOS", console.display.text); StringAssert.Contains("REGISTRO CONFIRMADO", console.display.text); Assert.IsFalse(console.CanInteract(root));
                // An already loaded display must also reflect restoring an earlier checkpoint.
                WorldStateRegistry.ResetSession(); yield return null;
                StringAssert.Contains("DIAGNÓSTICO", console.display.text); Assert.IsFalse(console.CanInteract(root));
            }
            finally { if (root) Object.Destroy(root); WorldStateRegistry.ResetSession(); WorldStateRegistry.Session.Restore(previous); }
#else
            Assert.Ignore("Editor prefab integration test"); yield break;
#endif
        }
    }
}
