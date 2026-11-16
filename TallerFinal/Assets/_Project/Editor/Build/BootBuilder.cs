using System.IO;
using System.Linq;
using Dream.Audio;
using Dream.Cinematic;
using Dream.UI;
using Unity.Cinemachine;
using UnityEditor;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem.UI;
using UnityEngine.Rendering;
using UnityEngine.Rendering.HighDefinition;
using static Dream.EditorTools.Build.BuildKit;

namespace Dream.EditorTools.Build
{
    // Boot: lo que vive todo el viaje. Juego (flujo, entrada, puntaje, viaje, director), luz (sol, luna y reloj),
    // cielo (Physically Based Sky + niebla + nubes + optica de camara), el sonador, las camaras y el audio.
    public static class BootBuilder
    {
        public static void Build()
        {
            var scene = NewScene();

            var game = Group("Juego");
            game.gameObject.AddComponent<DreamInput>();
            game.gameObject.AddComponent<GameFlow>();
            game.gameObject.AddComponent<ScoreSystem>();
            game.gameObject.AddComponent<JourneyManager>();
            var director = game.gameObject.AddComponent<CinematicDirector>();

            // ---- luz y cielo ----
            var lightRoot = Group("Luz");
            var sun = AddLight("Sol", lightRoot, LightType.Directional, Vector3.zero, new Vector3(30, 120, 0), Color.white, 100000f);
            sun.GetComponent<HDAdditionalLightData>().angularDiameter = 2.2f;   // sombras de borde suave, como el sol de verdad
            var moon = AddLight("Luna", lightRoot, LightType.Directional, Vector3.zero, new Vector3(40, 200, 0), new Color(0.8f, 0.86f, 1f), 2.5f, 10f, 60f, null, false);
            moon.GetComponent<HDAdditionalLightData>().lightDimmer = 1f;
            NightKit.ConfigureMoon(moon);                                  // luna llena grande, como un planeta
            var tod = lightRoot.gameObject.AddComponent<TimeOfDay>();
            tod.sun = sun; tod.moon = moon; tod.hour = 7f; tod.sunset = 18.2f; tod.sunrise = 5.2f;   // a las 07:00 el sol ya entra alto por la ventana del cuarto

            var sky = Profile("Boot_Cielo", p =>
            {
                var ve = p.Add<VisualEnvironment>();
                ve.skyType.Override((int)SkyType.PhysicallyBased);
                ve.skyAmbientMode.Override(SkyAmbientMode.Dynamic);
                p.Add<PhysicallyBasedSky>();
                var ex = p.Add<Exposure>();
                ex.mode.Override(ExposureMode.AutomaticHistogram);
                ex.limitMin.Override(-1.5f);
                ex.limitMax.Override(15.5f);
                ex.compensation.Override(0.3f);
                ex.adaptationSpeedDarkToLight.Override(1.2f);
                ex.adaptationSpeedLightToDark.Override(1.5f);
                Fog(p, 450f, 260f, new Color(0.96f, 0.9f, 0.95f));
                var tm = p.Add<Tonemapping>(); tm.mode.Override(TonemappingMode.ACES);
                var bl = p.Add<Bloom>(); bl.intensity.Override(0.22f); bl.scatter.Override(0.72f);
                var vg = p.Add<Vignette>(); vg.intensity.Override(0.2f); vg.smoothness.Override(0.55f);
                var fg = p.Add<FilmGrain>(); fg.type.Override(FilmGrainLookup.Thin1); fg.intensity.Override(0.12f);
                var st = p.Add<SplitToning>();
                st.shadows.Override(new Color(0.72f, 0.88f, 0.84f));
                st.highlights.Override(new Color(1f, 0.86f, 0.9f));
                st.balance.Override(15f);
                var ca = p.Add<ColorAdjustments>(); ca.saturation.Override(-6f); ca.contrast.Override(4f);
                var ao = p.Add<ScreenSpaceAmbientOcclusion>(); ao.intensity.Override(0.9f);
                var cs = p.Add<ContactShadows>(); cs.enable.Override(true);
                var ssr = p.Add<ScreenSpaceReflection>(); ssr.enabled.Override(true);
                var dof = p.Add<DepthOfField>(); dof.focusMode.Override(DepthOfFieldMode.UsePhysicalCamera);
            });
            GlobalVolume("Cielo", lightRoot, sky, 0f);

            // el sol visible: un disco con halo suave, siempre en la direccion de la luz del sol
            var discTex = SunTexture();
            var discMat = Unlit("M_Disco_Sol", new Color(30f, 28.8f, 26.4f, 1f));   // alfa 1: en aditivo el alfa multiplica el brillo (y desbordaba el bloom)
            HDMaterial.SetSurfaceType(discMat, true);
            discMat.SetFloat("_BlendMode", 1f);
            discMat.SetTexture("_UnlitColorMap", discTex);
            discMat.SetFloat("_EnableFogOnTransparent", 0f);       // a 3 km la niebla lo borraria
            HDMaterial.ValidateMaterial(discMat);
            var disc = Prim(PrimitiveType.Quad, "Disco_del_sol", lightRoot, Vector3.zero, Vector3.one, discMat, null, null, false);
            GameObjectUtility.SetStaticEditorFlags(disc, 0);
            disc.GetComponent<Renderer>().shadowCastingMode = ShadowCastingMode.Off;
            lightRoot.gameObject.AddComponent<SunDisc>().disc = disc.GetComponent<Renderer>();

            // la luna llena grande, como un planeta en el cielo: disco con la textura de luna, tapa las estrellas detras
            // y brilla poco (tools/taller_final/cielos_noche.py)
            var moonTexPath = ScanDir + "/HDRI/T_Luna_llena.png";
            var moonImp = (TextureImporter)AssetImporter.GetAtPath(moonTexPath);
            if (moonImp.wrapMode != TextureWrapMode.Clamp || !moonImp.alphaIsTransparency) { moonImp.wrapMode = TextureWrapMode.Clamp; moonImp.alphaIsTransparency = true; moonImp.SaveAndReimport(); }
            var moonMat = Unlit("M_Disco_Luna", new Color(2.2f, 2.2f, 2.35f, 1f));
            HDMaterial.SetSurfaceType(moonMat, true);
            moonMat.SetFloat("_BlendMode", 0f);                        // alfa: la luna tapa el cielo que tiene detras
            moonMat.SetTexture("_UnlitColorMap", AssetDatabase.LoadAssetAtPath<Texture2D>(moonTexPath));
            moonMat.SetFloat("_EnableFogOnTransparent", 0f);
            HDMaterial.ValidateMaterial(moonMat);
            var moonDisc = Prim(PrimitiveType.Quad, "Disco_de_la_luna", lightRoot, Vector3.zero, Vector3.one, moonMat, null, null, false);
            GameObjectUtility.SetStaticEditorFlags(moonDisc, 0);
            moonDisc.GetComponent<Renderer>().shadowCastingMode = ShadowCastingMode.Off;
            var md = lightRoot.gameObject.AddComponent<SunDisc>();
            md.disc = moonDisc.GetComponent<Renderer>(); md.moon = true; md.angularSizeDeg = 14f; md.distance = 2800f;

            // ---- el sonador ----
            var player = BuildPlayer();

            // ---- camaras ----
            var cams = Group("Camaras");
            var camGo = new GameObject("Camara", typeof(Camera), typeof(AudioListener));
            camGo.transform.SetParent(cams, false);
            camGo.tag = "MainCamera";
            var cam = camGo.GetComponent<Camera>();
            cam.nearClipPlane = 0.05f; cam.farClipPlane = 8000f;
            var hdCam = camGo.AddComponent<HDAdditionalCameraData>();
            hdCam.antialiasing = HDAdditionalCameraData.AntialiasingMode.TemporalAntialiasing;
            // agua, nubes volumetricas, reflejos y sombras de contacto activos en esta camara aunque el valor por
            // defecto del proyecto los tenga apagados
            hdCam.customRenderingSettings = true;
            foreach (var f in new[] { FrameSettingsField.Water, FrameSettingsField.VolumetricClouds, FrameSettingsField.SSR,
                                      FrameSettingsField.ContactShadows, FrameSettingsField.Volumetrics })
            {
                hdCam.renderingPathCustomFrameSettingsOverrideMask.mask[(uint)f] = true;
                hdCam.renderingPathCustomFrameSettings.SetEnabled(f, true);
            }
            var brain = camGo.AddComponent<CinemachineBrain>();
            camGo.AddComponent<FocusPuller>();

            var look = player.GetComponent<FirstPersonLook>();
            var fp = new GameObject("CM_PrimeraPersona").AddComponent<CinemachineCamera>();
            fp.transform.SetParent(look.pivot, false);
            fp.Lens.FieldOfView = 64f; fp.Lens.NearClipPlane = 0.05f; fp.Lens.FarClipPlane = 8000f;

            var modes = cams.gameObject.AddComponent<CameraModeController>();
            modes.brain = brain;
            modes.firstPerson = fp;
            string[] names = { "CM_Cine1_Steadicam", "CM_Cine2_Teleobjetivo", "CM_Cine3_Contrapicado" };
            for (int i = 0; i < 3; i++)
            {
                var c = new GameObject(names[i]).AddComponent<CinemachineCamera>();
                c.transform.SetParent(cams, false);
                c.gameObject.AddComponent<CineRig>().style = (CineStyle)i;
                c.gameObject.SetActive(false);
                modes.cine[i] = c;
            }
            var shot = new GameObject("CM_Rodaje").AddComponent<CinemachineCamera>();
            shot.transform.SetParent(cams, false);
            shot.Lens.NearClipPlane = 0.05f; shot.Lens.FarClipPlane = 8000f;
            shot.gameObject.SetActive(false);
            modes.cinematic = shot;
            director.shotCamera = shot;

            // ---- audio ----
            var audio = Group("Audio");
            var decks = new AudioSource[2];
            for (int i = 0; i < 2; i++)
            {
                var deckGo = new GameObject($"Musica_Plato_{(char)('A' + i)}", typeof(AudioSource), typeof(AudioLowPassFilter), typeof(AudioReverbFilter));
                deckGo.transform.SetParent(audio, false);
                decks[i] = deckGo.GetComponent<AudioSource>();
                decks[i].playOnAwake = false; decks[i].spatialBlend = 0f; decks[i].volume = 0f;
            }
            var ambGo = new GameObject("Ambiente", typeof(AudioSource));
            ambGo.transform.SetParent(audio, false);
            var amb = ambGo.GetComponent<AudioSource>(); amb.playOnAwake = false; amb.loop = true; amb.spatialBlend = 0f;
            var mp = audio.gameObject.AddComponent<MusicPlayer>();
            mp.decks = decks; mp.ambience = amb;
            mp.menu = MusicClip("Menu_");
            mp.playlist = MusicClips("Pista_");
            var sfxGo = new GameObject("Efectos", typeof(AudioSource));
            sfxGo.transform.SetParent(audio, false);
            var sfxSrc = sfxGo.GetComponent<AudioSource>(); sfxSrc.playOnAwake = false; sfxSrc.spatialBlend = 0f;
            var sfxRev = sfxGo.AddComponent<AudioReverbFilter>();
            sfxRev.reverbPreset = AudioReverbPreset.User; sfxRev.dryLevel = -300f; sfxRev.room = -600f; sfxRev.decayTime = 4.2f; sfxRev.reverbLevel = 0f;
            var sfxEcho = sfxGo.AddComponent<AudioEchoFilter>();
            sfxEcho.delay = 420f; sfxEcho.decayRatio = 0.35f; sfxEcho.wetMix = 0.3f; sfxEcho.dryMix = 0.9f;
            sfxGo.AddComponent<SfxPlayer>().source = sfxSrc;

            // ---- interfaz ----
            var ui = Group("Interfaz");
            ui.gameObject.AddComponent<UIRoot>();
            var es = new GameObject("EventSystem", typeof(EventSystem), typeof(InputSystemUIInputModule));
            es.transform.SetParent(ui, false);

            Save(scene, "Boot");
        }

