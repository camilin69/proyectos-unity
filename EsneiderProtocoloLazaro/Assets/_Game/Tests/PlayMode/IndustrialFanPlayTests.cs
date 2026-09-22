using System.Collections;
using Esneider.World;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
#if UNITY_EDITOR
using UnityEditor;
#endif

namespace Esneider.Tests
{
    public class IndustrialFanPlayTests
    {
        [UnityTest]
        public IEnumerator VisibleFanRotatesButPauseAndDistanceStopIt()
        {
#if UNITY_EDITOR
            var root=Object.Instantiate(AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Environment/OBJ-079_VentiladorIndustrial.prefab"));
            var cameraObject=new GameObject("Fan test viewer");var camera=cameraObject.AddComponent<Camera>();cameraObject.tag="MainCamera";
            var target=new RenderTexture(256,256,24);camera.targetTexture=target;
            var existing=Object.FindObjectsByType<Camera>(FindObjectsSortMode.None);var tags=new System.Collections.Generic.Dictionary<Camera,string>();
            foreach(var c in existing)if(c!=camera&&c.CompareTag("MainCamera")){tags[c]=c.tag;c.tag="Untagged";}
            float timeScale=Time.timeScale;
            try
            {
                root.transform.position=new Vector3(10000,0,0);camera.transform.position=root.transform.position+new Vector3(0,.85f,-3);camera.transform.LookAt(root.transform.position+Vector3.up*.85f);
                var fan=root.GetComponent<IndustrialFan>();Time.timeScale=1;
                yield return null;yield return null;
                var before=fan.rotor.localRotation;yield return new WaitForSeconds(.1f);
                Assert.Greater(Quaternion.Angle(before,fan.rotor.localRotation),1f,"Visible nearby fan must advance through Update");
                Time.timeScale=0;yield return null;before=fan.rotor.localRotation;yield return new WaitForSecondsRealtime(.1f);
                Assert.Less(Quaternion.Angle(before,fan.rotor.localRotation),.01f,"Pause must freeze presentation");
                camera.transform.position=root.transform.position+new Vector3(0,.85f,-40);Time.timeScale=1;yield return null;
                before=fan.rotor.localRotation;yield return new WaitForSeconds(.1f);
                Assert.Less(Quaternion.Angle(before,fan.rotor.localRotation),.01f,"Distant fan must stop updating");
            }
            finally {Time.timeScale=timeScale;foreach(var item in tags)if(item.Key)item.Key.tag=item.Value;camera.targetTexture=null;target.Release();Object.Destroy(target);Object.Destroy(root);Object.Destroy(cameraObject);}
#else
            Assert.Ignore("Editor prefab integration test");yield break;
#endif
        }
    }
}
