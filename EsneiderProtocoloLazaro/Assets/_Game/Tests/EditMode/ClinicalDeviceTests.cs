using Esneider.World;
using NUnit.Framework;
using UnityEngine;

namespace Esneider.Tests
{
    public class ClinicalDeviceTests
    {
        [Test] public void PausedTimeDoesNotAdvanceAndChecksRetainRemainder()
        {
            var root = new GameObject("Device test");
            try
            {
                var status = root.AddComponent<ClinicalDeviceStatus>();
                status.Advance(7); status.Advance(0);
                Assert.AreEqual(0,status.CompletedChecks);
                status.Advance(10); Assert.AreEqual(2,status.CompletedChecks);
                status.Advance(7); Assert.AreEqual(3,status.CompletedChecks);
            }
            finally { Object.DestroyImmediate(root); }
        }
        [Test] public void DisconnectedMonitorShowsNoFabricatedVitals()
        {
            var root = new GameObject("Device test");
            try
            {
                var status = root.AddComponent<ClinicalDeviceStatus>();
                status.display = root.AddComponent<TextMesh>();
                status.RefreshDisplay(); Assert.That(status.display.text,Does.Contain("SIN SUJETO"));
                status.checkInterval = 0; status.Advance(3); Assert.AreEqual(0,status.CompletedChecks);
                status.Advance(1); Assert.AreEqual(1,status.CompletedChecks);
                status.isPump = true; status.RefreshDisplay();
                Assert.That(status.display.text,Does.Contain("LINEA SELLADA"));
            }
            finally { Object.DestroyImmediate(root); }
        }
    }
}
