using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using Esneider.Core.Data;
using UnityEditor;
using UnityEngine;

namespace Esneider.EditorTools
{
    // Instancia las definiciones de 95.1 con los valores vigentes de 103.1 y exporta la tabla de baseline (95.3).
    public static class BaselineDataCreator
    {
        const string Dir = "Assets/_Game/Data/Definitions";

        static readonly string[] Layers = { "Player", "Enemy", "WorldStatic", "DynamicProp", "PlayerProjectile", "EnemyProjectile", "Interactable", "Trigger", "Corpse", "VFX" };

        [MenuItem("Esneider/Data/Create baseline definitions")]
        public static void CreateMenu() => Create();

        public static string Create()
        {
            Directory.CreateDirectory(Dir);
            EnsureLayers();
            var plan = LevelPlan.FromJson(File.ReadAllText(LevelPlan.DefaultAssetPath));

            // Se arma en memoria: crear assets durante la pasada invalida referencias cargadas antes.
            var catalog = ScriptableObject.CreateInstance<GameDataCatalog>();
            catalog.contentVersion = "0.1.0";
            catalog.levelPlanJson = AssetDatabase.LoadAssetAtPath<TextAsset>(LevelPlan.DefaultAssetPath);

            var player = Asset<PlayerDefinition>("Player_Esneider");
            player.id = "CHR-01"; player.gddSource = "10/103.1 (velocidades: VAL sección 9)";
            player.maxHp = 90; player.invulnerabilitySeconds = 0.65f;
            player.syringeHeal = 45; player.syringeDuration = 1.6f; player.syringeCommit = 1.1f;
            player.rationHeal = 20; player.rationDuration = 2.0f; player.rationCommit = 1.4f;
            player.maxSyringes = 3; player.maxRations = 2;
            player.fovVertical = 75; player.fovMin = 70; player.fovMax = 100;
            player.noiseCrouch = 1.5f; player.noiseWalk = 4f; player.noiseRun = 10f;
            catalog.player = player;

            catalog.weapons.Clear();
            var crowbar = Asset<WeaponDefinition>("Weapon_Crowbar");
            crowbar.id = "WPN-01"; crowbar.gddSource = "11/60/103.1"; crowbar.kind = WeaponKind.Melee;
            crowbar.damage = 20; crowbar.pellets = 1; crowbar.range = 1.6f; crowbar.attackCycle = 0.85f; crowbar.activeStart = 0.20f; crowbar.activeEnd = 0.35f; crowbar.noiseRadius = 12;
            var pistol = Asset<WeaponDefinition>("Weapon_Pistol");
            pistol.id = "WPN-02"; pistol.gddSource = "11/68/80/86/103.1"; pistol.kind = WeaponKind.Pistol;
            pistol.damage = 30; pistol.pellets = 1; pistol.range = 18f; pistol.magazineSize = 12; pistol.reserveMax = 80; pistol.pickupLoaded = 10; pistol.pickupReserve = 10;
            pistol.attackCycle = 0.35f; pistol.activeStart = 0f; pistol.activeEnd = 0.05f; pistol.reloadDuration = 1.9f; pistol.reloadCommit = 1.35f; pistol.noiseRadius = 28;
            var shotgun = Asset<WeaponDefinition>("Weapon_Shotgun");
            shotgun.id = "WPN-03"; shotgun.gddSource = "11/68/80/86/103.1"; shotgun.kind = WeaponKind.Shotgun;
            // daño completo ≤ 6 m, caída hasta 12 m (11)
            shotgun.damage = 7.5f; shotgun.pellets = 8; shotgun.range = 12f; shotgun.magazineSize = 6; shotgun.reserveMax = 36; shotgun.pickupLoaded = 5; shotgun.pickupReserve = 5;
            shotgun.attackCycle = 1.1f; shotgun.activeStart = 0f; shotgun.activeEnd = 0.05f; shotgun.pumpDuration = 0.65f;
            shotgun.shellEnter = 0.35f; shotgun.shellInsert = 0.6f; shotgun.shellInsertCommit = 0.4f; shotgun.shellExit = 0.3f; shotgun.noiseRadius = 36;
            catalog.weapons.AddRange(new[] { crowbar, pistol, shotgun });

            catalog.enemies.Clear();
            var vigia = Asset<EnemyDefinition>("Enemy_Vigia");
            vigia.id = "BOT-01"; vigia.gddSource = "12/14/77/78/103.1"; vigia.kind = EnemyKind.Vigia;
            vigia.maxHp = 60; vigia.patrolSpeed = 0.7f; vigia.chaseSpeed = 2.6f;
            vigia.attackRangeMin = 3; vigia.attackRangeMax = 9; vigia.telegraph = 1.1f; vigia.telegraphTutorial = 1.2f; vigia.recovery = 1.4f; vigia.cooldown = 3.5f; vigia.attackDamage = 0; vigia.captureSeconds = 2.5f;
            var custodio = Asset<EnemyDefinition>("Enemy_Custodio");
            custodio.id = "BOT-02"; custodio.gddSource = "13/14/77/78/103.1"; custodio.kind = EnemyKind.Custodio;
            custodio.maxHp = 120; custodio.patrolSpeed = 0.6f; custodio.chaseSpeed = 2.2f;
            custodio.attackRangeMin = 4; custodio.attackRangeMax = 14; custodio.telegraph = 1.0f; custodio.telegraphTutorial = 1.0f; custodio.recovery = 1.6f; custodio.cooldown = 3.0f; custodio.attackDamage = 30; custodio.captureSeconds = 0;
            foreach (var e in new[] { vigia, custodio })
            {
                e.visionRangeLit = 12; e.visionAngleLit = 90; e.visionRangeAlert = 16; e.visionAngleAlert = 100; e.visionRangeDark = 6; e.visionRangeDarkAlert = 8;
                e.closeRange = 3; e.closeReaction = 0.35f; e.searchSeconds = 12; e.combatSearchSeconds = 18;
            }
            catalog.enemies.AddRange(new[] { vigia, custodio });

            var boss = Asset<BossDefinition>("Boss_Archivista");
            boss.id = "BOT-03"; boss.gddSource = "15/61/79/103.1"; boss.maxHp = 1200; boss.phase2Threshold = 800; boss.phase3Threshold = 400; boss.phaseTransitionSeconds = 2; boss.doubleSequenceGap = 0.8f; boss.doubleSequenceRecovery = 2.5f;
            boss.attacks = new List<BossAttackDefinition>
            {
                new BossAttackDefinition { id = "BOSS-RAYO", damage = 30, telegraph = 1.2f, recovery = 2.0f, radius = 0, phaseFrom = 1 },
                new BossAttackDefinition { id = "BOSS-BARRIDO", damage = 30, telegraph = 1.4f, recovery = 2.2f, radius = 0, phaseFrom = 1 },
                new BossAttackDefinition { id = "BOSS-CARGA", damage = 45, telegraph = 1.5f, recovery = 2.4f, radius = 0, phaseFrom = 3 },
                new BossAttackDefinition { id = "BOSS-PULSO", damage = 30, telegraph = 1.8f, recovery = 2.4f, radius = 6, phaseFrom = 3 },
            };
            catalog.boss = boss;

            catalog.surfaces.Clear();
            var surf = new (string id, float s, float d, float mult, string vis)[]
            {
                ("SUR-CON", 0.65f, 0.55f, 1f, "Polvo puntual y marca de bala limitada"),
                ("SUR-MET", 0.5f, 0.4f, 1f, "Chispa ocasional localizada"),
                ("SUR-GRT", 0.6f, 0.5f, 1.25f, "Vibración autorada"),
                ("SUR-WET", 0.55f, 0.45f, 1f, "Gotas leves, charco plano"),
                ("SUR-CER", 0.6f, 0.5f, 1f, "Fragmento solo variante RX-3"),
                ("SUR-GLS", 0.45f, 0.35f, 1f, "Marca o rotura según ReactionClass"),
                ("SUR-FAB", 0.7f, 0.6f, 0.75f, "Deformación leve"),
                ("SUR-RUB", 0.8f, 0.7f, 0.65f, "Marca tenue sin chispas"),
                ("SUR-BOT", 0.5f, 0.4f, 1f, "Fluido técnico, chips y herida autorada"),
            };
            foreach (var s in surf)
            {
                var a = Asset<SurfaceDefinition>("Surface_" + s.id.Substring(4));
                a.id = s.id; a.gddSource = "96.1/96.2"; a.staticFriction = s.s; a.dynamicFriction = s.d; a.footstepNoiseMultiplier = s.mult; a.visualReaction = s.vis;
                catalog.surfaces.Add(a);
            }

            catalog.regions.Clear();
            foreach (var r in plan.rooms)
            {
                var f = plan.Floor(r.floor);
                var a = Asset<RoomRegionDefinition>("Region_" + r.id);
                a.id = r.id; a.gddSource = "68.2/88.1"; a.kind = RegionKind.Sector; a.regionId = f.region; a.guid = LevelPlan.StableGuid(r.id).ToString();
                a.floorId = f.id; a.sectorId = f.sector; a.worldOrigin = f.origin.ToVector3(); a.localRect = new Rect(r.x, r.z, r.w, r.d); a.height = f.height;
                a.doorIds = plan.doors.Where(d => d.room == r.id).Select(d => d.id).ToList();
                a.ownedEntityIds = plan.spawns.Where(s => s.space == f.id && r.Contains(s.x, s.z)).Select(s => s.id)
                    .Concat(plan.pickups.Where(p => p.space == f.id && r.Contains(p.x, p.z)).Select(p => p.id)).ToList();
                catalog.regions.Add(a);
            }
            foreach (var c in plan.connectors)
            {
                var a = Asset<RoomRegionDefinition>("Region_" + c.id);
                a.id = c.id; a.gddSource = "68.5/88.1"; a.kind = RegionKind.Connector; a.regionId = c.region; a.guid = LevelPlan.StableGuid(c.id).ToString();
                a.floorId = c.id; a.sectorId = c.region; a.worldOrigin = c.origin.ToVector3();
                a.localRect = new Rect(c.points.Min(p => p.x), c.points.Min(p => p.z), c.points.Max(p => p.x) - c.points.Min(p => p.x), c.points.Max(p => p.z) - c.points.Min(p => p.z)); a.height = c.height;
                a.doorIds = new List<string> { c.fromDoor, c.toDoor };
                a.ownedEntityIds = plan.spawns.Where(s => s.space == c.id).Select(s => s.id).ToList();
                catalog.regions.Add(a);
            }

            catalog.checkpoints.Clear();
            foreach (var cp in plan.checkpoints)
            {
                var a = Asset<CheckpointDefinition>("Checkpoint_" + cp.id);
                a.id = cp.id; a.gddSource = "68.9/80/89"; a.spaceId = cp.space; a.guid = LevelPlan.StableGuid(cp.id).ToString();
                plan.TryToWorld(cp.space, cp.x, cp.z, out var w); a.worldPosition = w; a.activation = cp.activation; a.protection = cp.protection;
                a.isShelter = cp.id == "CP-06";
                if (a.isShelter) { a.guaranteeHp = 90; a.guaranteePistolTotal = 50; a.guaranteeShotgunTotal = 24; }
                catalog.checkpoints.Add(a);
            }

            catalog.events.Clear();
            var evts = new (string id, string room, EventPolicy pol, string trig, string act, string rest)[]
            {
                ("EVT-01","S1-R01",EventPolicy.Once,"Nueva campaña, opening no completado","Apertura 58, control gradual, CP-00 al terminar","CP-00 omite apertura y coloca player seguro"),
                ("EVT-02","S1-R02",EventPolicy.Interaction,"Interactuar pickup linterna disponible","Equipar/aviso/flag equipo; termina al commit","Recogida no reaparece"),
                ("EVT-03","S1-R05",EventPolicy.Once,"Primera entrada, región Ready","Revelar cámaras vacías; una válvula 1 s","U válvula; A ventilación, sin bots"),
                ("EVT-04","S1-R03",EventPolicy.Interaction,"Extraer varilla existente","Sonido de liberación, equipar y O02","No desplomar escombros bloqueando salida"),
                ("EVT-05","S1-R04",EventPolicy.Interaction,"Operar palanca 2 s sin cancelación","Permiso servicio; preparar C1 y CP-01 seguro","Permiso persiste, DOC-02 no requerido"),
                ("EVT-06","S2-R01",EventPolicy.Once,"Cruzar D08, K01 vivo","Primera lectura K01 sin quitar control","Estado real del bot manda al retornar"),
                ("EVT-07","S2-R06",EventPolicy.Once,"Primera entrada taller","Brazo inerte reajusta 1.5 s, luego reposo","No convertir prop en unidad adicional"),
                ("EVT-08","S2-R03",EventPolicy.Interaction,"Interactuar DOC-03/04","Abrir texto y marcar documento visto","Archivo releíble"),
                ("EVT-09","S2-R02",EventPolicy.Interaction,"Recoger pistola disponible","Equipar protegido ENC-04; O04 y CP-02 seguro","No respawn ni tutorial repetido"),
                ("EVT-10","S2-R04",EventPolicy.Interaction,"Operar panel A, carro en posición válida","Permiso A, relé y CP-03 seguro","Estado carro/panel persistente"),
                ("EVT-11","S2-R05",EventPolicy.Ambient,"Aproximarse mesa sin combate inmediato","Iluminación revela seriales/rostros inertes","Pista visible siempre"),
                ("EVT-12","S3-R01",EventPolicy.Once,"Entrar admisión, estado seguro","O06 o contextualización; CP-04 seguro","DOC-06 independiente"),
                ("EVT-13","S3-R02A",EventPolicy.Once,"Primera visión del sujeto focal sin ataque","Respiración destacada 6 s y mano leve","A respiración discreta posterior"),
                ("EVT-14","S3-R02B",EventPolicy.Once,"Primera entrada opcional","Bomba inicia ciclo 3 s","No permiso obligatorio"),
                ("EVT-15","S3-R03",EventPolicy.Ambient,"Primera lectura visual de mesa","Goteo/monitor localizado","No gore nuevo al cargar"),
                ("EVT-16","S3-R04",EventPolicy.Once,"Iniciar primera lectura protegida DOC-09","V15 inactivo durante evento; flag al cerrar","Flag persiste; no inmunidad por lectura"),
                ("EVT-17","S3-R05",EventPolicy.Interaction,"Recoger escopeta disponible","Equipar, O07 y feedback; locker abierto","Commits 86, no segunda entrega"),
                ("EVT-18","S4-R05",EventPolicy.Once,"Interactuar DOC-11/consola","Leer firma; habilita despertar V23","Solo si V23 vivo"),
                ("EVT-19","S4-R02",EventPolicy.Interaction,"Entrar refugio y consolidar CP-06","Garantía 90 HP/50 balas/24 cartuchos","Idempotente, no suma"),
                ("EVT-20","S4-R01",EventPolicy.Once,"Primera entrada opcional","Relé rompe silencio 0.8 s","Botín normal, no oleada"),
                ("EVT-21","S4-R03",EventPolicy.Once,"Cruzar D27, boss no derrotado","Activar combate/fases 79; muerte estable/CP-07","Reinicio por retry CP-06"),
                ("EVT-22","S4-R04",EventPolicy.Interaction,"Boss muerto, interacción panel salida","Abrir D29, aire exterior, permitir escape","D29 y flag panel se restauran"),
                ("EVT-C1","C-01",EventPolicy.Once,"Abrir D06 y reconectar diagnóstico","Flag detección y O03; anuncio y alerta breve","No repetir por cruce ni carga"),
                ("EVT-C2","C-02",EventPolicy.Once,"Primera ventana humana a la vista sin amenaza","Gesto de mano 2 s y O06","V08 respeta ENC-08"),
                ("EVT-C3","C-03",EventPolicy.Once,"Primera segunda mitad del corredor","Impacto remoto del boss 1 s","No sincronizar si ya murió"),
                ("EVT-EXIT","S4-R04",EventPolicy.Once,"Volumen de victoria (97)","O11 y resultado una sola vez","Victoria persistente"),
            };
            foreach (var e in evts)
            {
                var a = Asset<EventDefinition>("Event_" + e.id);
                a.id = e.id; a.gddSource = "93"; a.roomId = e.room; a.guid = LevelPlan.StableGuid(e.id).ToString(); a.policy = e.pol; a.trigger = e.trig; a.action = e.act; a.restore = e.rest;
                catalog.events.Add(a);
            }

            catalog.difficulties.Clear();
            var normal = Asset<DifficultyDefinition>("Difficulty_Normal");
            normal.id = "DIF-NORMAL"; normal.gddSource = "80.3/103.1"; normal.presetName = "Normal";
            catalog.difficulties.Add(normal);

            var catalogAsset = Asset<GameDataCatalog>("GameDataCatalog");
            EditorUtility.CopySerialized(catalog, catalogAsset);
            Object.DestroyImmediate(catalog);
            catalog = catalogAsset;
            EditorUtility.SetDirty(catalog);
            AssetDatabase.SaveAssets();

            var report = DataValidator.Validate(catalog);
            var planReport = DataValidator.ValidatePlan(plan);
            Debug.Log(report.ToString());
            Debug.Log(planReport.ToString());
            ExportBaseline(catalog, plan, report, planReport);
            return report + "\n" + planReport;
        }

