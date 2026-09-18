using System.Collections;
using System.Collections.Generic;
using System.Linq;
using Esneider.Core;
using Esneider.Core.Data;
using Esneider.Core.Persistence;
using Esneider.Player;
using Esneider.World;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem.UI;
using UnityEngine.UI;

namespace Esneider.UI
{
    // 81.2/81.3: pantallas Inicio, Pausa, Derrota, Victoria, Ajustes, Documentos, Mapa y Créditos construidas en código (uGUI),
    // navegables con teclado (foco visible), mundo congelado por GameFlowController (timeScale 0), cursor visible solo con menú abierto.
    // Los ajustes persisten fuera del snapshot (AccessibilitySettings/PlayerPrefs). Nueva partida con guardado pide confirmación concreta.
    public class MenuController : MonoBehaviour
    {
        public static MenuController Instance { get; private set; }
        public static bool SkipTitle; // pruebas automáticas y builds -autotest
        public TextAsset planJson;
        public bool Modal { get; private set; }
        public string Current { get; private set; } = "";
        public bool IsOpen => !string.IsNullOrEmpty(Current);

        Canvas _canvas; Font _font; readonly Dictionary<string, GameObject> _panels = new Dictionary<string, GameObject>();
        PlayerController _pc; GameFlowController _flow; LevelPlan _plan; string _mapFloor = "P01"; Text _docText;
        readonly List<(string label, System.Func<string> value, System.Action<int> change)> _settings = new List<(string, System.Func<string>, System.Action<int>)>();

        void Awake()
        {
            if (Instance != null && Instance != this) { Destroy(gameObject); return; }
            Instance = this; AccessibilitySettings.Load();
            _font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            var cgo = new GameObject("MenuCanvas"); cgo.transform.SetParent(transform);
            _canvas = cgo.AddComponent<Canvas>(); _canvas.renderMode = RenderMode.ScreenSpaceOverlay; _canvas.sortingOrder = 50;
            var scaler = cgo.AddComponent<CanvasScaler>(); scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize; scaler.referenceResolution = new Vector2(1280, 720);
            cgo.AddComponent<GraphicRaycaster>();
            if (FindFirstObjectByType<EventSystem>() == null) { var es = new GameObject("EventSystem"); es.transform.SetParent(transform); es.AddComponent<EventSystem>(); es.AddComponent<InputSystemUIInputModule>(); }
            if (planJson != null) _plan = LevelPlan.FromJson(planJson.text);
        }
        void OnDestroy() { if (Instance == this) Instance = null; }

        IEnumerator Start()
        {
            yield return null;
            _pc = FindFirstObjectByType<PlayerController>(); _flow = GameFlowController.Instance;
            ApplySettings();
            if (_flow != null) _flow.StateChanged += OnState;
            if (!SkipTitle) ShowTitle();
        }

        void OnState(GameState prev, GameState next)
        {
            if (next == GameState.Paused && !IsOpen) ShowPause();
            else if (next == GameState.Playing && IsOpen && !Modal) Hide();
            else if (next == GameState.Dead || next == GameState.Captured) StartCoroutine(DefeatAfter(1.5f));
        }
        IEnumerator DefeatAfter(float s) { yield return new WaitForSecondsRealtime(s); if (_flow != null && (_flow.State == GameState.Dead || _flow.State == GameState.Captured)) ShowDefeat(); }

