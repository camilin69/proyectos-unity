using System.Collections.Generic;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

namespace Esneider.Tests
{
    // 49.8 / PIL-14 · el contacto del pie se mide sobre el FBX YA IMPORTADO, no sobre el .blend.
    //
    // El ciclo de marcha original interpolaba entre dos poses opuestas sin pose de paso, así que la pierna en vuelo
    // cruzaba la vertical -que es donde el pie queda más bajo- y el bot arrastraba los pies: 7.3 mm de despeje
    // medidos en el Vigía y 7.9 mm en el Custodio, para piernas de 0.70 y 0.98 m. Ningún test lo detectaba porque
    // ningún test miraba la geometría de la animación.
    //
    // El medidor de Blender (SourceArt/Scripts/measure_contacts.py) comprueba esto en origen, pero entre el .blend y
    // lo que Unity reproduce hay una exportación y una importación. Esta prueba cierra ese hueco: muestrea el clip
    // sobre la jerarquía instanciada y mide los mismos números contra los mismos umbrales.
    public class WalkContactTests
    {
        const float ClearanceMin = 0.030f;   // el pie en vuelo sube al menos 3 cm (G-06)
        const float GroundBand = 0.015f;     // el pie de apoyo no se separa más de 15 mm del punto más bajo (G-03)
        const int Samples = 48;

        static readonly string[] Prefabs =
        {
            "Assets/_Game/Prefabs/Enemies/BOT-01_Vigia.prefab",
            "Assets/_Game/Prefabs/Enemies/BOT-02_Custodio.prefab",
            "Assets/_Game/Prefabs/Enemies/BOT-03_Archivista.prefab",
        };

        [Test]
        public void WalkClips_LiftTheSwingFootAndKeepTheOtherOnTheGround()
        {
            var problemas = new List<string>();
            var resumen = new List<string>();

            foreach (var path in Prefabs)
            {
                var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(path);
                Assert.IsNotNull(prefab, "falta el prefab " + path);
                var go = Object.Instantiate(prefab);
                go.transform.position = Vector3.zero;
                go.transform.rotation = Quaternion.identity;
                try
                {
                    var clip = FindWalkClip(go);
                    Assert.IsNotNull(clip, "el prefab " + path + " no trae clip de marcha");
                    // SampleAnimation no hace nada sobre un clip genérico si el objeto no tiene Animator.
                    if (go.GetComponent<Animator>() == null) go.AddComponent<Animator>();
                    // Las mallas del pie y el hueso del pie se llaman igual; el que se mueve es el del esqueleto,
                    // así que hay que buscar dentro del armature y no en el primer objeto que coincida.
                    var esqueleto = FindDeep(go.transform, "root") ?? go.transform;
                    var pieL = FindDeep(esqueleto, "foot_L");
                    var pieR = FindDeep(esqueleto, "foot_R");
                    Assert.IsNotNull(pieL, "sin hueso foot_L en " + path);
                    Assert.IsNotNull(pieR, "sin hueso foot_R en " + path);

                    var alturaL = new float[Samples];
                    var alturaR = new float[Samples];
                    for (int i = 0; i < Samples; i++)
                    {
                        clip.SampleAnimation(go, clip.length * i / (Samples - 1f));
                        alturaL[i] = pieL.position.y;
                        alturaR[i] = pieR.position.y;
                    }

                    // El suelo del ciclo es la cota más baja que alcanza cualquiera de los dos pies.
                    float suelo = Mathf.Min(Mathf.Min(alturaL), Mathf.Min(alturaR));
                    float despejeL = Mathf.Max(alturaL) - suelo;
                    float despejeR = Mathf.Max(alturaR) - suelo;
                    float apoyoPeor = 0f;
                    for (int i = 0; i < Samples; i++)
                        apoyoPeor = Mathf.Max(apoyoPeor, Mathf.Min(alturaL[i], alturaR[i]) - suelo);

                    string id = System.IO.Path.GetFileNameWithoutExtension(path);
                    resumen.Add(string.Format("{0}: despeje L {1:F0} mm / R {2:F0} mm, separación máxima del pie de apoyo {3:F0} mm",
                        id, despejeL * 1000f, despejeR * 1000f, apoyoPeor * 1000f));

                    if (despejeL < ClearanceMin || despejeR < ClearanceMin)
                        problemas.Add(string.Format("{0} arrastra los pies: despeje L {1:F1} mm, R {2:F1} mm (mínimo {3:F0} mm)",
                            id, despejeL * 1000f, despejeR * 1000f, ClearanceMin * 1000f));
                    if (apoyoPeor > GroundBand)
                        problemas.Add(string.Format("{0} camina flotando: en algún frame el pie más bajo queda a {1:F1} mm del suelo (máximo {2:F0} mm)",
                            id, apoyoPeor * 1000f, GroundBand * 1000f));
                }
                finally { Object.DestroyImmediate(go); }
            }

            Debug.Log("Contacto de marcha medido sobre el FBX importado:\n  " + string.Join("\n  ", problemas.Count == 0 ? resumen.ToArray() : resumen.ToArray()));
            Assert.IsEmpty(problemas, string.Join("\n", problemas.ToArray()));
        }

        static AnimationClip FindWalkClip(GameObject go)
        {
            // Los clips viven en el FBX, no en el prefab. El FBX expone además una copia "__preview__" que usa el
            // inspector; hay que medir el clip real, que es el que carga el juego.
            string id = go.name.Replace("(Clone)", string.Empty);
            foreach (var sub in AssetDatabase.LoadAllAssetsAtPath("Assets/_Game/Art/Models/" + id + ".fbx"))
            {
                var clip = sub as AnimationClip;
                if (clip == null || clip.name.StartsWith("__")) continue;
                if (clip.name.ToLowerInvariant().Contains("walk")) return clip;
            }
            return null;
        }

        static Transform FindDeep(Transform root, string nombre)
        {
            if (root.name == nombre) return root;
            for (int i = 0; i < root.childCount; i++)
            {
                var hit = FindDeep(root.GetChild(i), nombre);
                if (hit != null) return hit;
            }
            return null;
        }
    }
}
