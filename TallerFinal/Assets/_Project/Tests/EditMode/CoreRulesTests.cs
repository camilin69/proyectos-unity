using NUnit.Framework;
using UnityEngine;

namespace Dream.Tests
{
    // Reglas puras: puntaje, reloj y bandas de cine.
    public class CoreRulesTests
    {
        [Test]
        public void ElBonoBajaConElTiempoYNuncaEsNegativo()
        {
            Assert.AreEqual(ScoreSystem.MaxQuickBonus, ScoreSystem.QuickBonus(0f));
            Assert.Less(ScoreSystem.QuickBonus(120f), ScoreSystem.QuickBonus(30f));
            Assert.AreEqual(0, ScoreSystem.QuickBonus(ScoreSystem.QuickBonusWindow * 3f));
        }

        [Test]
        public void ElSolSaleDeDiaYSeEscondeDeNoche()
        {
            Assert.Greater(TimeOfDay.SunElevation(12f, 6f, 18.5f, 64f), 55f);
            Assert.Greater(TimeOfDay.SunElevation(7f, 6f, 18.5f, 64f), 0f);
            Assert.Less(TimeOfDay.SunElevation(20f, 6f, 18.5f, 64f), -4f);
            Assert.Less(TimeOfDay.SunElevation(0f, 6f, 18.5f, 64f), -30f);
            Assert.Less(TimeOfDay.SunElevation(23.99f, 6f, 18.5f, 64f), -30f);
        }

        [Test]
        public void LaHoraSeEscribeComoUnReloj()
        {
            Assert.AreEqual("07:00", TimeOfDay.Format(7f));
            Assert.AreEqual("21:20", TimeOfDay.Format(21f + 20f / 60f + 0.001f));
            Assert.AreEqual("00:00", TimeOfDay.Format(24f));
        }

        [Test]
        public void LasBandasDejanElCuadroEn239()
        {
            float f = Letterbox.BarFraction(1920f, 1080f);
            float visible = 1080f * (1f - 2f * f);
            Assert.AreEqual(1920f / 2.39f, visible, 0.5f);
            Assert.AreEqual(0f, Letterbox.BarFraction(2560f, 1000f), 1e-5f, "una pantalla mas ancha que 2.39 no lleva bandas");
        }

        [Test]
        public void LasFocalesSonDeUnaCamaraReal()
        {
            Assert.AreEqual(53.1f, CineRig.FocalToFov(24f), 0.2f);
            Assert.AreEqual(37.8f, CineRig.FocalToFov(35f), 0.2f);
            Assert.AreEqual(10.2f, CineRig.FocalToFov(135f), 0.2f);
        }
    }
}