        // ---------- pantallas ----------
        public void ShowTitle()
        {
            _flow?.SetState(GameState.Paused);
            bool hasSave = CheckpointService.Instance != null && CheckpointService.Instance.Store.HasAnyCandidate;
            var p = Panel("Title", "ESNEIDER — PROTOCOLO LÁZARO", true);
            if (hasSave) Button(p, "Continuar", () => StartCoroutine(ContinueSaved()));
            Button(p, "Nueva partida", () => { if (hasSave) ShowConfirmNew(); else NewGame(); });
            Button(p, "Ajustes", () => ShowSettings("Title"));
            Button(p, "Créditos", ShowCredits);
            Button(p, "Salir", () => Application.Quit());
            Show("Title");
        }
        void ShowConfirmNew()
        {
            var p = Panel("ConfirmNew", "¿Reemplazar el guardado existente? Esta acción borra el progreso guardado.", true);
            Button(p, "Sí, reemplazar y empezar", () => { CheckpointService.Instance?.DeleteSaves(); NewGame(); });
            Button(p, "Cancelar", ShowTitle);
            Show("ConfirmNew");
        }
        void NewGame() { Hide(); if (_flow != null) { if (_flow.State == GameState.Boot) _flow.StartAttempt(); else _flow.SetState(GameState.Playing); } }
        IEnumerator ContinueSaved()
        {
            var cps = CheckpointService.Instance; var data = cps.LoadFromDisk(out var src);
            if (data == null) { Panel("Title", "ESNEIDER — PROTOCOLO LÁZARO\n\nGuardado incompatible o dañado: " + cps.LastNotice, true); ShowTitle(); yield break; }
            Hide(); _flow?.SetState(GameState.Loading);
            if (RegionStreamer.Instance != null) yield return RegionStreamer.Instance.LoadForCheckpoint(data.regionId, data.playerPosition, data.playerYaw);
            cps.RestoreInto(data, _pc);
            if (!string.IsNullOrEmpty(cps.LastNotice)) _pc?.inventory.Notify(cps.LastNotice);
        }

        public void ShowPause()
        {
            var p = Panel("Pause", "PAUSA", false);
            Button(p, "Reanudar", Resume);
            Button(p, "Cargar checkpoint", () => { Hide(); _pc?.Restart(); });
            Button(p, "Mapa", () => ShowMap("Pause"));
            Button(p, "Documentos", () => ShowDocuments("Pause"));
            Button(p, "Ajustes", () => ShowSettings("Pause"));
            Button(p, "Controles", () => ShowControls("Pause"));
            Button(p, "Volver al inicio", ShowTitle);
            Show("Pause");
        }
        public void Resume() { Hide(); if (_flow != null && _flow.State == GameState.Paused) _flow.SetState(GameState.Playing); }

        public void ShowDefeat()
        {
            string cause = _flow == null ? "" : _flow.LastResult == "DERROTA_RED" ? "Capturado: la red de un Vigía inmoviliza y el sistema ejecuta la recuperación." : "Daño letal: rayo u otro ataque.";
            string hint = _flow != null && _flow.deaths >= 3 && !AccessibilitySettings.Assist ? "\n\nSugerencia opcional: activar Asistencia en Ajustes (telegraphs +25 %, rayos −20 %). Nada cambia sin tu selección." : "";
            var p = Panel("Defeat", "DERROTA — " + cause + $"\nSector {_flow?.currentSector} · intentos {_flow?.attempts}" + hint, true);
            Button(p, "Reintentar desde el checkpoint", () => { Hide(); _pc?.Restart(); });
            Button(p, "Ajustes", () => ShowSettings("Defeat"));
            Button(p, "Volver al inicio", ShowTitle);
            Show("Defeat");
        }

        public void ShowVictory()
        {
            var reg = WorldStateRegistry.Session; int docs = reg.Documents.Count();
            string stats = _flow == null ? "" : $"Duración {Mathf.RoundToInt(_flow.attemptTime)} s · muertes {_flow.deaths} · documentos {docs}/12 · unidades neutralizadas {_flow.enemiesKilled} · disparos {_flow.shotsFired}";
            Debug.Log("VICTORIA | " + stats);
            var p = Panel("Victory", "ESCAPE\n" + stats, true);
            Button(p, "Contemplar el exterior", () => { Hide(); Modal = false; });
            Button(p, "Créditos", ShowCredits);
            Button(p, "Volver al inicio", ShowTitle);
            Show("Victory");
        }

