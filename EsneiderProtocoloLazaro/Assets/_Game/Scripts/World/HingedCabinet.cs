using Esneider.Core;
using UnityEngine;

namespace Esneider.World
{
    // Independent leaves retain their real hinge pivots; supplies/pickups are separate entities.
    public class HingedCabinet : MonoBehaviour, IInteractable
    {
        public Transform[] leaves;
        public float[] openAngles = {108,-108};
        public float openSeconds = 1.1f;
        public bool isOpen;
        Quaternion[] _closed;
        BoxCollider[] _boxes;
        float _progress, _target;
        bool _moving, _blocked;
        public bool IsMoving => _moving;
        public string Prompt => _blocked ? "Despeja la puerta" : isOpen ? "Cerrar armario" : "Abrir armario";
        public bool CanInteract(GameObject who) => !_moving && leaves != null && leaves.Length>0;

        void Awake() { Init(); }
        void Init()
        {
            if(_closed!=null)return;
            if(leaves==null || leaves.Length==0)return;
            _closed=new Quaternion[leaves.Length];_boxes=new BoxCollider[leaves.Length];
            for(int i=0;i<leaves.Length;i++){_closed[i]=leaves[i].localRotation;_boxes[i]=leaves[i].GetComponent<BoxCollider>();}
            _progress=_target=isOpen ? 1 : 0;Pose(_progress);
        }
        void Pose(float value)
        {
            float eased=Mathf.SmoothStep(0,1,value);
            for(int i=0;i<leaves.Length;i++)leaves[i].localRotation=Quaternion.Euler(0,openAngles[i]*eased,0)*_closed[i];
        }
        public void Interact(GameObject who)
        {
            Init();if(!CanInteract(who) || _closed==null)return;
            var persistent=GetComponent<PersistentEntity>();
            if(persistent && (!string.IsNullOrEmpty(persistent.guid) || !string.IsNullOrEmpty(persistent.stableId)))persistent.EnsureRegistered();
            _target=isOpen ? 0 : 1;_moving=true;_blocked=false;
            NoiseSystem.Emit(transform.position,4f,gameObject,"cabinet");
        }
        public void SnapOpen(bool open)
        {
            Init();if(_closed==null)return;
            isOpen=open;_progress=_target=open ? 1 : 0;_moving=false;_blocked=false;Pose(_progress);
        }
        void Update() { Advance(Time.deltaTime); }
        public void Advance(float seconds)
        {
            if(!_moving || seconds<=0)return;
            float remaining=seconds/Mathf.Max(.1f,openSeconds);
            int mask=GameLayers.Mask(GameLayers.Player,GameLayers.Enemy,GameLayers.DynamicProp,GameLayers.WorldStatic);
            while(remaining>0 && _moving)
            {
                float step=Mathf.Min(.02f,remaining);remaining-=step;
                float next=Mathf.MoveTowards(_progress,_target,step);Pose(next);Physics.SyncTransforms();
                bool blocked=false;
                foreach(var box in _boxes)
                {
                    if(!box)continue;
                    foreach(var other in Physics.OverlapBox(box.bounds.center,box.bounds.extents,Quaternion.identity,mask,QueryTriggerInteraction.Ignore))
                    {
                        if(other.transform.IsChildOf(transform))continue;
                        Vector3 direction;float depth;
                        if(Physics.ComputePenetration(box,box.transform.position,box.transform.rotation,other,other.transform.position,other.transform.rotation,out direction,out depth) && depth>.002f){blocked=true;break;}
                    }
                    if(blocked)break;
                }
                if(blocked){Pose(_progress);Physics.SyncTransforms();_moving=false;_blocked=true;return;}
                _progress=next;
                if(Mathf.Approximately(_progress,_target))
                {
                    isOpen=_target>0;_moving=false;
                    var persistent=GetComponent<PersistentEntity>();
                    if(persistent && (!string.IsNullOrEmpty(persistent.guid) || !string.IsNullOrEmpty(persistent.stableId)))
                    {persistent.EnsureRegistered();persistent.NotifyDoor(isOpen,true);}
                }
            }
        }
    }
}
