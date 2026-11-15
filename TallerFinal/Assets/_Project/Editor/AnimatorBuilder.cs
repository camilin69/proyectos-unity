using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Animations;
using UnityEngine;

namespace Dream.EditorTools
{
    // Construye Sonador.controller desde PlayerAnimatorSpec.json. El controller no se edita a mano: si hay que
    // cambiar el Animator se cambia la spec y se reconstruye, y el diagrama se regenera de la misma fuente.
    public static class AnimatorBuilder
    {
        public const string ControllerPath = "Assets/_Project/Animation/Controllers/Sonador.controller";

        [MenuItem("Sueno Lucido/Construir Animator desde la spec")]
        public static string Build()
        {
            var spec = AnimatorSpec.FromJson(File.ReadAllText(SonadorImportPostprocessor.SpecPath));
            var clips = AssetDatabase.LoadAllAssetsAtPath(SonadorImportPostprocessor.ModelPath)
                .OfType<AnimationClip>().Where(c => !c.name.StartsWith("__")).ToDictionary(c => c.name);

            if (AssetDatabase.LoadAssetAtPath<AnimatorController>(ControllerPath) != null)
                AssetDatabase.DeleteAsset(ControllerPath);
            var ctrl = AnimatorController.CreateAnimatorControllerAtPath(ControllerPath);

            foreach (var p in spec.parameters)
            {
                var type = (AnimatorControllerParameterType)Enum.Parse(typeof(AnimatorControllerParameterType), p.type);
                ctrl.AddParameter(p.name, type);
                var ps = ctrl.parameters;
                var last = ps[ps.Length - 1];
                if (type == AnimatorControllerParameterType.Float) last.defaultFloat = float.Parse(p.@default, System.Globalization.CultureInfo.InvariantCulture);
                if (type == AnimatorControllerParameterType.Bool) last.defaultBool = p.@default == "true";
                ctrl.parameters = ps;
            }

            var sm = ctrl.layers[0].stateMachine;
            var states = new Dictionary<string, AnimatorState>();
            foreach (var s in spec.states)
            {
                // misma disposicion que el diagrama: la ventana del Animator y el PNG se ven iguales
                var pos = new Vector3(260 * s.layout[0], 110 * s.layout[1], 0);
                var st = sm.AddState(s.name, pos);
                if (!clips.TryGetValue(s.clip, out var clip))
                    throw new Exception($"El FBX no tiene el clip '{s.clip}' que pide el estado '{s.name}'.");
                st.motion = clip;
                st.speed = s.speed;
                st.writeDefaultValues = true;
                states[s.name] = st;
            }
            sm.defaultState = states[spec.defaultState];

            foreach (var t in spec.transitions)
            {
                var tr = states[t.from].AddTransition(states[t.to]);
                tr.hasExitTime = t.hasExitTime;
                tr.exitTime = t.hasExitTime ? t.exitTime : 0f;
                tr.duration = t.duration;
                tr.hasFixedDuration = true;
                tr.interruptionSource = TransitionInterruptionSource.None;
                foreach (var c in t.conditions ?? new ConditionSpec[0])
                {
                    var mode = (AnimatorConditionMode)Enum.Parse(typeof(AnimatorConditionMode), c.mode);
                    tr.AddCondition(mode, c.threshold, c.param);
                }
            }
            // IK Pass en la capa base: HeadLook gira la cabeza hacia la puerta de luz y el hueco del arbol
            var layers = ctrl.layers;
            layers[0].iKPass = true;
            ctrl.layers = layers;
            EditorUtility.SetDirty(ctrl);
            AssetDatabase.SaveAssets();
            return $"{ControllerPath}: {spec.parameters.Length} parametros, {spec.states.Length} estados, {spec.transitions.Length} transiciones";
        }
    }

    // Vuelca un .controller real a la forma de la spec. AnimatorMatchesSpecTests compara este volcado con la spec;
    // tambien sirve para dibujar el diagrama "tal como se construyo".
    public static class AnimatorExporter
    {
        public static AnimatorSpec Export(AnimatorController ctrl)
        {
            var sm = ctrl.layers[0].stateMachine;
            var spec = new AnimatorSpec
            {
                name = ctrl.name,
                defaultState = sm.defaultState ? sm.defaultState.name : null,
                parameters = ctrl.parameters.Select(p => new ParamSpec
                {
                    name = p.name,
                    type = p.type.ToString(),
                    @default = p.type == AnimatorControllerParameterType.Float ? p.defaultFloat.ToString("0.###", System.Globalization.CultureInfo.InvariantCulture)
                             : p.type == AnimatorControllerParameterType.Bool ? (p.defaultBool ? "true" : "false") : ""
                }).ToArray(),
                states = sm.states.Select(cs => new StateSpec
                {
                    name = cs.state.name,
                    clip = cs.state.motion ? cs.state.motion.name : null,
                    loop = cs.state.motion is AnimationClip ac && ac.isLooping,
                    speed = cs.state.speed,
                    layout = new[] { Mathf.RoundToInt(cs.position.x / 260f), Mathf.RoundToInt(cs.position.y / 110f) }
                }).ToArray(),
            };
            var trs = new List<TransitionSpec>();
            foreach (var cs in sm.states)
                foreach (var t in cs.state.transitions)
                    trs.Add(new TransitionSpec
                    {
                        from = cs.state.name, to = t.destinationState.name,
                        hasExitTime = t.hasExitTime, exitTime = t.hasExitTime ? t.exitTime : 0f, duration = t.duration,
                        conditions = t.conditions.Select(c => new ConditionSpec { param = c.parameter, mode = c.mode.ToString(), threshold = c.threshold }).ToArray()
                    });
            spec.transitions = trs.ToArray();
            return spec;
        }
    }
}
