using UnityEngine;
using UnityEngine.SceneManagement;

namespace Dream
{
    // Para probar un escenario suelto: si se da Play directamente en S3_Colina, se carga Boot encima y el viaje
    // empieza en ese escenario, sin pasar por la intro.
    public static class DevBoot
    {
        public static int PendingStart = -1;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        static void Init()
        {
            var active = SceneManager.GetActiveScene().name;
            int i = System.Array.IndexOf(JourneyManager.Scenes, active);
            if (i < 0 || Object.FindAnyObjectByType<GameFlow>() != null) return;
            PendingStart = i;
            SceneManager.LoadScene("Boot", LoadSceneMode.Additive);
        }
    }
}
