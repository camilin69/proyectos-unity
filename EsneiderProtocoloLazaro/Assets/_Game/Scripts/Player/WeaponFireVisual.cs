using System.Collections.Generic;
using Esneider.Core.Data;
using UnityEngine;
using UnityEngine.Rendering;

namespace Esneider.Player
{
    // Cosmetic only. Damage and ammunition commit once in PlayerActions before this event.
    public class WeaponFireVisual : MonoBehaviour
    {
        PlayerActions actions;
        WeaponKind kind;
        Transform mouth, flash;
        Light lightFlash;
        Material material;
        readonly List<LineRenderer> trails = new List<LineRenderer>();
        readonly List<Transform> slideParts = new List<Transform>();
        readonly List<Vector3> restPositions = new List<Vector3>();
        Vector3 origin;
        Vector3[] ends;
        float shotAt = -100;
        public int ShotsShown { get; private set; }
        public Transform Muzzle => mouth;

        public void Initialize(PlayerActions source, WeaponKind weapon)
        {
            actions = source; kind = weapon;
            material = Resources.Load<Material>("Materials/Projectile_Bolt");
            mouth = new GameObject("ShotMuzzle").transform;
            mouth.SetParent(transform, false);
            foreach (var mesh in GetComponentsInChildren<MeshFilter>())
            {
                if (mesh.name == "crown" || mesh.name == "muzzle_crown")
                    mouth.position = mesh.transform.TransformPoint(mesh.sharedMesh.bounds.center) + transform.forward * .008f;
                if (weapon == WeaponKind.Pistol && (mesh.name == "slide" || mesh.name.StartsWith("serr_") || mesh.name.StartsWith("rear_sight") || mesh.name == "front_sight" || mesh.name == "front_dot" || mesh.name == "extractor"))
                { slideParts.Add(mesh.transform); restPositions.Add(mesh.transform.localPosition); }
            }
            var glow = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            glow.name = "MuzzleFlash"; glow.GetComponent<Collider>().enabled = false; Destroy(glow.GetComponent<Collider>());
            flash = glow.transform; flash.SetParent(mouth, false);
            var renderer = glow.GetComponent<Renderer>(); renderer.sharedMaterial = material;
            renderer.shadowCastingMode = ShadowCastingMode.Off;
            renderer.receiveShadows = false;
            lightFlash = glow.AddComponent<Light>(); lightFlash.color = new Color(1, .65f, .2f);
            lightFlash.range = 1.8f; lightFlash.intensity = 2.5f; lightFlash.shadows = LightShadows.None;
            glow.SetActive(false);
            actions.PresentationMuzzle = mouth;
            actions.Fired += OnFired;
        }

        void OnFired(WeaponKind weapon, Vector3[] endpoints)
        {
            if (weapon != kind || !gameObject.activeInHierarchy) return;
            ShotsShown++; shotAt = Time.time; origin = mouth.position; ends = endpoints;
            while (trails.Count < ends.Length)
            {
                var line = new GameObject("BulletTrail").AddComponent<LineRenderer>();
                line.transform.SetParent(transform, false); line.useWorldSpace = true;
                line.positionCount = 2; line.sharedMaterial = material;
                line.shadowCastingMode = ShadowCastingMode.Off; line.receiveShadows = false;
                line.startWidth = .012f; line.endWidth = .003f; line.numCapVertices = 2;
                trails.Add(line);
            }
            Update();
        }

        void Update()
        {
            if (ends == null) return;
            float age = Time.time - shotAt;
            bool flashing = age < .055f;
            flash.gameObject.SetActive(flashing);
            if (flashing)
            {
                var direction = ends[0] - mouth.position;
                flash.rotation = Quaternion.LookRotation(direction.sqrMagnitude > .000001f ? direction.normalized : transform.forward);
                float size = kind == WeaponKind.Shotgun ? 1.4f : 1;
                flash.localScale = new Vector3(.035f, .035f, .11f) * size * (1 - age / .07f);
            }
            float slide = age < .16f ? Mathf.Sin(age / .16f * Mathf.PI) * .028f : 0;
            for (int i = 0; i < slideParts.Count; i++)
                slideParts[i].localPosition = restPositions[i] - slideParts[i].parent.InverseTransformVector(transform.forward * slide);
            for (int i = 0; i < trails.Count; i++)
            {
                if (i >= ends.Length) { trails[i].enabled = false; continue; }
                Vector3 path = ends[i] - origin; float length = path.magnitude;
                // Keep a short streak visible even for a nearby impact, then stop at that impact.
                float duration = Mathf.Clamp(length / 180f, .06f, .25f);
                trails[i].enabled = age < duration;
                if (!trails[i].enabled) continue;
                float head = Mathf.Min(length, length * (age + .015f) / duration);
                trails[i].SetPosition(0, origin + path.normalized * Mathf.Max(0, head - 1.4f));
                trails[i].SetPosition(1, origin + path.normalized * head);
            }
        }

        void OnDestroy()
        {
            if (actions == null) return;
            actions.Fired -= OnFired;
            if (actions.PresentationMuzzle == mouth) actions.PresentationMuzzle = null;
        }
    }
}
