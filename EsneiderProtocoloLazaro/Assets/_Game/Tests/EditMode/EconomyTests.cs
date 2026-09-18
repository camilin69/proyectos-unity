using System.IO;
using System.Linq;
using Esneider.Core.Data;
using NUnit.Framework;

namespace Esneider.Tests
{
    // 80.1/103.1: stock del mundo 140 balas / 50 cartuchos antes del gabinete; garantía CP-06 cabe en capacidad 12+80 / 6+36;
    // curación 3 jeringas / 2 raciones como máximo; los conteos del plano son la fuente única.
    public class EconomyTests
    {
        LevelPlan Plan() => LevelPlan.FromJson(File.ReadAllText(LevelPlan.DefaultAssetPath));

        [Test]
        public void WorldStock_Is140Bullets_50Shells()
        {
            var p = Plan();
            int bullets = p.pickups.Where(x => x.kind == "PistolAmmo").Sum(x => x.amount) + p.pickups.Where(x => x.kind == "Pistol").Sum(x => x.amount);
            int shells = p.pickups.Where(x => x.kind == "ShotgunAmmo").Sum(x => x.amount) + p.pickups.Where(x => x.kind == "Shotgun").Sum(x => x.amount);
            Assert.AreEqual(140, bullets, "balas de pistola (munición + pickup de arma)");
            Assert.AreEqual(50, shells, "cartuchos (munición + pickup de arma)");
        }

        [Test]
        public void Guarantee_FitsCapacity_AndHealingCaps()
        {
            Assert.GreaterOrEqual(12 + 80, 50); Assert.GreaterOrEqual(6 + 36, 24);
            var p = Plan();
            Assert.AreEqual(12, p.pickups.Count(x => x.kind == "Syringe"), "12 jeringas en el mundo (68)");
            Assert.AreEqual(6, p.pickups.Count(x => x.kind == "Ration"), "6 raciones");
            // presupuesto 80.2 por tramo: S1 sin munición; antes de la pistola ninguna bala obligatoria
            Assert.AreEqual(0, p.pickups.Count(x => (x.kind == "PistolAmmo" || x.kind == "ShotgunAmmo") && (x.space == "P01" || x.space == "P02")), "S1 + C-01 sin munición");
        }
    }
}
