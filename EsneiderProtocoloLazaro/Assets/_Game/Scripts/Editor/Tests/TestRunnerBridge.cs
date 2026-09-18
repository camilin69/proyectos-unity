using System.IO;
using System.Text;
using UnityEditor;
using UnityEditor.TestTools.TestRunner.Api;
using UnityEngine;

namespace Esneider.EditorTools
{
    // Lanza el Test Runner desde código y escribe el resultado en disco: sobrevive a los domain reloads que
    // interrumpen el puente MCP (registro EX-02). Salida: docs/produccion/evidencia/tests_<modo>.md
    public static class TestRunnerBridge
    {
        class Callbacks : ICallbacks
        {
            readonly string _path; readonly StringBuilder _sb = new StringBuilder(); int _passed, _failed, _skipped;
            public Callbacks(string path) { _path = path; }
            public void RunStarted(ITestAdaptor t) { File.WriteAllText(_path, "RUNNING\n"); }
            public void TestStarted(ITestAdaptor t) { }
            public void TestFinished(ITestResultAdaptor r)
            {
                if (r.Test.IsSuite) return;
                if (r.TestStatus == TestStatus.Passed) _passed++; else if (r.TestStatus == TestStatus.Failed) _failed++; else _skipped++;
                _sb.AppendLine($"| {r.Test.FullName} | {r.TestStatus} | {r.Duration:F2}s | {(r.Message ?? "").Replace("\n", " ").Replace("\r", "").Trim()} |");
            }
            public void RunFinished(ITestResultAdaptor r)
            {
                var head = $"# Test run {r.Test.Name} · {System.DateTime.Now:yyyy-MM-dd HH:mm} · passed {_passed} · failed {_failed} · skipped {_skipped}\n\n| Test | Estado | Duración | Mensaje |\n|---|---|---|---|\n";
                File.WriteAllText(_path, head + _sb + $"\nDONE {(_failed == 0 ? "PASS" : "FAIL")}\n");
                Debug.Log($"TestRunnerBridge: {_passed} passed, {_failed} failed → {_path}");
            }
        }

        public static string Run(TestMode mode, string assemblyName)
        {
            var dir = Path.GetFullPath(Path.Combine(Application.dataPath, "../../docs/produccion/evidencia"));
            Directory.CreateDirectory(dir);
            var path = Path.Combine(dir, $"tests_{mode}.md");
            var api = ScriptableObject.CreateInstance<TestRunnerApi>();
            api.RegisterCallbacks(new Callbacks(path));
            var filter = new Filter { testMode = mode };
            if (!string.IsNullOrEmpty(assemblyName)) filter.assemblyNames = new[] { assemblyName };
            api.Execute(new ExecutionSettings(filter));
            return path;
        }

        [MenuItem("Esneider/Tests/Run EditMode")] public static void RunEdit() => Run(TestMode.EditMode, "Esneider.Tests.EditMode");
        [MenuItem("Esneider/Tests/Run PlayMode")] public static void RunPlay() => Run(TestMode.PlayMode, "Esneider.Tests.PlayMode");
    }
}