        // Disco del sol: nucleo blanco y un halo que se apaga suave hacia el borde.
        static Texture2D SunTexture()
        {
            string path = TexDir + "/T_Disco_Sol.png";
            const int n = 256;
            var t = new Texture2D(n, n, TextureFormat.RGBA32, false);
            for (int y = 0; y < n; y++)
                for (int x = 0; x < n; x++)
                {
                    float dx = (x - n / 2f + 0.5f) / (n / 2f), dy = (y - n / 2f + 0.5f) / (n / 2f);
                    float r = Mathf.Sqrt(dx * dx + dy * dy);
                    float core = Mathf.Clamp01((0.32f - r) / 0.04f);
                    float halo = Mathf.Pow(Mathf.Clamp01(1f - r), 3f) * 0.18f;
                    float a = Mathf.Clamp01(core + halo);
                    t.SetPixel(x, y, new Color(1f, 1f, 1f, a));
                }
            System.IO.File.WriteAllBytes(System.IO.Path.Combine(System.IO.Directory.GetCurrentDirectory(), path), t.EncodeToPNG());
            Object.DestroyImmediate(t);
            AssetDatabase.ImportAsset(path);
            var imp = (TextureImporter)AssetImporter.GetAtPath(path);
            imp.alphaIsTransparency = true; imp.wrapMode = TextureWrapMode.Clamp; imp.SaveAndReimport();
            return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
        }

