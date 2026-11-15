using System.IO;
using System.Linq;
using Dream.EditorTools;
using NUnit.Framework;
using UnityEditor;
using UnityEditor.Animations;
using UnityEngine;

namespace Dream.Tests
{
    // El diagrama entregado y el Animator real salen de la misma spec; esta prueba es la que lo garantiza.
    public class AnimatorMatchesSpecTests
    {
        AnimatorSpec spec, built;

        [OneTimeSetUp]
        public void Load()
        {
            spec = AnimatorSpec.FromJson(File.ReadAllText(SonadorImportPostprocessor.SpecPath));
            var ctrl = AssetDatabase.LoadAssetAtPath<AnimatorController>(AnimatorBuilder.ControllerPath);
            Assert.IsNotNull(ctrl, "Falta Sonador.controller: ejecuta 'Sueno Lucido/Construir Animator desde la spec'.");
            built = AnimatorExporter.Export(ctrl);
        }

        [Test] public void DefaultState() => Assert.AreEqual(spec.defaultState, built.defaultState);

        [Test]
        public void Parametros()
        {
            CollectionAssert.AreEquivalent(spec.parameters.Select(p => $"{p.name}:{p.type}:{p.@default}"),
                                           built.parameters.Select(p => $"{p.name}:{p.type}:{p.@default}"));
        }

        [Test]
        public void Estados()
        {
            CollectionAssert.AreEquivalent(spec.states.Select(s => $"{s.name}:{s.clip}:{s.layout[0]},{s.layout[1]}"),
                                           built.states.Select(s => $"{s.name}:{s.clip}:{s.layout[0]},{s.layout[1]}"));
        }

        [Test]
        public void LoopsDeLosClips()
        {
            foreach (var s in spec.states)
                Assert.AreEqual(s.loop, built.states.First(b => b.name == s.name).loop, $"loop de {s.name}");
        }

        static string Key(TransitionSpec t) =>
            $"{t.from}->{t.to} exit={t.hasExitTime}:{(t.hasExitTime ? t.exitTime : 0):0.##} dur={t.duration:0.##} [" +
            string.Join(",", (t.conditions ?? new ConditionSpec[0]).Select(c => $"{c.param} {c.mode} {c.threshold:0.##}").OrderBy(x => x)) + "]";

        [Test]
        public void Transiciones()
        {
            CollectionAssert.AreEquivalent(spec.transitions.Select(Key), built.transitions.Select(Key));
        }
    }

    public class AvatarTests
    {
        [Test]
        public void SonadorEsHumanoidValido()
        {
            var avatar = AssetDatabase.LoadAllAssetsAtPath(SonadorImportPostprocessor.ModelPath).OfType<Avatar>().FirstOrDefault();
            Assert.IsNotNull(avatar, "El FBX no genero Avatar");
            Assert.IsTrue(avatar.isValid, "Avatar invalido");
            Assert.IsTrue(avatar.isHuman, "Avatar no es Humanoid");
        }

        [Test]
        public void ClipsCompletos()
        {
            var names = AssetDatabase.LoadAllAssetsAtPath(SonadorImportPostprocessor.ModelPath).OfType<AnimationClip>()
                .Where(c => !c.name.StartsWith("__")).Select(c => c.name).ToList();
            foreach (var n in new[] { "Idle", "Walk", "Jog", "JumpStart", "Fall", "Land", "Fly", "Swim", "Pickup", "Peek", "Stumble", "Emerge" })
                Assert.Contains(n, names);
            foreach (var c in AssetDatabase.LoadAllAssetsAtPath(SonadorImportPostprocessor.ModelPath).OfType<AnimationClip>())
                if (!c.name.StartsWith("__")) Assert.AreEqual(30f, c.frameRate, 0.01f, $"{c.name} no esta a 30 fps");
        }
    }
}
