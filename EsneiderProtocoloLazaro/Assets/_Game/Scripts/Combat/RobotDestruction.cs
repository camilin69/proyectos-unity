using System.Collections.Generic;
using System.Linq;
using Esneider.Core;
using UnityEngine;

namespace Esneider.Combat
{
    // The persistent robot stays alive as data; only its visible shell is destroyed.
    public class RobotDestruction : MonoBehaviour
    {
        class Fragment { public Transform part; public Vector3 velocity, spin, scale; public bool spark; }
        Renderer[] renderers; bool[] rendererEnabled;
        Collider[] colliders; bool[] colliderEnabled;
        readonly List<Fragment> fragments = new List<Fragment>();
        readonly List<Mesh> ownedMeshes = new List<Mesh>();
        GameObject burst, flash; Light flashLight; ParticleSystem fireParticles, smokeParticles; float elapsed, size;
        public bool Hidden { get; private set; }
        public int BurstCount { get; private set; }
        public int FragmentCount => fragments.Count;

        void Cache()
        {
            if (renderers != null) return;
            renderers = GetComponentsInChildren<Renderer>(true); rendererEnabled = renderers.Select(r => r.enabled).ToArray();
            colliders = GetComponentsInChildren<Collider>(true); colliderEnabled = colliders.Select(c => c.enabled).ToArray();
        }

        public void Explode(bool boss)
        {
            Cache(); if (Hidden) return;
            BurstCount++; elapsed = 0;
            var bounds = new Bounds(transform.position + Vector3.up, Vector3.one);
            bool found = false;
            var shells = renderers.Where(r => r.enabled && r.gameObject.activeInHierarchy && PrimaryLod(r)).ToArray();
            foreach (var r in shells) { if (!found) { bounds = r.bounds; found = true; } else bounds.Encapsulate(r.bounds); }
            size = Mathf.Clamp(bounds.size.y, 1, 4);
            burst = new GameObject("RobotExplosion"); burst.transform.SetParent(transform, false);
            // A few large shells read better and cost far less than splitting every decorative renderer.
            foreach (var r in shells.OrderByDescending(r => r.bounds.size.sqrMagnitude).Take(boss ? 5 : 3))
            {
                var skin = r as SkinnedMeshRenderer;
                if (skin != null && skin.sharedMesh != null)
                {
                    var baked = new Mesh(); skin.BakeMesh(baked);
                    SplitShell(baked, skin.transform, r.sharedMaterials, bounds.center);
                    Destroy(baked);
                }
                else
                {
                    var filter = r.GetComponent<MeshFilter>();
                    if (filter != null && filter.sharedMesh != null)
                        AddPart(filter.sharedMesh, r.sharedMaterials, r.transform.position, r.transform.rotation, r.transform.lossyScale, bounds.center);
                }
            }
            var glow = Resources.Load<Material>("Materials/Projectile_Bolt");
            for (int i = 0; i < (boss ? 36 : 20); i++)
            {
                var go = Primitive("Spark", PrimitiveType.Cube, glow);
                go.transform.position = bounds.center + Random.insideUnitSphere * size * .15f;
                go.transform.localScale = new Vector3(.018f, .018f, .09f);
                fragments.Add(new Fragment { part = go.transform, velocity = Random.onUnitSphere * Random.Range(4f, 8f) + Vector3.up * 2, spin = Random.onUnitSphere * 360, scale = go.transform.localScale, spark = true });
            }
            flash = Primitive("ExplosionFlash", PrimitiveType.Sphere, glow); flash.transform.position = bounds.center;
            flashLight = flash.AddComponent<Light>(); flashLight.color = new Color(1, .55f, .12f); flashLight.range = size * 4; flashLight.intensity = boss ? 8 : 4; flashLight.shadows = LightShadows.None;
            CreateShockwave(bounds.center, boss, glow);
            fireParticles = CreateParticles("ExplosionFire", bounds.center, glow, boss, false);
            smokeParticles = CreateParticles("ExplosionSmoke", bounds.center, Resources.Load<Material>("Materials/Placeholder_Lit"), boss, true);
            HideForSnapshot();
            var audio = Audio.AudioService.Instance;
            if (audio != null) audio.Play("SND-ROBOT-Explosion", bounds.center, boss ? 1 : .7f, 20, 0, audio.enemies, false);
        }

