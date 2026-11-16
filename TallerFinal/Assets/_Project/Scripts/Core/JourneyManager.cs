using System.Collections;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Dream
{
    // Viaje lineal por los 8 escenarios. Boot queda siempre cargado; cada escenario entra en aditivo mientras la
    // cinematica tapa la carga, y el anterior se descarga. Al terminar el 7 se vuelve al cuarto: es el bucle.
    public class JourneyManager : MonoBehaviour
    {
        public static JourneyManager Instance { get; private set; }

        public static readonly string[] Scenes =
            { "S1_Cuarto", "S2_Pradera", "S3_Colina", "S4_Jardin", "S5_Pasillo", "S6_Playa", "S7_Piscina", "S8_Escalera" };

        public int Current { get; private set; } = -1;
        public bool InFinale { get; private set; }
        public SceneAnchor Anchor { get; private set; }
        public float SecondsInScene { get; private set; }
        public bool Busy { get; private set; }

        [Tooltip("Para probar: con que escenario empieza (0 = cuarto)")] public int startAt;

        string _pendingHint;

        void Awake() => Instance = this;
        void OnDestroy() { if (Instance == this) Instance = null; }

        // la pista del escenario aparece cuando el jugador recupera el control, no durante la cinematica
        void LateUpdate()
        {
            if (string.IsNullOrEmpty(_pendingHint) || Busy) return;
            if (GameFlow.Instance && GameFlow.Instance.State == GameState.Playing)
            {
                UI.HudView.Instance?.ShowHint(_pendingHint);
                _pendingHint = null;
            }
        }

        void Update()
        {
            if (Anchor == null || InFinale || (GameFlow.Instance && GameFlow.Instance.Lingering)) return;   // 3:33: el tiempo no avanza
            SecondsInScene += Time.deltaTime;
            // la hora avanza sola dentro del escenario, de su hora de inicio a la de cierre
            var tod = TimeOfDay.Instance;
            if (tod != null && GameFlow.Instance != null && GameFlow.Instance.State == GameState.Playing)
            {
                float f = Mathf.Clamp01(SecondsInScene / Mathf.Max(1f, Anchor.minutesToEndHour * 60f));
                float h = Mathf.Lerp(Anchor.startHour, Anchor.endHour, f);
                if (h > tod.hour) tod.hour = h;
            }
            var p = PlayerRig.Instance;
            bool playing = GameFlow.Instance == null || GameFlow.Instance.State == GameState.Playing;
            if (p != null && !Busy && playing && p.transform.position.y < Anchor.respawnBelowY) p.Respawn();
        }

        public void Begin() => StartCoroutine(BeginRoutine());

        IEnumerator BeginRoutine()
        {
            Busy = true;
            yield return LoadIndex(Mathf.Clamp(startAt, 0, Scenes.Length - 1), false);
            Busy = false;
            if (Anchor && Anchor.arrival) yield return Cinematic.CinematicDirector.Instance.PlayArrival(Anchor.arrival);
        }

        public bool NextIsFinale => Current == Scenes.Length - 1 && !InFinale;

        // Lo llama CinematicDirector entre la cinematica de salida y la de llegada.
        public IEnumerator LoadNext()
        {
            Busy = true;
            if (NextIsFinale) yield return LoadIndex(0, true);
            else yield return LoadIndex(Current + 1, false);
            Busy = false;
        }

        IEnumerator LoadIndex(int i, bool finale)
        {
            string prev = Current >= 0 ? Scenes[Current] : null;
            if (prev == Scenes[i])
            {
                yield return SceneManager.UnloadSceneAsync(prev);   // volver al mismo cuarto: se recarga limpio
                prev = null;
            }
            var loaded = SceneManager.GetSceneByName(Scenes[i]);
            if (!loaded.isLoaded)
            {
                var op = SceneManager.LoadSceneAsync(Scenes[i], LoadSceneMode.Additive);
                while (!op.isDone) yield return null;
                loaded = SceneManager.GetSceneByName(Scenes[i]);
            }
            SceneManager.SetActiveScene(loaded);
            if (prev != null && SceneManager.GetSceneByName(prev).isLoaded) yield return SceneManager.UnloadSceneAsync(prev);
            yield return null;   // un frame para que los OnEnable registren el anchor

            Current = i; InFinale = finale; SecondsInScene = 0f;
            Anchor = SceneAnchor.Find(i);
            if (Anchor == null) { Debug.LogError($"La escena {Scenes[i]} no tiene SceneAnchor con index {i}"); yield break; }
            Anchor.memoryCollected = false;
            if (Anchor.dayOnly) Anchor.dayOnly.SetActive(!finale);
            if (Anchor.nightOnly) Anchor.nightOnly.SetActive(finale);

            var spawn = finale && Anchor.finaleSpawn ? Anchor.finaleSpawn : Anchor.spawn;
            var rig = PlayerRig.Instance;
            if (rig != null)
            {
                rig.PlaceAt(spawn);
                rig.Motor.SetFlightAllowed(Anchor.allowFlight && !finale);
                if (Anchor.startFlying && !finale) rig.Motor.SetFlying(true);
            }
            _pendingHint = finale ? null : Anchor.arrivalHint;
            if (TimeOfDay.Instance) TimeOfDay.Instance.GoTo(finale ? 0f : Anchor.startHour, 0f);
            Audio.MusicPlayer.Instance?.ApplyScene(Anchor);
            ScoreSystem.Instance?.MarkSceneStart();
        }

        public void OnMemoryCollected()
        {
            if (Anchor) Anchor.memoryCollected = true;
        }

        public void FinishJourney()
        {
            ScoreSystem.Instance?.Lock();
            GameFlow.Instance?.SetState(GameState.Ended);
        }
    }
}