        void ShowCredits()
        {
            var p = Panel("Credits", "ESNEIDER — PROTOCOLO LÁZARO\n\nDiseño y documento maestro: el autor del GDD.\nFabricación (Blender + Unity vía MCP), código y pruebas: producción asistida por Claude.\nSíntesis de audio procedural y voz SAPI (Sabina) declaradas en AUDIO_MANIFEST.\nMotor: Unity 6 (URP). Modelado: Blender 5.2.\n\nGracias por jugar.", true);
            Button(p, "Volver", () => { if (_flow != null && _flow.State == GameState.Won) ShowVictory(); else ShowTitle(); });
            Show("Credits");
        }

        void ShowControls(string back)
        {
            var p = Panel("Controls", "CONTROLES\n\nWASD moverse · Shift correr · Ctrl agacharse · Espacio saltar\nRatón mirar · Clic izq. atacar/disparar · R recargar · F linterna\n1/2/3 o rueda cambiar arma · Q curar · E interactuar · Esc pausa\nEnter reintentar tras derrota", false);
            Button(p, "Volver", () => Show(back));
            Show("Controls");
        }

        void ShowSettings(string back)
        {
            _settings.Clear();
            _settings.Add(("Sensibilidad", () => AccessibilitySettings.Sensitivity.ToString("0.00"), d => AccessibilitySettings.Sensitivity = Mathf.Clamp(AccessibilitySettings.Sensitivity + 0.02f * d, 0.04f, 0.40f)));
            _settings.Add(("Invertir eje Y", () => AccessibilitySettings.InvertY ? "Sí" : "No", d => AccessibilitySettings.InvertY = !AccessibilitySettings.InvertY));
            _settings.Add(("FOV vertical", () => AccessibilitySettings.Fov.ToString("0") + "°", d => AccessibilitySettings.Fov = Mathf.Clamp(AccessibilitySettings.Fov + 5f * d, 70f, 100f)));
            _settings.Add(("Tamaño de texto", () => Mathf.RoundToInt(AccessibilitySettings.TextScale * 100) + " %", d => AccessibilitySettings.TextScale = Mathf.Clamp(AccessibilitySettings.TextScale + 0.1f * d, 1f, 1.5f)));
            _settings.Add(("Subtítulos", () => AccessibilitySettings.Subtitles ? "Sí" : "No", d => AccessibilitySettings.Subtitles = !AccessibilitySettings.Subtitles));
            _settings.Add(("Balanceo de cámara", () => AccessibilitySettings.HeadBob ? "Sí" : "No", d => AccessibilitySettings.HeadBob = !AccessibilitySettings.HeadBob));
            _settings.Add(("Asistencia (telegraph +25 %, rayos −20 %)", () => AccessibilitySettings.Assist ? "Activa" : "No", d => AccessibilitySettings.SetAssist(!AccessibilitySettings.Assist)));
            _settings.Add(("Volumen maestro", () => Mathf.RoundToInt(AccessibilitySettings.MasterVolume * 100) + " %", d => AccessibilitySettings.MasterVolume = Mathf.Clamp01(AccessibilitySettings.MasterVolume + 0.1f * d)));
            var p = Panel("Settings", "AJUSTES (se aplican al confirmar; cargar un checkpoint no los revierte)", false);
            foreach (var s in _settings) SettingRow(p, s.label, s.value, s.change);
            Button(p, "Aplicar y volver", () => { AccessibilitySettings.Save(); ApplySettings(); Show(back); });
            Button(p, "Cancelar", () => { AccessibilitySettings.Load(); ApplySettings(); Show(back); });
            Show("Settings");
        }
        public void ApplySettings()
        {
            if (_pc == null) _pc = FindFirstObjectByType<PlayerController>();
            if (_pc != null) { _pc.look.sensitivity = AccessibilitySettings.Sensitivity; _pc.look.invertY = AccessibilitySettings.InvertY; _pc.look.SetFov(AccessibilitySettings.Fov); }
            AudioListener.volume = AccessibilitySettings.MasterVolume;
            var hud = FindFirstObjectByType<HudController>(); if (hud != null) { hud.subtitles = AccessibilitySettings.Subtitles; hud.SetTextScale(AccessibilitySettings.TextScale); }
            var vm = FindFirstObjectByType<ViewmodelController>(); if (vm != null) vm.bobEnabled = AccessibilitySettings.HeadBob;
        }