        static void ExportBaseline(GameDataCatalog c, LevelPlan p, DataValidator.Report r, DataValidator.Report pr)
        {
            System.Threading.Thread.CurrentThread.CurrentCulture = System.Globalization.CultureInfo.InvariantCulture;
            var sb = new StringBuilder();
            sb.AppendLine("# DATA_BASELINE — export de definiciones ejecutables (95.3)\n");
            sb.AppendLine($"contentVersion `{c.contentVersion}` · plano `{p.version}` · validación datos: **{(r.Passed ? "PASA" : "FALLA")}** · validación plano: **{(pr.Passed ? "PASA" : "FALLA")}**\n");
            sb.AppendLine("| Campo | Valor ejecutable | Fuente GDD |\n|---|---|---|");
            sb.AppendLine($"| Player HP / invulnerabilidad | {c.player.maxHp} / {c.player.invulnerabilitySeconds}s | {c.player.gddSource} |");
            sb.AppendLine($"| FOV | {c.player.fovVertical}° ({c.player.fovMin}–{c.player.fovMax}) | 9/81 |");
            sb.AppendLine($"| Curación | jeringa +{c.player.syringeHeal} {c.player.syringeDuration}s/commit {c.player.syringeCommit}s; ración +{c.player.rationHeal} {c.player.rationDuration}s/commit {c.player.rationCommit}s; máx {c.player.maxSyringes}/{c.player.maxRations} | 10/86 |");
            foreach (var w in c.weapons)
                sb.AppendLine($"| {w.name} | daño {w.damage}×{w.pellets}; cargador {w.magazineSize}+{w.reserveMax}; pickup {w.pickupLoaded}+{w.pickupReserve}; ciclo {w.attackCycle}s; recarga {w.reloadDuration}/{w.reloadCommit}s; ruido {w.noiseRadius} m | {w.gddSource} |");
            foreach (var e in c.enemies)
                sb.AppendLine($"| {e.name} | HP {e.maxHp}; vel {e.patrolSpeed}/{e.chaseSpeed}; rango {e.attackRangeMin}–{e.attackRangeMax}; aviso {e.telegraph}s; rec {e.recovery}s; cd {e.cooldown}s; daño {e.attackDamage}; visión {e.visionRangeLit}m{e.visionAngleLit}°/{e.visionRangeAlert}m{e.visionAngleAlert}° | {e.gddSource} |");
            sb.AppendLine($"| Boss | HP {c.boss.maxHp}; fases {c.boss.phase2Threshold}/{c.boss.phase3Threshold}; ataques {string.Join(", ", (c.boss.attacks ?? new List<BossAttackDefinition>()).Select(a => $"{a.id} {a.damage} ({a.telegraph}/{a.recovery}s)"))} | {c.boss.gddSource} |");
            sb.AppendLine($"| Superficies | {string.Join(", ", c.surfaces.Select(s => $"{s.id} {s.staticFriction}/{s.dynamicFriction} ×{s.footstepNoiseMultiplier}"))} | 96 |");
            sb.AppendLine($"| Regiones | {c.regions.Count} ({c.regions.Count(x => x.kind == RegionKind.Sector)} salas + {c.regions.Count(x => x.kind == RegionKind.Connector)} conectores) | 68/88 |");
            sb.AppendLine($"| Checkpoints | {string.Join(", ", c.checkpoints.Select(x => x.id))} | 68.9 |");
            sb.AppendLine($"| Eventos | {c.events.Count} | 93 |");
            sb.AppendLine($"| Población plano | {p.spawns.Count(s => s.kind == "Vigia")}V/{p.spawns.Count(s => s.kind == "Custodio")}K/{p.spawns.Count(s => s.kind == "Boss")}B; balas {p.pickups.Where(x => x.kind == "PistolAmmo" || x.kind == "Pistol").Sum(x => x.amount)}; cartuchos {p.pickups.Where(x => x.kind == "ShotgunAmmo" || x.kind == "Shotgun").Sum(x => x.amount)} | 68.7/68.8 |");
            sb.AppendLine("\n## Informe de validación\n```\n" + r + "\n" + pr + "\n```\n");
            sb.AppendLine("## GUIDs estables (MD5 de `ESNEIDER:<ID>`)\n\n| ID | GUID |\n|---|---|");
            foreach (var reg in c.regions) sb.AppendLine($"| {reg.id} | {reg.guid} |");
            foreach (var cp in c.checkpoints) sb.AppendLine($"| {cp.id} | {cp.guid} |");
            var path = Path.GetFullPath(Path.Combine(Application.dataPath, "../../docs/produccion/DATA_BASELINE.md"));
            File.WriteAllText(path, sb.ToString());
            Debug.Log("Baseline exportado a " + path);
        }

        static T Asset<T>(string name) where T : ScriptableObject
        {
            string path = $"{Dir}/{name}.asset";
            var a = AssetDatabase.LoadAssetAtPath<T>(path);
            if (a == null) { a = ScriptableObject.CreateInstance<T>(); AssetDatabase.CreateAsset(a, path); }
            EditorUtility.SetDirty(a);
            return a;
        }

        static void EnsureLayers()
        {
            var tagManager = new SerializedObject(AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/TagManager.asset")[0]);
            var layers = tagManager.FindProperty("layers");
            var existing = new HashSet<string>();
            for (int i = 0; i < layers.arraySize; i++) existing.Add(layers.GetArrayElementAtIndex(i).stringValue);
            int next = 6; // 0–5 reservadas por Unity
            foreach (var name in Layers)
            {
                if (existing.Contains(name)) continue;
                while (next < layers.arraySize && !string.IsNullOrEmpty(layers.GetArrayElementAtIndex(next).stringValue)) next++;
                if (next >= layers.arraySize) { Debug.LogError("Sin capas libres para " + name); break; }
                layers.GetArrayElementAtIndex(next).stringValue = name; existing.Add(name); next++;
            }
            tagManager.ApplyModifiedProperties();
        }
    }
}
