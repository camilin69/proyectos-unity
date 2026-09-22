using System.Collections;
using System.IO;
using System.Linq;
using Esneider.AI;
using Esneider.Core;
using Esneider.Core.Data;
using Esneider.Core.Persistence;
using Esneider.Player;
using Esneider.World;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

namespace Esneider.Tests
{
    // 15/61/79.2: activación por umbral (EVT-21), ataques por fase con telegraph/recovery del catálogo, transición 2 s tras el ataque emitido,
    // nunca dos pulsos seguidos, muerte → BOSS_DEFEATED/O10/CP-07/D28, y retry desde CP-06 revive al jefe (reinicio de fases).
    public class BossPlayTests
    {
        PlayerController _pc; RegionStreamer _st; string _dir; LevelPlan _plan; BossBrain _boss; Health _bhp;

        [UnitySetUp]
        public IEnumerator SetUp()
        {
            Health.Clock = () => Time.time; WorldStateRegistry.ResetSession(); UI.MenuController.SkipTitle = true;
            _dir = Path.Combine(Path.GetTempPath(), "esneider-tests", System.Guid.NewGuid().ToString("N"));
            _plan = LevelPlan.FromJson(File.ReadAllText(LevelPlan.DefaultAssetPath));
#if UNITY_EDITOR
            yield return UnityEditor.SceneManagement.EditorSceneManager.LoadSceneAsyncInPlayMode("Assets/_Game/Scenes/BOOT.unity", new LoadSceneParameters(LoadSceneMode.Single));
#endif
            yield return null;
            _pc = Object.FindFirstObjectByType<PlayerController>(); _st = RegionStreamer.Instance;
            CheckpointService.Instance.saveDirectoryOverride = _dir;
            float t0 = Time.time; while (!_st.IsReady("REG-S1") && Time.time - t0 < 20f) yield return null;
            Object.FindFirstObjectByType<OpeningSequence>()?.RequestSkip();
            t0 = Time.time; while (!_pc.motor.movementEnabled && Time.time - t0 < 25f) yield return null;
            yield return _st.LoadForCheckpoint("REG-S4", W(40f, 31f), 180f);
            _boss = Object.FindObjectsByType<BossBrain>(FindObjectsSortMode.None).FirstOrDefault(b => b.stableId == "B01");
            Assert.IsNotNull(_boss, "B01 en REG-S4"); _bhp = _boss.GetComponent<Health>();
        }

        [UnityTearDown]
        public IEnumerator TearDown()
        {
            Time.timeScale = 1f; try { Directory.Delete(_dir, true); } catch { }
            yield return SceneManager.LoadSceneAsync("Combat_Sandbox", LoadSceneMode.Single);
            var pc = Object.FindFirstObjectByType<PlayerController>(); if (pc != null) Object.Destroy(pc.transform.root.gameObject);
            yield return null;
        }

        Vector3 W(float x, float z) { _plan.TryToWorld("P06", x, z, out var w); return w; }
        void Hit(float amount) { _bhp.ApplyDamage(new DamageInfo { amount = amount, attackId = AttackIds.Next(), source = _pc.gameObject, kind = "Test" }); }
        IEnumerator WaitState(BossState s, float timeout) { float t0 = Time.time; while (_boss.State != s && Time.time - t0 < timeout) yield return null; }

        [UnityTest]
        public IEnumerator Boss_ActivatesOnThreshold_AttacksByPhase_NoDoublePulse()
        {
            // fuera del umbral (galería) → Dormant; dentro de la arena → despertar 2 s → Engage
            _pc.motor.Teleport(W(40f, 31f), 180f); yield return new WaitForSeconds(0.6f);
            Assert.AreEqual(BossState.Dormant, _boss.State, "retirarse antes del umbral no inicia la fase");
            _pc.motor.Teleport(W(40f, 22f), 180f);
            yield return WaitState(BossState.Awakening, 2f);
            Assert.AreEqual(BossState.Awakening, _boss.State, "EVT-21 al cruzar el umbral con espacio útil");
            Assert.IsTrue(EventRunner.Instance.IsDone("EVT-21"));
            yield return WaitState(BossState.Engage, 4f);
            Assert.AreEqual(BossState.Engage, _boss.State);
            // fase I: primer ataque es rayo o barrido; telegraph del catálogo
            yield return WaitState(BossState.Prepare, 8f);
            Assert.AreEqual(BossState.Prepare, _boss.State, "el jefe prepara un ataque en fase I");
            string first = _boss.CurrentAttack; Assert.IsTrue(first == "BOSS-RAYO" || first == "BOSS-BARRIDO", first);
            float p0 = Time.time; yield return WaitState(BossState.Attack, 3f); yield return WaitState(BossState.Recover, 2f);
            var def = _boss.definition.attacks.Find(a => a.id == first);
            Assert.That(Time.time - p0, Is.GreaterThanOrEqualTo(def.telegraph - 0.1f).And.LessThan(def.telegraph + 0.6f), "telegraph " + first);
            Assert.AreEqual(1, _boss.Phase);
            // daño hasta 700 → transición solo tras resolver el ataque emitido → fase II
            Hit(500f); Assert.AreEqual(1, _boss.Phase, "la fase no cambia en mitad de un ataque");
            yield return WaitState(BossState.Transition, 6f);
            Assert.AreEqual(BossState.Transition, _boss.State, "transición 2 s tras el ataque emitido");
            float tr = Time.time; yield return WaitState(BossState.Engage, 4f);
            Assert.That(Time.time - tr, Is.GreaterThanOrEqualTo(1.9f)); Assert.AreEqual(2, _boss.Phase);
            // fase III: 300 HP; observar 6 emisiones: nunca dos pulsos consecutivos, solo carga/pulso/rayo
            Hit(400f); yield return WaitState(BossState.Transition, 15f); yield return WaitState(BossState.Engage, 4f); Assert.AreEqual(3, _boss.Phase);
            int before = _boss.Emitted.Count; float t0 = Time.time;
            while (_boss.Emitted.Count < before + 6 && Time.time - t0 < 60f) { _pc.motor.Teleport(W(40f, 22f), 180f); _pc.health.ResetTo(90f); yield return null; }
            var seq = _boss.Emitted.Skip(before).ToList();
            Assert.GreaterOrEqual(seq.Count, 4, "emisiones en fase III: " + string.Join(",", seq));
            for (int i = 1; i < seq.Count; i++) Assert.IsFalse(seq[i] == "BOSS-PULSO" && seq[i - 1] == "BOSS-PULSO", "dos pulsos seguidos: " + string.Join(",", seq));
            Assert.IsTrue(seq.All(s => s == "BOSS-CARGA" || s == "BOSS-PULSO" || s == "BOSS-RAYO"), string.Join(",", seq));
        }

