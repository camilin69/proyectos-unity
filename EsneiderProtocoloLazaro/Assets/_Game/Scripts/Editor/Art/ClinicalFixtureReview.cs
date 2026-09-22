using UnityEditor;
using UnityEngine;

namespace Esneider.EditorTools
{
    public static class ClinicalFixtureReview
    {
        public static string IntegrateLamp()
        {
            const string asset = "OBJ-048_LamparaClinica";
            string result = FurnitureReview.Integrate(asset);
            var root = PrefabUtility.LoadPrefabContents(FurnitureReview.Prefab(asset));
            try
            {
                var aperture = new GameObject("Head aperture light");
                aperture.transform.SetParent(root.transform,false);
                aperture.transform.localPosition = new Vector3(1.22f,2.085f,0);
                aperture.transform.localRotation = Quaternion.Euler(90,0,0);
                var light = aperture.AddComponent<Light>();
                light.type = LightType.Spot; light.spotAngle = 65; light.innerSpotAngle = 42;
                light.range = 3; light.intensity = 2; light.color = new Color(.83f,.95f,1);
                light.shadows = LightShadows.None;
                // Opt in per mounted instance; avoid making every clinical lamp dynamic.
                light.enabled = false;
                PrefabUtility.SaveAsPrefabAsset(root,FurnitureReview.Prefab(asset));
            }
            finally { PrefabUtility.UnloadPrefabContents(root); }
            AssetDatabase.SaveAssets(); return result;
        }
    }
}
