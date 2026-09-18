using System.IO;
using System.Text;
using Esneider.Core.Persistence;
using NUnit.Framework;
using UnityEngine;

namespace Esneider.Tests
{
    // 89.5: truncado, checksum incorrecto, GUID duplicado, campo negativo, versión futura, backup corrupto, dos checkpoints seguidos.
    public class SaveStoreTests
    {
        string _dir; SaveFileStore _store;

        [SetUp] public void SetUp() { _dir = Path.Combine(Path.GetTempPath(), "esneider-tests", System.Guid.NewGuid().ToString("N")); _store = new SaveFileStore(_dir); }
        [TearDown] public void TearDown() { try { Directory.Delete(_dir, true); } catch { } }

        static SaveData Valid(string cp, long seq)
        {
            var d = new SaveData { checkpointId = cp, saveSequence = seq, health = 60, hasPistol = true, pistolMag = 5, pistolReserve = 20, syringeCount = 1, rationCount = 1, contentVersion = "0.1.0" };
            d.world.entities.Add(new EntityState { guid = "g1", kind = EntityKind.Enemy, hp = 30 });
            d.world.entities.Add(new EntityState { guid = "g2", kind = EntityKind.Pickup, amount = 2 });
            return d;
        }

        [Test]
        public void CommitThenLoadRoundTrip()
        {
            Assert.IsTrue(_store.Commit(Valid("CP-01", 1)), _store.LastError);
            var d = _store.LoadBest(out var src);
            Assert.IsNotNull(d); Assert.AreEqual("checkpoint.json", src); Assert.AreEqual("CP-01", d.checkpointId); Assert.AreEqual(20, d.pistolReserve); Assert.AreEqual(2, d.world.entities.Count);
        }

        [Test]
        public void TwoCheckpointsRotateGenerations()
        {
            Assert.IsTrue(_store.Commit(Valid("CP-01", 1)));
            Assert.IsTrue(_store.Commit(Valid("CP-02", 2)));
            Assert.IsTrue(File.Exists(_store.Backup1Path));
            Assert.AreEqual("CP-02", _store.LoadBest(out _).checkpointId);
            Assert.AreEqual("CP-01", SaveFileStore.Unwrap(File.ReadAllText(_store.Backup1Path), out _).checkpointId, "la generación previa se conserva");
        }

        [Test]
        public void TruncatedActiveFallsBackToBackup()
        {
            _store.Commit(Valid("CP-01", 1)); _store.Commit(Valid("CP-02", 2));
            var text = File.ReadAllText(_store.ActivePath); File.WriteAllText(_store.ActivePath, text.Substring(0, text.Length / 2));
            var d = _store.LoadBest(out var src);
            Assert.IsNotNull(d); Assert.AreEqual("checkpoint.bak1.json", src); Assert.AreEqual("CP-01", d.checkpointId);
            StringAssert.Contains("Se recuperó el checkpoint anterior", _store.LastRecoveryNotice);
            Assert.IsTrue(Directory.GetFiles(_dir, "checkpoint.json.invalid-*").Length == 1, "copia inválida conservada para diagnóstico");
        }

        [Test]
        public void WrongChecksumIsRejected()
        {
            _store.Commit(Valid("CP-01", 1));
            // misma longitud, contenido alterado (también en el envelope): el checksum del payload lo detecta
            var text = File.ReadAllText(_store.ActivePath).Replace("CP-01", "CP-09");
            Assert.IsNull(SaveFileStore.Unwrap(text, out var why)); StringAssert.Contains("checksum", why);
        }

        [Test]
        public void SemanticRejections()
        {
            var dup = Valid("CP-01", 1); dup.world.entities.Add(new EntityState { guid = "g1", kind = EntityKind.Pickup });
            Assert.IsFalse(SaveValidator.Validate(dup).ok);
            var neg = Valid("CP-01", 1); neg.pistolReserve = -1; Assert.IsFalse(SaveValidator.Validate(neg).ok);
            var over = Valid("CP-01", 1); over.health = 120; Assert.IsFalse(SaveValidator.Validate(over).ok);
            var zombie = Valid("CP-01", 1); zombie.world.entities[0].hp = 0; zombie.world.entities[0].dead = false; Assert.IsFalse(SaveValidator.Validate(zombie).ok);
            var taken = Valid("CP-01", 1); taken.world.entities[1].taken = true; taken.world.entities[1].amount = 3; Assert.IsFalse(SaveValidator.Validate(taken).ok);
            var d29 = Valid("CP-01", 1); d29.world.flags.Add("DOOR_D29_OPEN"); Assert.IsFalse(SaveValidator.Validate(d29).ok);
            Assert.IsFalse(_store.Commit(neg), "un candidato inválido nunca se promueve");
            Assert.IsFalse(File.Exists(_store.ActivePath));
        }

        [Test]
        public void FutureSchemaVersionIsPreservedNotOpened()
        {
            var d = Valid("CP-01", 1); d.schemaVersion = SaveData.CurrentSchemaVersion + 1;
            File.WriteAllText(_store.ActivePath, JsonUtility.ToJson(SaveFileStore.Wrap(d)));
            Assert.IsNull(_store.LoadBest(out _));
            Assert.IsTrue(File.Exists(_store.ActivePath), "el guardado de versión futura se conserva");
        }

        [Test]
        public void OrphanTempIsNotACheckpoint()
        {
            File.WriteAllText(_store.TempPath, "{\"schemaVersion\":1");
            Assert.IsNull(_store.LoadBest(out _));
            Assert.IsTrue(File.Exists(_store.TempPath));
        }

        [Test]
        public void RegistryEventsAreIdempotent()
        {
            var reg = new WorldStateRegistry();
            reg.GetOrCreate("p1", "Pickup", "REG-S1", EntityKind.Pickup);
            Assert.IsTrue(reg.Apply(WorldEventKind.PickupTaken, "p1", s => s.amount = 2, externalSequence: 10));
            Assert.IsFalse(reg.Apply(WorldEventKind.PickupTaken, "p1", s => s.amount = 0, externalSequence: 10), "mismo evento dos veces no se aplica");
            reg.TryGet("p1", out var st); Assert.AreEqual(2, st.amount);
            var snap = reg.Snapshot(); st.amount = 0;
            Assert.AreEqual(2, snap.entities[0].amount, "el snapshot es una copia inmutable");
            var reg2 = new WorldStateRegistry(); reg2.Restore(snap); reg2.TryGet("p1", out var st2); Assert.AreEqual(2, st2.amount);
        }
    }
}