        void CreateShockwave(Vector3 center, bool boss, Material material)
        {
            for (int i = 0; i < 3; i++)
            {
                var ring = Primitive("ExplosionShockwave", PrimitiveType.Cylinder, material);
                ring.transform.position = center + Vector3.up * (.08f * i);
                ring.transform.localScale = new Vector3(.12f, .012f, .12f);
                fragments.Add(new Fragment
                {
                    part = ring.transform,
                    velocity = Vector3.zero,
                    spin = new Vector3(0, 80 + i * 35, 0),
                    scale = Vector3.one * size * (boss ? 4.5f : 2.8f),
                    spark = true
                });
            }
        }

        ParticleSystem CreateParticles(string label, Vector3 center, Material material, bool boss, bool smoke)
        {
            var go = new GameObject(label, typeof(ParticleSystem));
            go.transform.SetParent(burst.transform, false); go.transform.position = center;
            var ps = go.GetComponent<ParticleSystem>();
            ps.Stop(true, ParticleSystemStopBehavior.StopEmittingAndClear);
            var main = ps.main; main.loop = false; main.playOnAwake = false; main.simulationSpace = ParticleSystemSimulationSpace.World;
            main.duration = smoke ? 1.5f : .45f; main.startLifetime = smoke ? new ParticleSystem.MinMaxCurve(1.4f, 2.4f) : new ParticleSystem.MinMaxCurve(.45f, .9f);
            main.startSpeed = smoke ? new ParticleSystem.MinMaxCurve(.4f, 1.4f) : new ParticleSystem.MinMaxCurve(3f, boss ? 10f : 7f);
            main.startSize = smoke ? new ParticleSystem.MinMaxCurve(size * .25f, size * .65f) : new ParticleSystem.MinMaxCurve(.04f, .13f);
            main.startColor = smoke ? new ParticleSystem.MinMaxGradient(new Color(.08f, .07f, .06f, .7f), new Color(.28f, .20f, .12f, .35f)) : new ParticleSystem.MinMaxGradient(new Color(1f, .25f, .02f, 1), new Color(1f, .9f, .18f, 1));
            main.gravityModifier = smoke ? -.08f : .7f; main.maxParticles = boss ? 100 : 60;
            var emission = ps.emission; emission.enabled = true; emission.rateOverTime = smoke ? 10 : 0;
            emission.SetBursts(new[] { new ParticleSystem.Burst(0, (short)(boss ? (smoke ? 28 : 70) : (smoke ? 18 : 42))) });
            var shape = ps.shape; shape.shapeType = ParticleSystemShapeType.Sphere; shape.radius = size * .22f;
            var color = ps.colorOverLifetime; color.enabled = true;
            var gradient = new Gradient(); gradient.SetKeys(
                new[] { new GradientColorKey(Color.white, 0), new GradientColorKey(smoke ? new Color(.18f, .13f, .1f) : new Color(1f, .12f, .01f), 1) },
                new[] { new GradientAlphaKey(1, 0), new GradientAlphaKey(0, 1) });
            color.color = gradient;
            var renderer = ps.GetComponent<ParticleSystemRenderer>(); renderer.sharedMaterial = material; renderer.renderMode = smoke ? ParticleSystemRenderMode.Billboard : ParticleSystemRenderMode.Stretch; renderer.lengthScale = smoke ? 0 : 2.4f;
            ps.Play(); return ps;
        }

        static bool PrimaryLod(Renderer r)
        {
            var lod = r.GetComponentInParent<LODGroup>();
            return lod == null || lod.GetLODs().Length == 0 || lod.GetLODs()[0].renderers.Contains(r);
        }

        void SplitShell(Mesh source, Transform frame, Material[] materials, Vector3 center)
        {
            var vertices = source.vertices; var normals = source.normals; var uv = source.uv; var triangles = source.triangles;
            var pivot = source.bounds.center;
            var groups = new List<int>[8]; for (int i = 0; i < groups.Length; i++) groups[i] = new List<int>();
            for (int i = 0; i < triangles.Length; i += 3)
            {
                var p = (vertices[triangles[i]] + vertices[triangles[i + 1]] + vertices[triangles[i + 2]]) / 3 - pivot;
                int bucket = (p.x > 0 ? 1 : 0) | (p.y > 0 ? 2 : 0) | (p.z > 0 ? 4 : 0);
                groups[bucket].Add(triangles[i]); groups[bucket].Add(triangles[i + 1]); groups[bucket].Add(triangles[i + 2]);
            }
            foreach (var group in groups)
            {
                if (group.Count == 0) continue;
                var mesh = new Mesh { name = "BrokenShell", indexFormat = UnityEngine.Rendering.IndexFormat.UInt32 };
                var v = group.Select(i => vertices[i]).ToArray();
                var origin = v.Aggregate(Vector3.zero, (a, b) => a + b) / v.Length;
                mesh.vertices = v.Select(p => p - origin).ToArray();
                mesh.triangles = Enumerable.Range(0, v.Length).ToArray();
                if (normals.Length == vertices.Length) mesh.normals = group.Select(i => normals[i]).ToArray(); else mesh.RecalculateNormals();
                if (uv.Length == vertices.Length) mesh.uv = group.Select(i => uv[i]).ToArray();
                mesh.RecalculateBounds(); ownedMeshes.Add(mesh);
                AddPart(mesh, materials.Take(1).ToArray(), frame.TransformPoint(origin), frame.rotation, frame.lossyScale, center);
            }
        }

