using Esneider.Core.Persistence;

namespace Esneider.Core
{
    // 20.1: autorizaciones y condición de salida como flags globales del registro (93/95).
    public static class ObjectiveService
    {
        public const string PermisoServicio = "PERMISO_SERVICIO"; // palanca S1 → D06
        public const string PermisoA = "PERMISO_A";               // panel A → D14
        public const string PermisoB = "PERMISO_B";               // panel B → D22
        public const string BossDefeated = "BOSS_DEFEATED";       // → D28
        public const string PanelExit = "PANEL_EXIT";             // → D29
        public const string Detected = "DETECTADO";               // EVT-C1
        public const string FinalCabinet = "GABINETE_CP06";

        public static bool Has(string flag) => WorldStateRegistry.Session.HasFlag(flag);
        public static bool Grant(string flag) => WorldStateRegistry.Session.SetFlag(flag);

        public static bool DoorAllowed(string doorId)
        {
            switch (doorId)
            {
                case "D06": return Has(PermisoServicio);
                case "D14": return Has(PermisoA);
                case "D22": return Has(PermisoB);
                case "D28A": case "D28B": return Has(BossDefeated);
                case "D29": case "D29-EXT": return Has(BossDefeated) && Has(PanelExit);
                default: return true;
            }
        }
    }
}
