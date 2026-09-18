using System;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using UnityEngine;

namespace Esneider.Core.Persistence
{
    // 89.2/89.4: escritura transaccional (temporal → validar → promover con generaciones) y recuperación desde backups.
    public class SaveFileStore
    {
        public readonly string directory;
        public const string ActiveName = "checkpoint.json";
        public const string Backup1Name = "checkpoint.bak1.json";
        public const string Backup2Name = "checkpoint.bak2.json";
        public const string TempName = "checkpoint.tmp";

        public string ActivePath => Path.Combine(directory, ActiveName);
        public string Backup1Path => Path.Combine(directory, Backup1Name);
        public string Backup2Path => Path.Combine(directory, Backup2Name);
        public string TempPath => Path.Combine(directory, TempName);

        public string LastError { get; private set; } = "";
        public string LastRecoveryNotice { get; private set; } = "";

        public SaveFileStore(string dir) { directory = dir; Directory.CreateDirectory(directory); }

        public static string Sha256(string s)
        {
            using (var sha = SHA256.Create())
            {
                var h = sha.ComputeHash(Encoding.UTF8.GetBytes(s));
                var sb = new StringBuilder(64); foreach (var b in h) sb.Append(b.ToString("x2")); return sb.ToString();
            }
        }

        public static SaveEnvelope Wrap(SaveData data)
        {
            var payload = JsonUtility.ToJson(data);
            return new SaveEnvelope
            {
                schemaVersion = data.schemaVersion, contentVersion = data.contentVersion, buildId = data.buildId, campaignId = data.campaignId,
                saveSequence = data.saveSequence, checkpointId = data.checkpointId, createdUtc = DateTime.UtcNow.ToString("o"),
                payloadLength = Encoding.UTF8.GetByteCount(payload), payloadChecksum = Sha256(payload), payload = payload
            };
        }

        // Devuelve null y razón si el archivo no es un checkpoint íntegro.
        public static SaveData Unwrap(string text, out string reason)
        {
            reason = "";
            if (string.IsNullOrWhiteSpace(text)) { reason = "vacío"; return null; }
            SaveEnvelope env;
            try { env = JsonUtility.FromJson<SaveEnvelope>(text); } catch (Exception e) { reason = "envelope ilegible: " + e.Message; return null; }
            if (env == null || string.IsNullOrEmpty(env.payload)) { reason = "envelope sin payload"; return null; }
            if (Encoding.UTF8.GetByteCount(env.payload) != env.payloadLength) { reason = "longitud de payload no coincide (truncado)"; return null; }
            if (!string.Equals(Sha256(env.payload), env.payloadChecksum, StringComparison.OrdinalIgnoreCase)) { reason = "checksum incorrecto"; return null; }
            if (env.schemaVersion > SaveData.CurrentSchemaVersion) { reason = $"schemaVersion {env.schemaVersion} de una versión futura"; return null; }
            SaveData data;
            try { data = JsonUtility.FromJson<SaveData>(env.payload); } catch (Exception e) { reason = "payload ilegible: " + e.Message; return null; }
            if (data == null) { reason = "payload nulo"; return null; }
            if (data.saveSequence != env.saveSequence || data.checkpointId != env.checkpointId) { reason = "envelope y payload no concuerdan"; return null; }
            var v = SaveValidator.Validate(data);
            if (!v.ok) { reason = "validación semántica: " + v.reason; return null; }
            return data;
        }

        // Pasos 5–10 de 89.2. Nunca borra el activo antes de que el candidato sea válido.
        public bool Commit(SaveData data)
        {
            LastError = "";
            try
            {
                var v = SaveValidator.Validate(data);
                if (!v.ok) { LastError = "candidato inválido: " + v.reason; return false; }
                var text = JsonUtility.ToJson(Wrap(data));
                using (var fs = new FileStream(TempPath, FileMode.Create, FileAccess.Write, FileShare.None))
                {
                    var bytes = Encoding.UTF8.GetBytes(text);
                    fs.Write(bytes, 0, bytes.Length); fs.Flush(true);
                }
                // reabrir y comprobar antes de promover
                var check = Unwrap(File.ReadAllText(TempPath, Encoding.UTF8), out var why);
                if (check == null) { LastError = "candidato reabierto inválido: " + why; return false; }
                if (File.Exists(ActivePath))
                {
                    // rotación de generaciones: activo → bak1 → bak2; el más antiguo se descarta solo tras promover
                    if (File.Exists(Backup2Path)) File.Delete(Backup2Path);
                    if (File.Exists(Backup1Path)) File.Move(Backup1Path, Backup2Path);
                    File.Replace(TempPath, ActivePath, Backup1Path);
                }
                else File.Move(TempPath, ActivePath);
                return true;
            }
            catch (Exception e) { LastError = e.GetType().Name + ": " + e.Message; return false; }
        }

        // 89.4: activo → bak1 → bak2; conserva copias inválidas para diagnóstico.
        public SaveData LoadBest(out string source)
        {
            LastRecoveryNotice = ""; source = "";
            string[] candidates = { ActivePath, Backup1Path, Backup2Path };
            for (int i = 0; i < candidates.Length; i++)
            {
                var p = candidates[i];
                if (!File.Exists(p)) continue;
                var data = Unwrap(File.ReadAllText(p, Encoding.UTF8), out var why);
                if (data != null)
                {
                    source = Path.GetFileName(p);
                    if (i > 0) LastRecoveryNotice = $"Se recuperó el checkpoint anterior ({data.checkpointId}) por un problema con el guardado: {LastError}";
                    return data;
                }
                if (i == 0) LastError = why;
                try { File.Copy(p, p + ".invalid-" + DateTime.UtcNow.ToString("yyyyMMddHHmmss"), true); } catch { }
            }
            return null;
        }

        public bool HasAnyCandidate => File.Exists(ActivePath) || File.Exists(Backup1Path) || File.Exists(Backup2Path);
    }
}
