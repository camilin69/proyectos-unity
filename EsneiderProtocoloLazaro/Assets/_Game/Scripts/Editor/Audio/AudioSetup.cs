using Esneider.Core;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using Esneider.Audio;
using UnityEditor;
using UnityEngine;
using UnityEngine.Audio;

namespace Esneider.EditorTools
{
    // 17: mezclador con grupos Master/Ambient/Enemies/Weapons/Voice/UI y bancos por ID desde Assets/_Game/Audio/**.
    public static class AudioSetup
    {
        public const string MixerPath = "Assets/_Game/Audio/EsneiderMixer.mixer";
        public const string BankSetPath = "Assets/_Game/Audio/AudioBankSet.asset";
        static readonly string[] Groups = { "Ambient", "Enemies", "Weapons", "Voice", "UI" };

        [MenuItem("Esneider/Audio/Setup mixer + banks")]
        public static void SetupMenu() => Debug.Log(Setup());

        public static string Setup()
        {
            var log = new List<string>();
            var mixer = AssetDatabase.LoadAssetAtPath<AudioMixer>(MixerPath);
            if (mixer == null)
            {
                // AudioMixerController es API interna del editor: se crea por reflexión y se documenta como dependencia (94.4)
                try
                {
                    var t = typeof(Editor).Assembly.GetType("UnityEditor.Audio.AudioMixerController");
                    var create = t.GetMethod("CreateMixerControllerAtPath", BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic);
                    var ctrl = create.Invoke(null, new object[] { MixerPath });
                    var master = t.GetProperty("masterGroup").GetValue(ctrl);
                    var createGroup = t.GetMethod("CreateNewGroup", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
                    var addChild = t.GetMethod("AddChildToParent", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
                    foreach (var g in Groups)
                    {
                        var grp = createGroup.Invoke(ctrl, new object[] { g, false });
                        addChild.Invoke(ctrl, new object[] { grp, master });
                    }
                    EditorUtility.SetDirty((Object)ctrl); AssetDatabase.SaveAssets(); AssetDatabase.ImportAsset(MixerPath);
                    mixer = AssetDatabase.LoadAssetAtPath<AudioMixer>(MixerPath);
                    log.Add("mixer creado con " + Groups.Length + " grupos");
                }
                catch (System.Exception e) { log.Add("mixer no creado (API interna): " + e.Message); }
            }
            var set = AssetDatabase.LoadAssetAtPath<AudioBankSet>(BankSetPath);
            if (set == null) { set = ScriptableObject.CreateInstance<AudioBankSet>(); AssetDatabase.CreateAsset(set, BankSetPath); }
            set.banks.Clear();
            var byId = new Dictionary<string, List<AudioClip>>();
            foreach (var guid in AssetDatabase.FindAssets("t:AudioClip", new[] { "Assets/_Game/Audio" }))
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                var name = Path.GetFileNameWithoutExtension(path);
                if (name.EndsWith("_dry")) continue;
                var clip = AssetDatabase.LoadAssetAtPath<AudioClip>(path);
                string id = System.Text.RegularExpressions.Regex.Replace(name, @"-(\d+|[A-D]|Tutorial)$", "");
                if (name.EndsWith("-Tutorial")) id = name;
                if (!byId.TryGetValue(id, out var list)) byId[id] = list = new List<AudioClip>();
                list.Add(clip);
                var imp = AssetImporter.GetAtPath(path) as AudioImporter;
                if (imp != null)
                {
                    var s = imp.defaultSampleSettings; bool bed = path.Contains("/Ambience/") || name.Contains("AMBI");
                    s.loadType = bed ? AudioClipLoadType.Streaming : AudioClipLoadType.DecompressOnLoad; s.compressionFormat = bed ? AudioCompressionFormat.Vorbis : AudioCompressionFormat.ADPCM; s.quality = 0.6f;
                    imp.defaultSampleSettings = s; imp.forceToMono = !bed; imp.loadInBackground = bed; imp.SaveAndReimport();
                }
            }
            foreach (var kv in byId.OrderBy(k => k.Key)) set.banks.Add(new AudioBank { id = kv.Key, clips = kv.Value.OrderBy(c => c.name).ToArray() });
            EditorUtility.SetDirty(set); AssetDatabase.SaveAssets();
            log.Add($"bancos: {set.banks.Count} ({byId.Values.Sum(v => v.Count)} clips)");
            return string.Join(" | ", log);
        }

        // Añade AudioService + AudioEvents a un GameObject de sistemas con el mixer y los bancos.
        public static AudioService Attach(GameObject systems)
        {
            var svc = systems.GetOrAdd<AudioService>();
            var mixer = AssetDatabase.LoadAssetAtPath<AudioMixer>(MixerPath);
            if (mixer != null)
            {
                svc.mixer = mixer;
                AudioMixerGroup G(string n) { var g = mixer.FindMatchingGroups(n); return g != null && g.Length > 0 ? g[0] : null; }
                svc.master = G("Master"); svc.ambient = G("Ambient"); svc.enemies = G("Enemies"); svc.weapons = G("Weapons"); svc.voice = G("Voice"); svc.ui = G("UI");
            }
            var ev = systems.GetOrAdd<AudioEvents>();
            ev.service = svc; ev.bankSet = AssetDatabase.LoadAssetAtPath<AudioBankSet>(BankSetPath);
            return svc;
        }
    }
}