        void ShowDocuments(string back)
        {
            var reg = WorldStateRegistry.Session; var read = reg.Documents.OrderBy(x => x).ToList();
            var p = Panel("Documents", read.Count == 0 ? "DOCUMENTOS — ninguno leído todavía" : "DOCUMENTOS LEÍDOS", false, 1100, 640);
            var row = new GameObject("Row"); row.transform.SetParent(p.transform, false); var h = row.AddComponent<HorizontalLayoutGroup>(); h.spacing = 12; h.childForceExpandHeight = true; row.AddComponent<LayoutElement>().preferredHeight = 430;
            var list = new GameObject("List"); list.transform.SetParent(row.transform, false); var v = list.AddComponent<VerticalLayoutGroup>(); v.spacing = 4; v.childForceExpandHeight = false; list.AddComponent<LayoutElement>().preferredWidth = 320;
            _docText = Label(row.transform, "Selecciona un documento.", 16, TextAnchor.UpperLeft); _docText.GetComponent<LayoutElement>().preferredWidth = 720;
            foreach (var id in read)
            {
                var d = DocumentLibrary.Get(id); string title = d != null ? $"{id} · {d.title}" : id;
                Button(list.transform, title, () => { _docText.text = d != null ? $"{d.title}\n({d.support})\n\n{d.text}" : id + ": texto no disponible"; }, 16);
            }
            Button(p, "Volver", () => Show(back));
            Show("Documents");
        }

