using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace Esneider.Core.Persistence
{
    // 88.3/88.6: registro lógico de sesión para todas las regiones. Streaming lee de aquí; el checkpoint toma una copia inmutable.
    public class WorldStateRegistry
    {
        public static WorldStateRegistry Session { get; private set; } = new WorldStateRegistry();
        public static void ResetSession() => Session = new WorldStateRegistry();

        readonly Dictionary<string, EntityState> _entities = new Dictionary<string, EntityState>();
        readonly HashSet<string> _flags = new HashSet<string>();
        readonly HashSet<string> _objectives = new HashSet<string>();
        readonly HashSet<string> _documents = new HashSet<string>();
        readonly HashSet<string> _discoveredRooms = new HashSet<string>();
        readonly HashSet<string> _discoveredDoors = new HashSet<string>();
        readonly HashSet<string> _eventsDone = new HashSet<string>();   // EventGuid completados (política U)
        readonly HashSet<string> _appliedEventKeys = new HashSet<string>(); // (entity, sequence) idempotencia
        long _sequence;

        public event Action<WorldEvent> EventApplied;
        public long Sequence => _sequence;
        public IEnumerable<EntityState> Entities => _entities.Values;
        public IEnumerable<string> Flags => _flags;
        public IEnumerable<string> Objectives => _objectives;
        public IEnumerable<string> Documents => _documents;
        public IEnumerable<string> DiscoveredRooms => _discoveredRooms;
        public IEnumerable<string> DiscoveredDoors => _discoveredDoors;
        public IEnumerable<string> EventsDone => _eventsDone;

        public bool TryGet(string guid, out EntityState s) => _entities.TryGetValue(guid, out s);

        public EntityState GetOrCreate(string guid, string prefabId, string regionId, EntityKind kind)
        {
            if (string.IsNullOrEmpty(guid)) throw new ArgumentException("GUID vacío");
            if (!_entities.TryGetValue(guid, out var s))
            {
                s = new EntityState { guid = guid, prefabId = prefabId, regionId = regionId, kind = kind };
                _entities[guid] = s;
            }
            return s;
        }

        // Aplica un evento lógico con secuencia propia; devuelve false si ya estaba aplicado (doble callback).
        public bool Apply(WorldEventKind kind, string entityGuid, Action<EntityState> mutate, string data = "", long? externalSequence = null)
        {
            long seq = externalSequence ?? ++_sequence;
            if (externalSequence.HasValue && seq > _sequence) _sequence = seq;
            string key = entityGuid + "#" + seq;
            if (!_appliedEventKeys.Add(key)) return false;
            if (!string.IsNullOrEmpty(entityGuid) && _entities.TryGetValue(entityGuid, out var s))
            {
                if (s.lastEventSequence >= seq && externalSequence.HasValue) return false;
                mutate?.Invoke(s); s.stateVersion++; s.lastEventSequence = seq;
            }
            var e = new WorldEvent { sequence = seq, kind = kind, entityGuid = entityGuid, data = data, time = Time.time };
            EventApplied?.Invoke(e);
            return true;
        }

        public bool SetFlag(string flag) { if (!_flags.Add(flag)) return false; Apply(WorldEventKind.FlagSet, "", null, flag); return true; }
        public bool HasFlag(string flag) => _flags.Contains(flag);
        public bool CompleteObjective(string id) => _objectives.Add(id);
        public bool HasObjective(string id) => _objectives.Contains(id);
        public bool MarkDocumentRead(string id) => _documents.Add(id);
        public bool DiscoverRoom(string id) { if (!_discoveredRooms.Add(id)) return false; Apply(WorldEventKind.RoomDiscovered, "", null, id); return true; }
        public bool DiscoverDoor(string id) => _discoveredDoors.Add(id);
        public bool MarkEventDone(string eventGuid) => _eventsDone.Add(eventGuid);
        public bool IsEventDone(string eventGuid) => _eventsDone.Contains(eventGuid);

        // Copia inmutable para el checkpoint (89.2 paso 2).
        public RegistrySnapshot Snapshot()
        {
            return new RegistrySnapshot
            {
                sequence = _sequence,
                entities = _entities.Values.Select(e => e.Clone()).ToList(),
                flags = _flags.ToList(), objectives = _objectives.ToList(), documents = _documents.ToList(),
                discoveredRooms = _discoveredRooms.ToList(), discoveredDoors = _discoveredDoors.ToList(), eventsDone = _eventsDone.ToList()
            };
        }

        // Restaurar = leer, no repetir eventos (88.6).
        public void Restore(RegistrySnapshot snap)
        {
            _entities.Clear(); _flags.Clear(); _objectives.Clear(); _documents.Clear(); _discoveredRooms.Clear(); _discoveredDoors.Clear(); _eventsDone.Clear(); _appliedEventKeys.Clear();
            _sequence = snap.sequence;
            foreach (var e in snap.entities) _entities[e.guid] = e.Clone();
            foreach (var f in snap.flags) _flags.Add(f);
            foreach (var o in snap.objectives) _objectives.Add(o);
            foreach (var d in snap.documents) _documents.Add(d);
            foreach (var r in snap.discoveredRooms) _discoveredRooms.Add(r);
            foreach (var d in snap.discoveredDoors) _discoveredDoors.Add(d);
            foreach (var ev in snap.eventsDone) _eventsDone.Add(ev);
        }
    }

    [Serializable]
    public class RegistrySnapshot
    {
        public long sequence;
        public List<EntityState> entities = new List<EntityState>();
        public List<string> flags = new List<string>();
        public List<string> objectives = new List<string>();
        public List<string> documents = new List<string>();
        public List<string> discoveredRooms = new List<string>();
        public List<string> discoveredDoors = new List<string>();
        public List<string> eventsDone = new List<string>();
    }
}
