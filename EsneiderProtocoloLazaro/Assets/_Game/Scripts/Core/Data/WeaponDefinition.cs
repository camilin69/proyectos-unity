using System.Collections.Generic;
using UnityEngine;

namespace Esneider.Core.Data
{
    public enum WeaponKind { Melee, Pistol, Shotgun }

    [CreateAssetMenu(menuName = "Esneider/Data/Weapon", fileName = "WeaponDefinition")]
    public class WeaponDefinition : GameDefinition
    {
        public WeaponKind kind;
        [Header("Daño (11/103)")] public float damage = 20f;
        [Tooltip("Pellets por disparo; 1 salvo escopeta")] public int pellets = 1;
        public float range = 1.6f;
        [Header("Capacidad")] public int magazineSize = 0;
        public int reserveMax = 0;
        public int pickupLoaded = 0, pickupReserve = 0;
        [Header("Tiempos y commit (60/86)")] public float attackCycle = 0.85f;
        public float activeStart = 0.20f, activeEnd = 0.35f;
        public float reloadDuration = 0f, reloadCommit = 0f;
        [Tooltip("Escopeta: entrada, inserción por cartucho, commit de inserción, salida, bombeo")]
        public float shellEnter = 0f, shellInsert = 0f, shellInsertCommit = 0f, shellExit = 0f, pumpDuration = 0f;
        [Header("Ruido lógico (14/78)")] public float noiseRadius = 12f;
        [Header("Presentación")] public string viewmodelSocket = "hand_R";
        public List<string> clipIds = new List<string>();
    }
}