        // 87.3: pestañas P01–P06; norte +Z arriba; solo salas/puertas descubiertas; jugador aproximado en su sala; sin enemigos ni botín
        void ShowMap(string back)
        {
            if (_plan == null && RoomDiscovery.Plan != null) _plan = RoomDiscovery.Plan;
            var p = Panel("Map", "MAPA — norte arriba (+Z)", false, 1100, 660);
            var tabs = new GameObject("Tabs"); tabs.transform.SetParent(p.transform, false); var h = tabs.AddComponent<HorizontalLayoutGroup>(); h.spacing = 6; tabs.AddComponent<LayoutElement>().preferredHeight = 36;
            if (_plan != null) foreach (var f in _plan.floors) { var id = f.id; Button(tabs.transform, id + " " + f.sector, () => { _mapFloor = id; ShowMap(back); }, 15); }
            var area = new GameObject("Area"); area.transform.SetParent(p.transform, false); var img = area.AddComponent<Image>(); img.color = new Color(0.05f, 0.06f, 0.07f, 0.9f); area.AddComponent<LayoutElement>().preferredHeight = 440;
            var areaRt = area.GetComponent<RectTransform>();
            if (_plan != null) DrawFloor(areaRt, _mapFloor);
            Label(p.transform, "Leyenda: ■ sala descubierta · ▲ jugador · puertas: verde abierta, gris cerrada, ámbar autorización requerida, rojo acceso final", 14, TextAnchor.MiddleCenter);
            Button(p, "Volver", () => Show(back));
            Show("Map");
        }
        void DrawFloor(RectTransform area, string floorId)
        {
            var f = _plan.Floor(floorId); if (f == null) return;
            float W = 1040f, H = 430f, s = Mathf.Min(W / f.w, H / f.d); Vector2 off = new Vector2(-f.w * s / 2f, -f.d * s / 2f);
            var reg = WorldStateRegistry.Session;
            Image Rect(string n, float x, float z, float w, float d, Color c) { var g = new GameObject(n); g.transform.SetParent(area, false); var i = g.AddComponent<Image>(); i.color = c; var rt = i.rectTransform; rt.anchorMin = rt.anchorMax = new Vector2(0.5f, 0.5f); rt.pivot = Vector2.zero; rt.anchoredPosition = off + new Vector2(x * s, z * s); rt.sizeDelta = new Vector2(w * s, d * s); return i; }
            Rect("Floor", 0, 0, f.w, f.d, new Color(0.12f, 0.13f, 0.15f));
            var discovered = new HashSet<string>(reg.DiscoveredRooms);
            foreach (var r in _plan.rooms.Where(r => r.floor == floorId))
            {
                bool seen = discovered.Contains(r.id);
                var img = Rect(r.id, r.x, r.z, r.w, r.d, seen ? new Color(0.35f, 0.42f, 0.48f) : new Color(0.16f, 0.17f, 0.19f));
                if (seen) { var t = Label(img.transform, r.name, 12, TextAnchor.MiddleCenter); var trt = t.rectTransform; trt.anchorMin = Vector2.zero; trt.anchorMax = Vector2.one; trt.offsetMin = trt.offsetMax = Vector2.zero; }
            }
            var seenDoors = new HashSet<string>(reg.DiscoveredDoors);
            foreach (var d in _plan.doors.Where(d => d.floor == floorId && seenDoors.Contains(d.id)))
            {
                bool auth = ObjectiveService.DoorAllowed(d.id) == false; bool final = d.id.StartsWith("D28") || d.id.StartsWith("D29");
                bool open = reg.TryGet(LevelPlan.StableGuid("DOOR-" + d.id).ToString(), out var st) && st.isOpen;
                var c = final && !ObjectiveService.DoorAllowed(d.id) ? new Color(0.8f, 0.25f, 0.2f) : auth ? new Color(0.9f, 0.7f, 0.2f) : open ? new Color(0.3f, 0.8f, 0.4f) : new Color(0.6f, 0.6f, 0.6f);
                Rect("Door_" + d.id, d.x - 0.6f, d.z - 0.6f, 1.2f, 1.2f, c);
            }
            var pc = _pc != null ? _pc : FindFirstObjectByType<PlayerController>();
            if (pc != null)
            {
                var o = f.origin.ToVector3(); var lp = pc.transform.position - o;
                if (lp.x >= 0 && lp.x <= f.w && lp.z >= 0 && lp.z <= f.d && Mathf.Abs(lp.y) < f.height + 1f)
                { var m = Rect("Player", lp.x - 0.7f, lp.z - 0.7f, 1.4f, 1.4f, new Color(0.95f, 0.95f, 0.6f)); m.transform.rotation = Quaternion.Euler(0, 0, -pc.transform.eulerAngles.y); }
            }
        }

        // ---------- infraestructura uGUI ----------
        void Show(string name)
        {
            foreach (var kv in _panels) kv.Value.SetActive(kv.Key == name);
            Current = name; Modal = name == "Title" || name == "ConfirmNew" || name == "Defeat" || name == "Victory" || name == "Credits";
            Cursor.lockState = CursorLockMode.None; Cursor.visible = true;
            var first = _panels[name].GetComponentInChildren<Button>();
            if (first != null && EventSystem.current != null) EventSystem.current.SetSelectedGameObject(first.gameObject);
        }
        public void Hide()
        {
            foreach (var kv in _panels) kv.Value.SetActive(false);
            Current = ""; Modal = false;
            if (_flow == null || _flow.State == GameState.Playing) { Cursor.lockState = CursorLockMode.Locked; Cursor.visible = false; }
        }

