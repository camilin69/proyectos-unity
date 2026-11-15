using System;
using UnityEngine;

namespace Dream
{
    // Modelo de PlayerAnimatorSpec.json: la UNICA fuente del Animator del sonador. AnimatorBuilder construye el
    // .controller desde aqui, tools/taller_final/animator_diagram.py dibuja el diagrama desde aqui, y
    // AnimatorMatchesSpecTests exige que el .controller real coincida. Asi el diagrama y la implementacion no
    // pueden separarse, que es lo que pide el taller.
    [Serializable] public class AnimatorSpec
    {
        public string name;
        public string defaultState;
        public ParamSpec[] parameters;
        public StateSpec[] states;
        public TransitionSpec[] transitions;

        public static AnimatorSpec FromJson(string json) => JsonUtility.FromJson<AnimatorSpec>(json);
    }

    [Serializable] public class ParamSpec { public string name; public string type; public string @default; }
    [Serializable] public class StateSpec { public string name; public string clip; public bool loop; public float speed = 1f; public int[] layout; }
    [Serializable] public class ConditionSpec { public string param; public string mode; public float threshold; }
    [Serializable] public class TransitionSpec
    {
        public string from, to;
        public ConditionSpec[] conditions;
        public bool hasExitTime;
        public float exitTime;
        public float duration;
    }
}
