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

        // 70.1: objetivos persistentes O01–O11 (no son llaves: las puertas consultan permisos, no objetivos).
        public static string Title(string id) => id switch
        {
            "O01" => "Despertar", "O02" => "Equipo básico", "O03" => "Salir de S1", "O04" => "Pistola", "O05" => "Autorización A",
            "O06" => "Descubrir contención", "O07" => "Escopeta", "O08" => "Autorización B", "O09" => "Alcanzar refugio",
            "O10" => "Derrotar al Archivista", "O11" => "Cruzar exterior", _ => id
        };

        public static bool Complete(string objectiveId)
        {
            if (string.IsNullOrEmpty(objectiveId) || !WorldStateRegistry.Session.CompleteObjective(objectiveId)) return false;
            var hud = UnityEngine.Object.FindFirstObjectByType<UI.HudController>();
            hud?.ShowMessage("Objetivo cumplido: " + Title(objectiveId), 3.5f);
            return true;
        }

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