        static GameObject BuildPlayer()
        {
            var root = new GameObject("Sonador");
            root.transform.position = Vector3.zero;
            var cc = root.AddComponent<CharacterController>();
            cc.height = 1.7f; cc.radius = 0.26f; cc.center = new Vector3(0, 0.85f, 0);
            var motor = root.AddComponent<PlayerMotor>();
            var look = root.AddComponent<FirstPersonLook>();
            look.pivot = Point("Ojos", root.transform, new Vector3(0, 1.58f, 0.08f));
            var src = root.AddComponent<AudioSource>();
            src.playOnAwake = false; src.spatialBlend = 0f; src.volume = 0.42f;
            // pasos suaves: sin agudos, con una cola de reverb y un eco muy leve
            root.AddComponent<AudioLowPassFilter>().cutoffFrequency = 2600f;
            var stepRev = root.AddComponent<AudioReverbFilter>();
            stepRev.reverbPreset = AudioReverbPreset.User; stepRev.dryLevel = 0f; stepRev.room = -1400f; stepRev.decayTime = 1.6f; stepRev.reverbLevel = -900f;
            var echo = root.AddComponent<AudioEchoFilter>();
            echo.delay = 190f; echo.decayRatio = 0.18f; echo.wetMix = 0.12f; echo.dryMix = 1f;
            var steps = root.AddComponent<FootstepSystem>();
            steps.source = src;
            steps.banks = FootstepBanks(out var land);
            steps.landBank = land;

            var fbx = AssetDatabase.LoadAssetAtPath<GameObject>(SonadorImportPostprocessor.ModelPath);
            var body = (GameObject)PrefabUtility.InstantiatePrefab(fbx);
            body.name = "Cuerpo";
            body.transform.SetParent(root.transform, false);
            var anim = body.GetComponent<Animator>();
            if (!anim) anim = body.AddComponent<Animator>();
            anim.runtimeAnimatorController = AssetDatabase.LoadAssetAtPath<RuntimeAnimatorController>(AnimatorBuilder.ControllerPath);
            anim.applyRootMotion = false;
            body.AddComponent<PlayerAnimatorBridge>().motor = motor;
            body.AddComponent<HeadLook>();
            steps.animator = anim;

            var cloth = Mat("M_Tela_Sonador", new Color(0.78f, 0.77f, 0.75f), 0.22f);
            var rends = body.GetComponentsInChildren<Renderer>();
            foreach (var r in rends) r.sharedMaterials = Enumerable.Repeat(cloth, r.sharedMaterials.Length).ToArray();

            var rig = root.AddComponent<PlayerRig>();
            rig.Motor = motor; rig.Look = look; rig.Anim = body.GetComponent<PlayerAnimatorBridge>(); rig.HeadLook = body.GetComponent<HeadLook>();
            rig.bodyRenderers = rends;
            foreach (var r in rends) r.shadowCastingMode = ShadowCastingMode.ShadowsOnly;
            return root;
        }

