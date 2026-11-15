using Dream.Cinematic;
using UnityEngine;
using UnityEngine.UI;

namespace Dream.UI
{
    // Arma toda la interfaz al arrancar: HUD, intro, pausa, final, bandas de cine y fundido. Asi Boot no depende de
    // prefabs de UI hechos a mano y todo se puede leer en codigo.
    [DefaultExecutionOrder(-70)]
    public class UIRoot : MonoBehaviour
    {
        void Awake()
        {
            var hud = UIKit.Canvas(transform, "HUD", 10);
            hud.gameObject.AddComponent<HudView>().Build();

            var cine = UIKit.Canvas(transform, "Bandas", 20);
            var lb = cine.gameObject.AddComponent<Letterbox>();
            lb.top = UIKit.Panel(cine.transform, "Arriba", Color.black).rectTransform;
            lb.bottom = UIKit.Panel(cine.transform, "Abajo", Color.black).rectTransform;
            if (CameraModeController.Instance) CameraModeController.Instance.letterbox = lb;
            else { var cm = FindAnyObjectByType<CameraModeController>(); if (cm) cm.letterbox = lb; }

            var menus = UIKit.Canvas(transform, "Menus", 30);
            menus.gameObject.AddComponent<IntroPanel>().Build();
            menus.gameObject.AddComponent<PauseMenu>().Build();
            menus.gameObject.AddComponent<EndPanel>().Build();

            var fadeCanvas = UIKit.Canvas(transform, "Fundido", 40);
            var img = UIKit.Panel(fadeCanvas.transform, "Velo", new Color(0, 0, 0, 0));
            var fader = fadeCanvas.gameObject.AddComponent<ScreenFader>();
            fader.image = img;
            fader.Set(Color.black, 0f);
        }
    }
}
