using System.Collections.Generic;

namespace Esneider.Core.Persistence
{
    // 89.3: validación semántica. No repara inventando; salud/permisos/consumibles incoherentes rechazan el candidato.
    public static class SaveValidator
    {
        public const int MaxHp = 90, PistolMag = 12, PistolReserve = 80, ShotgunMag = 6, ShotgunReserve = 36, MaxSyringes = 3, MaxRations = 2;

        public static (bool ok, string reason) Validate(SaveData d)
        {
            if (d == null) return (false, "nulo");
            if (string.IsNullOrEmpty(d.checkpointId)) return (false, "sin checkpointId");
            bool final = d.checkpointId == "CP-07" || d.campaignWon;
            if (d.health < (final ? 0 : 1) || d.health > MaxHp) return (false, $"salud {d.health} fuera de 1–{MaxHp}");
            if (d.pistolMag < 0 || d.pistolMag > PistolMag || d.pistolReserve < 0 || d.pistolReserve > PistolReserve) return (false, "munición pistola fuera de capacidad");
            if (d.shotgunMag < 0 || d.shotgunMag > ShotgunMag || d.shotgunReserve < 0 || d.shotgunReserve > ShotgunReserve) return (false, "munición escopeta fuera de capacidad");
            if (d.syringeCount < 0 || d.syringeCount > MaxSyringes || d.rationCount < 0 || d.rationCount > MaxRations) return (false, "curas fuera de 0–3/0–2");
            if (!d.hasPistol && (d.pistolMag > 0)) return (false, "cargador de pistola sin pistola");
            if (!d.hasShotgun && (d.shotgunMag > 0)) return (false, "cargador de escopeta sin escopeta");
            if (float.IsNaN(d.playerPosition.x) || float.IsNaN(d.playerPosition.y) || float.IsNaN(d.playerPosition.z) || float.IsInfinity(d.playerPosition.magnitude)) return (false, "posición NaN/Infinity");
            if (d.shotsFired < 0 || d.kills < 0 || d.collisionImpacts < 0 || d.elapsedPlaySeconds < 0) return (false, "estadísticas negativas");
            if (d.world == null) return (false, "sin registro de mundo");
            var seen = new HashSet<string>();
            foreach (var e in d.world.entities)
            {
                if (string.IsNullOrEmpty(e.guid)) return (false, "entidad sin GUID");
                if (!seen.Add(e.guid)) return (false, "GUID duplicado " + e.guid);
                if ((e.kind == EntityKind.Enemy || e.kind == EntityKind.Boss) && e.hp >= 0f)
                {
                    if (e.hp <= 0f && !e.dead) return (false, $"{e.guid}: HP 0 sin muerto");
                    if (e.dead && e.hp > 0f) return (false, $"{e.guid}: muerto con HP>0");
                }
                if (e.kind == EntityKind.Pickup && e.taken && e.amount > 0) return (false, $"{e.guid}: recogido con cantidad positiva");
            }
            if (d.bossDefeated != d.world.flags.Contains("BOSS_DEFEATED")) return (false, "bossDefeated no concuerda con flag");
            if (d.world.flags.Contains("DOOR_D29_OPEN") && !d.bossDefeated) return (false, "D29 abierta sin jefe derrotado");
            return (true, "");
        }
    }
}