        // La musica vive fuera del repositorio (derechos): Menu_*.ogg suena en la pantalla inicial; Pista_*.ogg, en orden, en el viaje.
        static AudioClip[] MusicClips(string prefix)
        {
            const string dir = Root + "/Audio/Music";
            if (!AssetDatabase.IsValidFolder(dir)) return new AudioClip[0];
            return AssetDatabase.FindAssets("t:AudioClip", new[] { dir }).Select(AssetDatabase.GUIDToAssetPath)
                .Where(p => System.IO.Path.GetFileName(p).StartsWith(prefix)).OrderBy(p => p)
                .Select(AssetDatabase.LoadAssetAtPath<AudioClip>).ToArray();
        }

        static AudioClip MusicClip(string prefix) => MusicClips(prefix).FirstOrDefault();

        // Un banco por superficie. Si hay grabaciones en Audio/Footsteps/<Superficie>/ se cargan solas.
        static FootstepBank[] FootstepBanks(out FootstepBank land)
        {
            const string dir = Root + "/Audio/Footsteps";
            EnsureDir(dir + "/Bancos");
            var types = (SurfaceType[])System.Enum.GetValues(typeof(SurfaceType));
            var list = new FootstepBank[types.Length];
            for (int i = 0; i < types.Length; i++) list[i] = Bank(dir, types[i].ToString(), types[i]);
            land = Bank(dir, "Aterrizaje", SurfaceType.Stone);
            return list;
        }

        static FootstepBank Bank(string dir, string folder, SurfaceType type)
        {
            string path = $"{dir}/Bancos/Pasos_{folder}.asset";
            var b = AssetDatabase.LoadAssetAtPath<FootstepBank>(path);
            if (!b) { b = ScriptableObject.CreateInstance<FootstepBank>(); AssetDatabase.CreateAsset(b, path); }
            b.surface = type;
            string clipDir = $"{dir}/{folder}";
            b.clips = AssetDatabase.IsValidFolder(clipDir)
                ? AssetDatabase.FindAssets("t:AudioClip", new[] { clipDir }).Select(g => AssetDatabase.LoadAssetAtPath<AudioClip>(AssetDatabase.GUIDToAssetPath(g))).ToArray()
                : new AudioClip[0];
            EditorUtility.SetDirty(b);
            return b;
        }
    }
}
