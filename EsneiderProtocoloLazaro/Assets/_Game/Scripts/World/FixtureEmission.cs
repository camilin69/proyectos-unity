using UnityEngine;

namespace Esneider.World
{
    // The baked mask limits glow to the diffuser; no extra lights, flicker or audio.
    public class FixtureEmission : MonoBehaviour
    {
        public Light source;
        public Renderer surface;
        public Color previewColor=Color.white;
        public float strength=1.3f;
        MaterialPropertyBlock block;
        void OnEnable(){Refresh();}
        void LateUpdate(){Refresh();}
        public void Refresh()
        {
            if(!surface)return;
            Color color=previewColor;
            if(source)color=source.enabled&&source.gameObject.activeInHierarchy ? source.color*Mathf.Clamp(source.intensity,0,2) : Color.black;
            if(block==null)block=new MaterialPropertyBlock();
            surface.GetPropertyBlock(block);block.SetColor("_EmissionColor",color*strength);surface.SetPropertyBlock(block);
        }
    }
}
