using System.Collections.Generic;
using Esneider.Core;
using UnityEngine;

namespace Esneider.Combat
{
    public enum ProjectileKind { Net, Bolt, BossBolt }

    // 12.1/13/20.3: proyectil con detección barrida entre posición anterior y siguiente; una sola aplicación por AttackID;
    // pool con reinicio completo de owner, vida, collider y callbacks.
    public class Projectile : MonoBehaviour
    {
        public ProjectileKind kind;
        public float speed, radius, maxLife, damage;
        public int attackId;
        public GameObject owner;
        public bool Active { get; private set; }
        Vector3 _dir; float _born;
        static readonly Dictionary<ProjectileKind, Stack<Projectile>> _pool = new Dictionary<ProjectileKind, Stack<Projectile>>();

        public static Projectile Spawn(ProjectileKind kind, Vector3 origin, Vector3 dir, GameObject owner, int attackId, float damage)
        {
            if (!_pool.TryGetValue(kind, out var stack)) { stack = new Stack<Projectile>(); _pool[kind] = stack; }
            Projectile p = null;
            while (stack.Count > 0 && p == null) { var c = stack.Pop(); if (c != null) p = c; }
            if (p == null) p = Create(kind);
            p.Reset(kind, origin, dir, owner, attackId, damage);
            return p;
        }

        static Projectile Create(ProjectileKind kind)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            go.name = "Projectile_" + kind;
            Object.Destroy(go.GetComponent<Collider>()); // colisión por barrido, no por collider físico
            go.layer = GameLayers.EnemyProjectile;
            var mr = go.GetComponent<MeshRenderer>();
            // material como asset (Resources): en la build `Shader.Find` puede devolver null por stripping y un proyectil no puede fallar por cosmética (93.3)
            var mat = Resources.Load<Material>("Materials/Projectile_" + kind);
            if (mat == null)
            {
                var shader = Shader.Find("Universal Render Pipeline/Unlit") ?? Shader.Find("Unlit/Color") ?? Shader.Find("Universal Render Pipeline/Lit");
                if (shader != null) { mat = new Material(shader); mat.color = kind == ProjectileKind.Net ? new Color(0.4f, 0.7f, 1f) : new Color(1f, 0.9f, 0.3f); }
                else { mr.enabled = false; Debug.LogWarning("Projectile: sin material/shader disponible; proyectil invisible pero funcional"); }
            }
            if (mat != null) mr.sharedMaterial = mat;
            return go.AddComponent<Projectile>();
        }

        void Reset(ProjectileKind k, Vector3 origin, Vector3 dir, GameObject own, int id, float dmg)
        {
            kind = k; owner = own; attackId = id; damage = dmg; _dir = dir.normalized; _born = Time.time;
            speed = k == ProjectileKind.Net ? 6f : 9f; radius = k == ProjectileKind.Net ? 0.25f : 0.18f; maxLife = 2f;
            transform.position = origin; transform.localScale = Vector3.one * radius * 2f;
            gameObject.SetActive(true); Active = true;
        }

        void FixedUpdate()
        {
            if (!Active) return;
            if (Time.time - _born > maxLife) { Despawn(); return; }
            var from = transform.position; var to = from + _dir * speed * Time.fixedDeltaTime;
            float dist = (to - from).magnitude;
            if (Physics.SphereCast(from, radius, _dir, out var hit, dist, GameLayers.EnemyProjectileHitMask, QueryTriggerInteraction.Ignore))
            {
                if (owner != null && (hit.collider.gameObject == owner || hit.collider.transform.IsChildOf(owner.transform))) { transform.position = to; return; }
                OnHit(hit);
                Despawn();
                return;
            }
            transform.position = to;
        }

        void OnHit(RaycastHit hit)
        {
            var player = hit.collider.GetComponentInParent<Player.PlayerController>();
            if (player == null) return; // cobertura destruye el proyectil
            if (kind == ProjectileKind.Net)
            {
                player.Capture(owner);
                var brain = owner != null ? owner.GetComponent<AI.EnemyBrain>() : null;
                if (brain != null) brain.OnNetCaptured(player);
            }
            else
            {
                var hp = player.GetComponent<Health>();
                hp?.ApplyDamage(new DamageInfo { amount = damage, attackId = attackId, source = owner, point = hit.point, direction = _dir, kind = kind.ToString() });
            }
        }

        public void Despawn()
        {
            if (!Active) return;
            Active = false; gameObject.SetActive(false); owner = null; attackId = 0;
            if (!_pool.TryGetValue(kind, out var stack)) { stack = new Stack<Projectile>(); _pool[kind] = stack; }
            stack.Push(this);
        }

        public static void DespawnAllFrom(GameObject owner)
        {
            foreach (var p in FindObjectsByType<Projectile>(FindObjectsSortMode.None)) if (p.Active && p.owner == owner) p.Despawn();
        }
    }
}