        GameObject Panel(string name, string title, bool modal, float w = 900f, float h = 560f)
        {
            if (_panels.TryGetValue(name, out var old)) Destroy(old);
            var g = new GameObject("Panel_" + name); g.transform.SetParent(_canvas.transform, false);
            var img = g.AddComponent<Image>(); img.color = new Color(0.02f, 0.025f, 0.03f, 0.92f);
            var rt = g.GetComponent<RectTransform>(); rt.anchorMin = rt.anchorMax = new Vector2(0.5f, 0.5f); rt.sizeDelta = new Vector2(w, h);
            var v = g.AddComponent<VerticalLayoutGroup>(); v.padding = new RectOffset(28, 28, 20, 20); v.spacing = 8; v.childAlignment = TextAnchor.UpperCenter; v.childForceExpandHeight = false; v.childForceExpandWidth = true;
            var t = Label(g.transform, title, 20, TextAnchor.UpperCenter); t.GetComponent<LayoutElement>().preferredHeight = 90;
            _panels[name] = g; g.SetActive(false);
            return g;
        }
        Text Label(Transform parent, string text, int size, TextAnchor align)
        {
            var g = new GameObject("Label"); g.transform.SetParent(parent, false);
            var t = g.AddComponent<Text>(); t.font = _font; t.fontSize = Mathf.RoundToInt(size * AccessibilitySettings.TextScale); t.color = new Color(0.9f, 0.9f, 0.88f); t.alignment = align; t.text = text; t.horizontalOverflow = HorizontalWrapMode.Wrap; t.verticalOverflow = VerticalWrapMode.Overflow;
            g.AddComponent<LayoutElement>().flexibleWidth = 1;
            return t;
        }
        Button Button(GameObject panel, string label, System.Action onClick, int size = 18) => Button(panel.transform, label, onClick, size);
        Button Button(Transform parent, string label, System.Action onClick, int size = 18)
        {
            var g = new GameObject("Btn_" + label); g.transform.SetParent(parent, false);
            var img = g.AddComponent<Image>(); img.color = new Color(0.16f, 0.18f, 0.2f, 1f);
            var b = g.AddComponent<Button>(); var cb = b.colors; cb.highlightedColor = new Color(0.35f, 0.5f, 0.6f); cb.selectedColor = new Color(0.35f, 0.5f, 0.6f); cb.pressedColor = new Color(0.5f, 0.7f, 0.8f); b.colors = cb;
            b.onClick.AddListener(() => onClick());
            g.AddComponent<LayoutElement>().preferredHeight = Mathf.RoundToInt(36 * AccessibilitySettings.TextScale);
            var t = Label(g.transform, label, size, TextAnchor.MiddleCenter); var trt = t.rectTransform; trt.anchorMin = Vector2.zero; trt.anchorMax = Vector2.one; trt.offsetMin = trt.offsetMax = Vector2.zero; Destroy(t.GetComponent<LayoutElement>());
            return b;
        }
        void SettingRow(GameObject panel, string label, System.Func<string> value, System.Action<int> change)
        {
            var row = new GameObject("Row_" + label); row.transform.SetParent(panel.transform, false);
            var h = row.AddComponent<HorizontalLayoutGroup>(); h.spacing = 8; h.childForceExpandWidth = false; h.childAlignment = TextAnchor.MiddleLeft; row.AddComponent<LayoutElement>().preferredHeight = 34;
            var l = Label(row.transform, label, 16, TextAnchor.MiddleLeft); l.GetComponent<LayoutElement>().preferredWidth = 520;
            Text val = null;
            var minus = Button(row.transform, "−", () => { change(-1); val.text = value(); }, 18); minus.GetComponent<LayoutElement>().preferredWidth = 44;
            val = Label(row.transform, value(), 16, TextAnchor.MiddleCenter); val.GetComponent<LayoutElement>().preferredWidth = 120;
            var plus = Button(row.transform, "+", () => { change(1); val.text = value(); }, 18); plus.GetComponent<LayoutElement>().preferredWidth = 44;
        }
    }
}