        void AddPart(Mesh mesh, Material[] materials, Vector3 position, Quaternion rotation, Vector3 scale, Vector3 center)
        {
            var go = new GameObject("BrokenRobotPart", typeof(MeshFilter), typeof(MeshRenderer)); go.transform.SetParent(burst.transform, false);
            go.transform.SetPositionAndRotation(position, rotation); go.transform.localScale = scale;
            go.GetComponent<MeshFilter>().sharedMesh = mesh; go.GetComponent<MeshRenderer>().sharedMaterials = materials;
            var direction = position - center; if (direction.sqrMagnitude < .01f) direction = Random.onUnitSphere;
            fragments.Add(new Fragment { part = go.transform, velocity = direction.normalized * Random.Range(1.5f, 3.5f) + Vector3.up * 2.8f, spin = Random.onUnitSphere * 240, scale = scale });
        }

        GameObject Primitive(string label, PrimitiveType type, Material material)
        {
            var go = GameObject.CreatePrimitive(type); go.name = label; go.transform.SetParent(burst.transform, false);
            go.GetComponent<Collider>().enabled = false; Destroy(go.GetComponent<Collider>());
            var r = go.GetComponent<Renderer>(); r.sharedMaterial = material; r.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            return go;
        }

        public void HideForSnapshot()
        {
            Cache(); Hidden = true;
            foreach (var r in renderers) if (r != null) r.enabled = false;
            foreach (var c in colliders) if (c != null) c.enabled = false;
        }

        public void RestoreVisuals()
        {
            ClearBurst(); Cache(); Hidden = false;
            for (int i = 0; i < renderers.Length; i++) if (renderers[i] != null) renderers[i].enabled = rendererEnabled[i];
            for (int i = 0; i < colliders.Length; i++) if (colliders[i] != null) colliders[i].enabled = colliderEnabled[i];
        }

        void Update()
        {
            if (burst == null) return;
            float dt = Time.deltaTime; elapsed += dt;
            if (flash != null)
            {
                flash.SetActive(elapsed < .5f);
                flash.transform.localScale = Vector3.one * size * (.1f + elapsed * 2.6f);
                flashLight.intensity = Mathf.Max(0, 10 * (1 - elapsed / .5f));
            }
            foreach (var f in fragments)
            {
                if (f.part == null) continue;
                if (f.part.name == "ExplosionShockwave")
                {
                    float delay = fragments.IndexOf(f) * .035f;
                    float p = Mathf.Clamp01((elapsed - delay) / .8f);
                    f.part.localScale = new Vector3(f.scale.x * p, size * .015f, f.scale.z * p);
                    if (elapsed > .9f + delay) f.part.gameObject.SetActive(false);
                    else f.part.Rotate(f.spin * dt, Space.World);
                    continue;
                }
                if (f.spark && elapsed > 1.1f) { f.part.gameObject.SetActive(false); continue; }
                f.velocity += Vector3.down * 9.81f * dt;
                var step = f.velocity * dt;
                if (step.sqrMagnitude > 0 && Physics.Raycast(f.part.position, step.normalized, out var hit, step.magnitude + .03f, GameLayers.CoverMask, QueryTriggerInteraction.Ignore))
                { f.part.position = hit.point + hit.normal * .035f; f.velocity = Vector3.Reflect(f.velocity, hit.normal) * .3f; }
                else f.part.position += step;
                f.part.Rotate(f.spin * dt, Space.World);
                f.part.localScale = f.scale * (1 - Mathf.Clamp01((elapsed - 5) / 2f));
            }
            if (elapsed > 7f) ClearBurst();
        }

        void ClearBurst() { if (burst != null) { burst.SetActive(false); Destroy(burst); } burst = null; fragments.Clear(); foreach (var mesh in ownedMeshes) if (mesh != null) Destroy(mesh); ownedMeshes.Clear(); }
        void OnDestroy() { ClearBurst(); }
    }
}
