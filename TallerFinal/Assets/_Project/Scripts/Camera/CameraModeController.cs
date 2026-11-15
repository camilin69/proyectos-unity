using System;
using System.Collections;
using Unity.Cinemachine;
using UnityEngine;

namespace Dream
{
    // Tecla F: primera persona -> Cine 1 -> Cine 2 -> Cine 3 -> primera persona. Se activa una sola camara virtual
    // y el Brain mezcla con ease in-out de 1,5 s. En cine aparecen las bandas 2.39:1 y el cuerpo se ve entero.
    public class CameraModeController : MonoBehaviour
    {
        public static CameraModeController Instance { get; private set; }

        public CinemachineBrain brain;
        public CinemachineCamera firstPerson;
        public CinemachineCamera[] cine = new CinemachineCamera[3];
        public CinemachineCamera cinematic;
        public Letterbox letterbox;
        public float blendSeconds = 1.5f;

        public int Mode { get; private set; }
        public bool InCinematic { get; private set; }
        public bool ShowingBody => Mode != 0 || InCinematic;
        public event Action Changed;

        Coroutine _hideBody;

        void Awake()
        {
            Instance = this;
            if (brain) brain.DefaultBlend = new CinemachineBlendDefinition(CinemachineBlendDefinition.Styles.EaseInOut, blendSeconds);
        }

        void OnDestroy() { if (Instance == this) Instance = null; }

        void Start() => Apply();

        void Update()
        {
            var input = DreamInput.Instance;
            if (input == null || InCinematic) return;
            if (GameFlow.Instance != null && GameFlow.Instance.State != GameState.Playing) return;
            if (input.ConsumeCamera()) { Mode = (Mode + 1) % 4; Apply(); }
        }

        void Activate(CinemachineCamera cam)
        {
            firstPerson.gameObject.SetActive(cam == firstPerson);
            foreach (var c in cine) if (c) c.gameObject.SetActive(c == cam);
            if (cinematic) cinematic.gameObject.SetActive(cam == cinematic);
        }

        public void Apply()
        {
            var cam = Mode == 0 ? firstPerson : cine[Mode - 1];
            Activate(cam);
            if (letterbox) letterbox.Show(Mode != 0);
            SetBody(Mode != 0);
            Changed?.Invoke();
        }

        void SetBody(bool visible)
        {
            var rig = PlayerRig.Instance;
            if (!rig) return;
            if (_hideBody != null) { StopCoroutine(_hideBody); _hideBody = null; }
            if (visible) rig.SetBodyVisible(true);
            else _hideBody = StartCoroutine(HideBodyAfterBlend(rig));
        }

        // Al volver a primera persona el cuerpo se oculta cuando la mezcla ya casi llego a los ojos.
        IEnumerator HideBodyAfterBlend(PlayerRig rig)
        {
            yield return new WaitForSeconds(blendSeconds * 0.75f);
            rig.SetBodyVisible(false);
            _hideBody = null;
        }

        public void SetCut(bool cut) =>
            brain.DefaultBlend = cut ? new CinemachineBlendDefinition(CinemachineBlendDefinition.Styles.Cut, 0f)
                                     : new CinemachineBlendDefinition(CinemachineBlendDefinition.Styles.EaseInOut, blendSeconds);

        public void EnterCinematic()
        {
            InCinematic = true;
            Activate(cinematic);
            if (letterbox) letterbox.Show(true);
            SetBody(true);
            Changed?.Invoke();
        }

        public void ExitCinematic()
        {
            InCinematic = false;
            Mode = 0;
            Apply();
        }
    }
}
