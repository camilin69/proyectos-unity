using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace Esneider.Core.Data
{
    // Sección 95.2: rechaza duplicados, rangos inválidos y verifica las equivalencias de balance del GDD.
    public static class DataValidator
    {
        public class Report
        {
            public readonly List<string> errors = new List<string>();
            public readonly List<string> warnings = new List<string>();
            public bool Passed => errors.Count == 0;
            public override string ToString() =>
                $"DataValidator: {(Passed ? "PASA" : "FALLA")} · {errors.Count} errores · {warnings.Count} avisos\n" +
                string.Join("\n", errors.Select(e => "  [E] " + e).Concat(warnings.Select(w => "  [W] " + w)));
        }

        public static Report Validate(GameDataCatalog c)
        {
            var r = new Report();
            if (c == null) { r.errors.Add("Catálogo nulo"); return r; }

            CheckDuplicateIds(r, "weapons", c.weapons.Select(w => w != null ? w.id : null));
            CheckDuplicateIds(r, "enemies", c.enemies.Select(e => e != null ? e.id : null));
            CheckDuplicateIds(r, "surfaces", c.surfaces.Select(s => s != null ? s.id : null));
            CheckDuplicateIds(r, "regions", c.regions.Select(x => x != null ? x.id : null));
            CheckDuplicateIds(r, "events", c.events.Select(x => x != null ? x.id : null));
            CheckDuplicateIds(r, "checkpoints", c.checkpoints.Select(x => x != null ? x.id : null));
            CheckDuplicateIds(r, "region guids", c.regions.Select(x => x != null ? x.guid : null));

            if (c.player == null) r.errors.Add("PlayerDefinition ausente");
            else
            {
                if (c.player.maxHp != 90) r.warnings.Add($"Player HP {c.player.maxHp} ≠ 90 (103.1)");
                if (c.player.invulnerabilitySeconds <= 0) r.errors.Add("Invulnerabilidad ≤ 0");
                if (c.player.syringeCommit > c.player.syringeDuration || c.player.rationCommit > c.player.rationDuration)
                    r.errors.Add("Commit de curación fuera de la duración");
                if (c.player.fovVertical < c.player.fovMin || c.player.fovVertical > c.player.fovMax) r.errors.Add("FOV fuera de rango");
            }

            foreach (var w in c.weapons.Where(w => w != null))
            {
                if (w.damage <= 0) r.errors.Add($"{w.id}: daño ≤ 0");
                if (w.pellets <= 0) r.errors.Add($"{w.id}: pellets ≤ 0");
                if (w.activeEnd > w.attackCycle || w.activeStart > w.activeEnd) r.errors.Add($"{w.id}: ventana activa fuera del ciclo");
                if (w.reloadCommit > w.reloadDuration) r.errors.Add($"{w.id}: commit de recarga fuera de duración");
                if (w.shellInsertCommit > w.shellInsert) r.errors.Add($"{w.id}: commit de inserción fuera de duración");
                if (w.kind != WeaponKind.Melee && w.magazineSize <= 0) r.errors.Add($"{w.id}: cargador ≤ 0");
                if (w.kind == WeaponKind.Shotgun && !Approximately(w.damage * w.pellets, 60f)) r.warnings.Add($"{w.id}: escopeta máxima {w.damage * w.pellets} ≠ 60 (103.1)");
            }

            var melee = c.weapons.FirstOrDefault(w => w != null && w.kind == WeaponKind.Melee);
            var pistol = c.weapons.FirstOrDefault(w => w != null && w.kind == WeaponKind.Pistol);
            var vigia = c.enemies.FirstOrDefault(e => e != null && e.kind == EnemyKind.Vigia);
            var custodio = c.enemies.FirstOrDefault(e => e != null && e.kind == EnemyKind.Custodio);
            if (melee == null) r.errors.Add("Sin arma melee (varilla)");
            if (vigia == null || custodio == null) r.errors.Add("Faltan definiciones de Vigía/Custodio");
            if (melee != null && vigia != null && Hits(vigia.maxHp, melee.damage) != 3) r.errors.Add($"Vigía {vigia.maxHp}/{melee.damage} ≠ 3 golpes");
            if (melee != null && custodio != null && Hits(custodio.maxHp, melee.damage) != 6) r.errors.Add($"Custodio {custodio.maxHp}/{melee.damage} ≠ 6 golpes");
            if (custodio != null && c.player != null && Hits(c.player.maxHp, custodio.attackDamage) != 3) r.errors.Add($"Rayos para matar {c.player.maxHp}/{custodio.attackDamage} ≠ 3");
            if (custodio != null && custodio.attackDamage != 30) r.warnings.Add("Rayo del Custodio ≠ 30");

            if (c.boss == null) r.errors.Add("BossDefinition ausente");
            else
            {
                if (c.boss.maxHp != 1200) r.warnings.Add($"Boss HP {c.boss.maxHp} ≠ 1200");
                if (!(c.boss.maxHp > c.boss.phase2Threshold && c.boss.phase2Threshold > c.boss.phase3Threshold && c.boss.phase3Threshold > 0))
                    r.errors.Add("Umbrales de fase del boss no ordenados");
                if (c.boss.attacks.Count == 0) r.errors.Add("Boss sin ataques");
                foreach (var a in c.boss.attacks) if (a.damage <= 0 || a.telegraph <= 0) r.errors.Add($"Boss ataque {a.id}: valores ≤ 0");
                if (melee != null && Hits(c.boss.maxHp, melee.damage) != 60) r.warnings.Add("Boss/varilla ≠ 60 golpes");
                if (pistol != null && Hits(c.boss.maxHp, pistol.damage) != 40) r.warnings.Add("Boss/pistola ≠ 40 disparos");
            }

            foreach (var cp in c.checkpoints.Where(x => x != null))
            {
                if (cp.id == "CP-06")
                {
                    if (!cp.isShelter) r.errors.Add("CP-06 debe ser refugio");
                    if (pistol != null && cp.guaranteePistolTotal > pistol.magazineSize + pistol.reserveMax) r.errors.Add("Garantía CP-06 pistola > capacidad");
                    var sg = c.weapons.FirstOrDefault(w => w != null && w.kind == WeaponKind.Shotgun);
                    if (sg != null && cp.guaranteeShotgunTotal > sg.magazineSize + sg.reserveMax) r.errors.Add("Garantía CP-06 escopeta > capacidad");
                }
                if (string.IsNullOrEmpty(cp.guid)) r.errors.Add($"{cp.id}: sin GUID");
            }

            foreach (var reg in c.regions.Where(x => x != null))
                if (reg.height <= 0 || reg.localRect.width <= 0 || reg.localRect.height <= 0) r.errors.Add($"{reg.id}: rectángulo/altura inválidos");

            foreach (var s in c.surfaces.Where(x => x != null))
                if (s.staticFriction < 0 || s.dynamicFriction < 0 || s.dynamicFriction > s.staticFriction) r.errors.Add($"{s.id}: fricción inválida");

            if (c.difficulties.Count == 0 || !c.difficulties.Any(d => d != null && d.presetName == "Normal")) r.errors.Add("Falta preset Normal");
            if (c.levelPlanJson == null) r.errors.Add("Catálogo sin bunker_plan.json");
            return r;
        }

        public static Report ValidatePlan(LevelPlan p)
        {
            var r = new Report();
            if (p == null) { r.errors.Add("Plano nulo"); return r; }
            CheckDuplicateIds(r, "rooms", p.rooms.Select(x => x.id));
            CheckDuplicateIds(r, "doors", p.doors.Select(x => x.id));
            CheckDuplicateIds(r, "spawns", p.spawns.Select(x => x.id));
            CheckDuplicateIds(r, "pickups", p.pickups.Select(x => x.id));
            CheckDuplicateIds(r, "checkpoints", p.checkpoints.Select(x => x.id));
            CheckDuplicateIds(r, "documents", p.documents.Select(x => x.id));

            // 68.2: ninguna pareja de habitaciones de una misma planta comparte interior.
            foreach (var f in p.floors)
            {
                var rs = p.rooms.Where(x => x.floor == f.id).ToList();
                for (int i = 0; i < rs.Count; i++)
                {
                    if (rs[i].x < 0 || rs[i].z < 0 || rs[i].x + rs[i].w > f.w || rs[i].z + rs[i].d > f.d) r.errors.Add($"{rs[i].id} fuera de la envolvente de {f.id}");
                    for (int j = i + 1; j < rs.Count; j++)
                        if (Overlaps(rs[i], rs[j])) r.errors.Add($"Solape interior {rs[i].id} / {rs[j].id}");
                }
            }

            // 68.4: cada puerta con habitación debe estar sobre el borde declarado.
            foreach (var d in p.doors)
            {
                if (string.IsNullOrEmpty(d.room)) continue;
                var room = p.Room(d.room);
                if (room == null) { r.errors.Add($"{d.id}: habitación {d.room} inexistente"); continue; }
                bool ok = d.edge switch
                {
                    "E" => Approximately(d.x, room.x + room.w) && d.z >= room.z && d.z <= room.z + room.d,
                    "W" => Approximately(d.x, room.x) && d.z >= room.z && d.z <= room.z + room.d,
                    "N" => Approximately(d.z, room.z + room.d) && d.x >= room.x && d.x <= room.x + room.w,
                    "S" => Approximately(d.z, room.z) && d.x >= room.x && d.x <= room.x + room.w,
                    _ => false
                };
                if (!ok) r.errors.Add($"{d.id}: centro ({d.x},{d.z}) no está en el borde {d.edge} de {room.id}");
            }

            // 68.5: el fin de cada conector coincide con la puerta destino en mundo.
            foreach (var c in p.connectors)
            {
                var to = p.Door(c.toDoor); var from = p.Door(c.fromDoor);
                if (to == null || from == null) { r.errors.Add($"{c.id}: puertas extremas inexistentes"); continue; }
                var last = c.points[c.points.Count - 1];
                var endWorld = c.origin.ToVector3() + new Vector3(last.x, 0, last.z);
                if (!p.TryToWorld(to.floor, to.x, to.z, out var doorWorld)) continue;
                if (Vector3.Distance(endWorld, doorWorld) > 0.01f) r.errors.Add($"{c.id}: fin {endWorld} ≠ {to.id} {doorWorld}");
                float len = 0; for (int i = 1; i < c.points.Count; i++) len += Mathf.Abs(c.points[i].x - c.points[i - 1].x) + Mathf.Abs(c.points[i].z - c.points[i - 1].z);
                if (!Approximately(len, c.length)) r.warnings.Add($"{c.id}: longitud polilínea {len} ≠ nominal {c.length}");
            }

            // Cada spawn/pickup/checkpoint apunta a un espacio existente y cae dentro de alguna superficie transitable.
            foreach (var s in p.spawns) CheckPoint(r, p, s.id, s.space, s.x, s.z);
            foreach (var s in p.pickups) CheckPoint(r, p, s.id, s.space, s.x, s.z);
            foreach (var s in p.checkpoints) CheckPoint(r, p, s.id, s.space, s.x, s.z);
            foreach (var s in p.documents) CheckPoint(r, p, s.id, s.space, s.x, s.z);

            // 68.8: stock de munición antes del gabinete.
            int pistolAmmo = p.pickups.Where(x => x.kind == "PistolAmmo" || x.kind == "Pistol").Sum(x => x.amount);
            int shotgunAmmo = p.pickups.Where(x => x.kind == "ShotgunAmmo" || x.kind == "Shotgun").Sum(x => x.amount);
            if (pistolAmmo != 140) r.errors.Add($"Stock balas {pistolAmmo} ≠ 140");
            if (shotgunAmmo != 50) r.errors.Add($"Stock cartuchos {shotgunAmmo} ≠ 50");
            int v = p.spawns.Count(x => x.kind == "Vigia"), k = p.spawns.Count(x => x.kind == "Custodio"), b = p.spawns.Count(x => x.kind == "Boss");
            if (v != 23 || k != 14 || b != 1) r.errors.Add($"Población {v}V/{k}K/{b}B ≠ 23/14/1");
            if (p.pickups.Count(x => x.kind == "Syringe") != 12 || p.pickups.Count(x => x.kind == "Ration") != 6) r.errors.Add("Curaciones ≠ 12 jeringas / 6 raciones");
            return r;
        }

        static void CheckPoint(Report r, LevelPlan p, string id, string space, float x, float z)
        {
            var f = p.Floor(space);
            if (f != null)
            {
                bool inside = p.rooms.Any(rm => rm.floor == space && rm.Contains(x, z)) ||
                              p.circulation.Any(c => c.floor == space && c.Contains(x, z)) ||
                              p.stairs.Any(s => (s.lowerFloor == space || s.upperFloor == space) && s.Contains(x, z));
                if (!inside) r.warnings.Add($"{id}: ({x},{z}) en {space} no cae en habitación/circulación (revisar en blockout)");
                return;
            }
            var c2 = p.Connector(space);
            if (c2 != null)
            {
                float half = c2.width / 2f + 0.01f; bool near = false;
                for (int i = 1; i < c2.points.Count; i++)
                    if (DistanceToSegment(x, z, c2.points[i - 1], c2.points[i]) <= half) { near = true; break; }
                if (!near && !c2.alcoves.Any(a => a.Contains(x, z))) r.warnings.Add($"{id}: ({x},{z}) fuera de la banda de {space}");
                return;
            }
            r.errors.Add($"{id}: espacio {space} inexistente");
        }

        static float DistanceToSegment(float px, float pz, PlanPoint a, PlanPoint b)
        {
            float dx = b.x - a.x, dz = b.z - a.z; float len2 = dx * dx + dz * dz;
            float t = len2 <= 0 ? 0 : Mathf.Clamp01(((px - a.x) * dx + (pz - a.z) * dz) / len2);
            float cx = a.x + t * dx, cz = a.z + t * dz;
            return Mathf.Sqrt((px - cx) * (px - cx) + (pz - cz) * (pz - cz));
        }

        static bool Overlaps(PlanRect a, PlanRect b) => a.x < b.x + b.w && b.x < a.x + a.w && a.z < b.z + b.d && b.z < a.z + a.d;
        static bool Approximately(float a, float b) => Mathf.Abs(a - b) < 0.001f;
        static int Hits(int hp, float dmg) => dmg <= 0 ? -1 : Mathf.CeilToInt(hp / dmg - 0.0001f);

        static void CheckDuplicateIds(Report r, string set, IEnumerable<string> ids)
        {
            var seen = new HashSet<string>();
            foreach (var id in ids)
            {
                if (string.IsNullOrEmpty(id)) { r.errors.Add($"{set}: ID vacío"); continue; }
                if (!seen.Add(id)) r.errors.Add($"{set}: ID duplicado {id}");
            }
        }
    }
}
