using System;
using System.Collections.Generic;

namespace Esneider.Core
{
    public enum ActionPhase { Idle, Running, Completed, Cancelled }

    // Sección 86.6: Begin/Commit/Cancel/Complete con guardas. Los commits son puntos temporales dentro de la duración;
    // un commit ejecutado nunca se repite ni se deshace por cancelar después.
    public class ActionTransaction
    {
        static int _nextId = 1;

        public readonly int Id;
        public readonly string Type;
        public readonly float Duration;
        public ActionPhase Phase { get; private set; } = ActionPhase.Idle;
        public float Elapsed { get; private set; }
        public string EndReason { get; private set; } = "";

        readonly List<(float at, Action fn, bool done)> _commits = new List<(float, Action, bool)>();
        public int CommitsDone { get; private set; }
        public bool AnyCommitDone => CommitsDone > 0;

        public ActionTransaction(string type, float duration)
        {
            Id = _nextId++; Type = type; Duration = duration;
        }

        public ActionTransaction AddCommit(float atSeconds, Action fn)
        {
            if (atSeconds > Duration) throw new ArgumentException($"Commit {atSeconds}s fuera de la duración {Duration}s de {Type}");
            _commits.Add((atSeconds, fn, false));
            return this;
        }

        public void Begin()
        {
            if (Phase != ActionPhase.Idle) return;
            Phase = ActionPhase.Running; Elapsed = 0f;
        }

        // Avanza el reloj; devuelve true cuando la acción termina en este paso.
        public bool Tick(float dt)
        {
            if (Phase != ActionPhase.Running) return false;
            Elapsed += dt;
            for (int i = 0; i < _commits.Count; i++)
            {
                var c = _commits[i];
                if (!c.done && Elapsed >= c.at) { _commits[i] = (c.at, c.fn, true); CommitsDone++; c.fn?.Invoke(); }
            }
            if (Elapsed >= Duration) { Complete(); return true; }
            return false;
        }

        // Avanza el reloj sin evaluar commits fijos (acciones con commits calculados en tiempo de ejecución, 86.4).
        public void Advance(float dt) { if (Phase == ActionPhase.Running) Elapsed += dt; }

        public void Complete()
        {
            if (Phase != ActionPhase.Running) return;
            for (int i = 0; i < _commits.Count; i++)
            {
                var c = _commits[i];
                if (!c.done) { _commits[i] = (c.at, c.fn, true); CommitsDone++; c.fn?.Invoke(); }
            }
            Phase = ActionPhase.Completed; EndReason = "complete";
        }

        public void Cancel(string reason)
        {
            if (Phase != ActionPhase.Running) return;
            Phase = ActionPhase.Cancelled; EndReason = reason;
        }

        public bool IsRunning => Phase == ActionPhase.Running;
        public bool IsFinished => Phase == ActionPhase.Completed || Phase == ActionPhase.Cancelled;
    }
}
