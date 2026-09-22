using System;
using System.Linq;
using Esneider.AI;
using Esneider.Core.Data;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine.SceneManagement;

namespace Esneider.EditorTools
{
    public static class RobotPresentationRepair
    {
        // Old scene copies referenced the 37 separate Vigia meshes removed when the
        // model became two LOD meshes. Replace only presentation; retain AI/save IDs.
        public static int Repair(Scene scene)
        {
            int replaced=0;
            foreach(var brain in scene.GetRootGameObjects().SelectMany(g=>g.GetComponentsInChildren<EnemyBrain>(true)))
            {
                var view=brain.GetComponent<EnemyAnimator>();
                if(!view || !view.animator) continue;
                var skins=view.animator.GetComponentsInChildren<SkinnedMeshRenderer>(true);
                if(skins.Any(r=>!r.sharedMesh))
                {
                    if(brain.definition.kind!=EnemyKind.Vigia) throw new InvalidOperationException("Missing robot mesh: "+brain.stableId);
                    var prefab=AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Enemies/BOT-01_Vigia.prefab");
                    var old=view.animator.gameObject;
                    var visual=(GameObject)PrefabUtility.InstantiatePrefab(prefab,old.transform.parent);
                    visual.name=old.name;visual.transform.localPosition=old.transform.localPosition;visual.transform.localScale=old.transform.localScale;
                    foreach(var t in visual.GetComponentsInChildren<Transform>(true)) t.gameObject.layer=brain.gameObject.layer;
                    foreach(var c in visual.GetComponentsInChildren<Collider>(true)) UnityEngine.Object.DestroyImmediate(c);
                    view.animator=visual.GetComponent<Animator>();
                    if(!view.animator)view.animator=visual.AddComponent<Animator>();
                    UnityEngine.Object.DestroyImmediate(old);
                    view.clipsFromFbx=AssetDatabase.LoadAllAssetsAtPath("Assets/_Game/Art/Models/BOT-01_Vigia.fbx").OfType<AnimationClip>().Where(c=>!c.name.StartsWith("__")).ToArray();
                    replaced++;
                }
                view.AlignVisualFacing();view.animator.applyRootMotion=false;view.animator.cullingMode=AnimatorCullingMode.AlwaysAnimate;
            }
            EditorSceneManager.MarkSceneDirty(scene);
            return replaced;
        }

        public static string ApplyExisting()
        {
            if(SceneManager.GetActiveScene().isDirty) throw new InvalidOperationException("Preserve unsaved scene changes first");
            var original=SceneManager.GetActiveScene().path;int repaired=0,total=0;
            foreach(var guid in AssetDatabase.FindAssets("t:Scene",new[]{"Assets/_Game/Scenes/Regions"}))
            {
                var scene=EditorSceneManager.OpenScene(AssetDatabase.GUIDToAssetPath(guid));
                repaired+=Repair(scene);total+=scene.GetRootGameObjects().Sum(g=>g.GetComponentsInChildren<EnemyBrain>(true).Length);
                EditorSceneManager.SaveScene(scene);
            }
            if(!string.IsNullOrEmpty(original))EditorSceneManager.OpenScene(original);
            return "Robots inspected="+total+"; visuals replaced="+repaired;
        }
    }
}
