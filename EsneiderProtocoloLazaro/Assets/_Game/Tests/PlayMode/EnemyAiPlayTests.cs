using System.Collections;
using Esneider.AI;
using Esneider.Combat;
using Esneider.Core;
using Esneider.Core.Data;
using Esneider.Player;
using Esneider.World;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;

namespace Esneider.Tests
{
    // 14/78: la FSM confirma al humano con visión clara, persigue, prepara con telegraph completo y emite una sola vez por ciclo.
    public class EnemyAiPlayTests
    {
        SandboxFactory.Result _r;
        PlayerController _pc;

        [UnitySetUp]
        public IEnumerator SetUp()
        {
            Health.Clock = () => Time.time; Esneider.Core.Persistence.WorldStateRegistry.ResetSession();
#if UNITY_EDITOR
            var cat = UnityEditor.AssetDatabase.LoadAssetAtPath<GameDataCatalog>("Assets/_Game/Data/Definitions/GameDataCatalog.asset");
#else
            GameDataCatalog cat = null;
#endif
            _r = SandboxFactory.Build(cat);
            _pc = _r.player.GetComponent<PlayerController>();
            // aislar: solo el Vigía activo, Custodio inerte
            Object.Destroy(_r.custodio);
            yield return null; yield return null;
        }

        [UnityTearDown]
        public IEnumerator TearDown()
        {
            Time.timeScale = 1f;
            if (_r != null && _r.root != null) Object.Destroy(_r.root);
            foreach (var p in Object.FindObjectsByType<Projectile>(FindObjectsSortMode.None)) Object.Destroy(p.gameObject);
            yield return null;
        }

        [UnityTest]
        public IEnumerator Vigia_SeesPlayer_ConfirmsAfterSuspicion_ThenTelegraphsAndEmitsNet()
        {
            var brain = _r.vigia.GetComponent<EnemyBrain>();
            var per = _r.vigia.GetComponent<EnemyPerception>();
            // jugador a 6 m frente al Vigía, ambos en línea de visión, sin pilar en medio
            _r.vigia.transform.position = new Vector3(3f, 0, 3f); _r.vigia.transform.rotation = Quaternion.Euler(0, 180f, 0);
            _pc.motor.Teleport(new Vector3(3f, 0, -3f), 0f);
            yield return null;
            float t0 = Time.time;
            bool sawSuspicion = false, sawPrepare = false;
            while (Time.time - t0 < 10f && brain.attacksEmitted == 0)
            {
                if (per.suspicion > 0.2f && per.suspicion < 1f) sawSuspicion = true;
                if (brain.State == EnemyState.Prepare) sawPrepare = true;
                yield return null;
            }
            Assert.IsTrue(sawSuspicion, "la confirmación acumula sospecha (1.2 s de visión clara), no es instantánea");
            Assert.IsTrue(sawPrepare, "pasa por Preparar (telegraph) antes de emitir");
            Assert.AreEqual(1, brain.attacksEmitted, "una emisión por ciclo");
            Assert.GreaterOrEqual(Time.time - t0, 1.2f + 1.1f - 0.1f, "confirmación + telegraph mínimos");
            // La red captura, pero permite escapar mediante pulsaciones de F.
            float e = Time.time;
            while (Time.time - e < 2.5f && !_pc.IsCaptured) yield return null;
            Assert.IsTrue(_pc.IsCaptured, "red válida en rango 3–9 m captura al jugador quieto");
            Assert.AreEqual(EnemyState.Executing, brain.State);
            for(int i=0;i<_pc.captureEscapePresses;i++) { _pc.input.FlashlightPressed=true; yield return null; }
            Assert.IsFalse(_pc.IsCaptured); Assert.IsTrue(GameFlowController.Instance.AttemptOpen);
            Assert.AreEqual(EnemyState.Staggered,brain.State,"el captor abandona Executing al escapar");
        }

        [UnityTest]
        public IEnumerator Vigia_LosesSightBehindPillar_SearchesLastKnownPosition()
        {
            var brain = _r.vigia.GetComponent<EnemyBrain>();
            var per = _r.vigia.GetComponent<EnemyPerception>();
            // línea de visión libre: Vigía en (3,4.5) mirando -z y jugador en (3,-3); el pilar (0,1.5) no interfiere
            // jugador a 10 m: dentro de visión (12 m) pero fuera del rango de red (3–9 m), así no hay ataque
            var agent = _r.vigia.GetComponent<UnityEngine.AI.NavMeshAgent>();
            brain.waypoints.Clear(); agent.speed = 0f; // el Vigía no patrulla: se queda en su posición de partida
            agent.Warp(new Vector3(3f, 0, 4.5f)); _r.vigia.transform.rotation = Quaternion.Euler(0, 180f, 0);
            _pc.motor.Teleport(new Vector3(3f, 0, -5.5f), 0f);
            yield return null;
            float t0 = Time.time;
            while (Time.time - t0 < 6f && brain.State != EnemyState.Chase) yield return null;
            Assert.AreEqual(EnemyState.Chase, brain.State, "confirma y persigue");
            var lastSeen = per.lastKnownPosition;
            // el Vigía queda bloqueado (ruta impedida) y el jugador se oculta tras el pilar (0,*,1.5) respecto a z=4.5
            _r.vigia.GetComponent<UnityEngine.AI.NavMeshAgent>().speed = 0f;
            // (3,4.5) → pilar (0,1.5) → (-3.5,-2): colineal, el pilar ocluye torso y cabeza
            _pc.motor.Teleport(new Vector3(-3.5f, 0, -2f), 0f);
            yield return null;
            float t1 = Time.time; bool searched = false;
            while (Time.time - t1 < 8f) { if (brain.State == EnemyState.Search) { searched = true; break; } yield return null; }
            Assert.IsTrue(searched, $"sin visión inicia búsqueda en la última posición, no omnisciencia: {brain.State} sees={per.SeesTarget} t={brain.StateTime:F1} emitted={brain.attacksEmitted}");
            Assert.Less(Vector3.Distance(per.lastKnownPosition, lastSeen), 4f, "la última posición conocida es donde lo vio");
        }
    }
}
