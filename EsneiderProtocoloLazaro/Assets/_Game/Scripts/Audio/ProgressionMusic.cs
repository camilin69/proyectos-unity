using Esneider.Core;
using Esneider.Core.Persistence;
using UnityEngine;

namespace Esneider.Audio
{
    public class ProgressionMusic : MonoBehaviour
    {
        public static ProgressionMusic Instance { get; private set; }
        public int Stage { get; private set; } = -2;
        readonly AudioClip[] tracks = new AudioClip[5];
        readonly AudioSource[] sources = new AudioSource[2];
        int current; float poll;
        public bool IsSilent => sources[0] != null && !sources[0].isPlaying && !sources[1].isPlaying;
        public string CurrentTrackName => sources[current] != null && sources[current].clip != null ? sources[current].clip.name : "";
        public float CurrentVolume => sources[current] != null ? sources[current].volume : 0f;

        void Awake() { Instance = this; }
        void Start()
        {
            var service = GetComponent<AudioService>();
            for (int i = 0; i < tracks.Length; i++) tracks[i] = Resources.Load<AudioClip>("Music/Tension" + i);
            for (int i = 0; i < sources.Length; i++)
            {
                var go = new GameObject("Score_" + i); go.transform.SetParent(transform, false);
                var source = go.AddComponent<AudioSource>(); source.playOnAwake = false; source.loop = true; source.spatialBlend = 0;
                source.outputAudioMixerGroup = service.ambient; source.volume = 0; source.priority = 160; sources[i] = source;
            }
            var explosion = Resources.Load<AudioClip>("Music/RobotExplosion");
            if (explosion != null) service.RegisterBank("SND-ROBOT-Explosion", new[] { explosion });
        }

        public static int ResolveStage(string region)
        {
            var registry = WorldStateRegistry.Session;
            if (ObjectiveService.Has(ObjectiveService.BossDefeated)) return -1;
            if (registry.IsEventDone("EVT-21")) return 4;
            int stage = region == "REG-S4" || region == "REG-C3" ? 3 : region == "REG-S3" || region == "REG-C2" ? 2 : region == "REG-S2" || region == "REG-C1" ? 1 : 0;
            for (int i = 1; i <= 3; i++) if (registry.HasFlag("MUSIC_STAGE_" + i)) stage = Mathf.Max(stage, i);
            if (stage == 0 && !registry.HasFlag("OPENING_DONE")) return -2;
            return stage;
        }

        public static void DoorOpened(string id)
        {
            int stage = id == "D06" ? 1 : id == "D14" ? 2 : id == "D22" || id == "D27" ? 3 : 0;
            if (stage > 0)
            {
                WorldStateRegistry.Session.SetFlag("MUSIC_STAGE_" + stage);
                Instance?.RefreshNow();
            }
        }

        public void RefreshNow()
        {
            int desired = ResolveStage(World.RegionStreamer.Instance != null ? World.RegionStreamer.Instance.CurrentRegion : "REG-S1");
            // Progression only grows during a run. Explicit silence states still reset it for
            // a new game/opening (-2) or after defeating the boss (-1).
            if (desired >= 0 && Stage >= 0) desired = Mathf.Max(desired, Stage);
            if (desired == Stage) return;
            Stage = desired;
            if (Stage < 0) { foreach (var source in sources) if (source != null) { source.Stop(); source.volume = 0; } return; }
            current = 1 - current;
            var incoming = sources[current]; if (incoming == null) return;
            incoming.Stop(); incoming.clip = tracks[Stage]; incoming.volume = 0;
            if (incoming.clip != null) incoming.Play();
        }

        void Update()
        {
            if (sources[0] == null) return;
            if (Time.unscaledTime >= poll) { poll = Time.unscaledTime + .15f; RefreshNow(); }
            var flow = GameFlowController.Instance;
            bool paused = Time.timeScale == 0 || (flow != null && !flow.GameplayActive);
            for (int i = 0; i < sources.Length; i++)
            {
                if (paused) { sources[i].Pause(); continue; }
                sources[i].UnPause();
                // Each gate raises both musical density (separate track) and loudness. A faster
                // crossfade makes the crescendo perceptible when the difficult door opens.
                float target = Stage >= 0 && i == current ? .38f + Stage * .08f : 0;
                sources[i].volume = Mathf.MoveTowards(sources[i].volume, target, Time.deltaTime * .55f);
                if (target == 0 && sources[i].volume <= 0) sources[i].Stop();
            }
        }
        void OnDestroy() { if (Instance == this) Instance = null; }
    }
}