        [UnityTest]
        public IEnumerator BossCannotEmitBackwardAndItsVisualFaceMatchesGameplayForward()
        {
            _boss.enabled = false;
            _pc.motor.Teleport(_boss.transform.position + Vector3.forward * 5, 180);
            var type = typeof(BossBrain);
            type.GetMethod("Set", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).Invoke(_boss, new object[] { BossState.Prepare });
            Assert.IsFalse(_boss.GetComponent<UnityEngine.AI.NavMeshAgent>().updateRotation);
            var emit = type.GetMethod("Emit", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            var attack = _boss.definition.attacks.Find(a => a.id == "BOSS-RAYO");
            int before = _boss.attacksEmitted;
            _boss.transform.rotation = Quaternion.Euler(0, 180, 0);
            Assert.IsFalse(_boss.FacingTarget); emit.Invoke(_boss, new object[] { attack });
            Assert.AreEqual(before, _boss.attacksEmitted);
            _boss.transform.rotation = Quaternion.identity;
            Assert.IsTrue(_boss.FacingTarget); emit.Invoke(_boss, new object[] { attack });
            Assert.AreEqual(before + 1, _boss.attacksEmitted);
            var view = _boss.GetComponent<EnemyAnimator>();
            yield return null;
            Assert.Greater(Vector3.Dot(view.animator.transform.TransformDirection(Vector3.back), _boss.transform.forward), .99f,
                "The Archivista chest/face (-Z in the imported model) must match gameplay forward after attack animation evaluation");
        }

        [UnityTest]
        public IEnumerator Boss_Death_GrantsExit_CP07_AndRetryFromCP06Revives()
        {
            // CP-06 antes del combate (refugio: garantía idempotente)
            _pc.motor.Teleport(W(6f, 42f), 0f); yield return null;
            Assert.IsTrue(CheckpointService.Instance.CommitNow("CP-06", _pc, "REG-S4", true, 90, 50, 24), "CP-06 consolidado");
            var cp06 = CheckpointService.Instance.LastConfirmed;
            _pc.motor.Teleport(W(40f, 22f), 180f); yield return WaitState(BossState.Engage, 6f);
            Hit(1200f); yield return null;
            Assert.IsTrue(_boss.IsDead); Assert.IsTrue(ObjectiveService.Has(ObjectiveService.BossDefeated)); Assert.IsTrue(WorldStateRegistry.Session.HasObjective("O10"));
            var destruction = _boss.GetComponent<Esneider.Combat.RobotDestruction>();
            Assert.IsNotNull(destruction); Assert.IsTrue(destruction.Hidden); Assert.AreEqual(1, destruction.BurstCount);
            Assert.Greater(destruction.FragmentCount, 36);
            Assert.IsTrue(Esneider.Audio.ProgressionMusic.Instance.IsSilent, "Boss death cuts the score immediately");
            Assert.IsTrue(ObjectiveService.DoorAllowed("D28A"), "D28 se abre con el jefe derrotado");
            Assert.IsFalse(ObjectiveService.DoorAllowed("D29"), "D29 exige además el panel final");
            float t0 = Time.time; while ((CheckpointService.Instance.LastConfirmed == null || CheckpointService.Instance.LastConfirmed.checkpointId != "CP-07") && Time.time - t0 < 5f) yield return null;
            Assert.AreEqual("CP-07", CheckpointService.Instance.LastConfirmed.checkpointId, "CP-07 guardado antes de cualquier menú");
            Assert.IsTrue(CheckpointService.Instance.LastConfirmed.bossDefeated);
            // retry desde CP-06: jefe vivo, fase I, EVT-21 pendiente, permiso retirado
            Assert.IsTrue(CheckpointService.Instance.RestoreInto(cp06, _pc)); yield return null; yield return null;
            Assert.IsFalse(_boss.IsDead, "el registro manda: jefe vivo al cargar CP-06");
            Assert.IsFalse(destruction.Hidden); Assert.AreEqual(0, destruction.FragmentCount);
            Assert.AreEqual(1, _boss.Phase); Assert.AreEqual(BossState.Dormant, _boss.State);
            Assert.IsFalse(ObjectiveService.Has(ObjectiveService.BossDefeated)); Assert.IsFalse(EventRunner.Instance.IsDone("EVT-21"));
            Assert.AreEqual(1200f, _bhp.Current, 0.5f);
        }
    }
}
