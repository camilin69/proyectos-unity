using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;

namespace Dream.EditorTools
{
    // Configura el FBX del sonador como Humanoid y ajusta sus clips segun la spec, de forma reproducible: si el
    // FBX se reexporta desde Blender, el import vuelve a quedar igual sin tocar nada a mano.
    // Los huesos ya llevan los nombres canonicos de Unity (Hips, LeftUpperArm...), asi que el mapeo automatico
    // acierta; el rig esta en pose A y Unity la lleva a T al configurar el Avatar.
    public class SonadorImportPostprocessor : AssetPostprocessor
    {
        public const string ModelPath = "Assets/_Project/Art/Models/Character/SN-01_Sonador.fbx";
        public const string SpecPath = "Assets/_Project/Animation/Spec/PlayerAnimatorSpec.json";

        void OnPreprocessModel()
        {
            if (assetPath != ModelPath) return;
            var mi = (ModelImporter)assetImporter;
            mi.animationType = ModelImporterAnimationType.Human;
            mi.avatarSetup = ModelImporterAvatarSetup.CreateFromThisModel;
            mi.importAnimation = true;
            mi.animationCompression = ModelImporterAnimationCompression.Optimal;
            mi.materialImportMode = ModelImporterMaterialImportMode.None;   // el material de tela se asigna en HDRP
            mi.importBlendShapes = false;
        }

        void OnPreprocessAnimation()
        {
            if (assetPath != ModelPath) return;
            var mi = (ModelImporter)assetImporter;
            var spec = File.Exists(SpecPath) ? Dream.AnimatorSpec.FromJson(File.ReadAllText(SpecPath)) : null;
            var clips = mi.defaultClipAnimations;
            foreach (var c in clips)
            {
                var st = spec?.states.FirstOrDefault(s => s.clip == c.name);
                bool loop = st != null ? st.loop : false;
                c.loopTime = loop;
                c.loopPose = loop;
                // clips en el sitio: el CharacterController mueve al personaje, no la animacion
                c.lockRootRotation = true;
                c.keepOriginalOrientation = true;
                c.lockRootHeightY = false;
                c.keepOriginalPositionY = true;
                c.lockRootPositionXZ = true;
                c.keepOriginalPositionXZ = true;
            }
            mi.clipAnimations = clips;
        }
    }
}
