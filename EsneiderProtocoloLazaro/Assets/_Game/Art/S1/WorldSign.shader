Shader "Esneider/WorldSign"
{
    Properties { _MainTex ("Font atlas", 2D) = "white" {} }
    SubShader
    {
        Tags { "RenderPipeline"="UniversalPipeline" "Queue"="Transparent" "RenderType"="Transparent" }
        Pass
        {
            Tags { "LightMode"="SRPDefaultUnlit" }
            Blend SrcAlpha OneMinusSrcAlpha
            ZWrite Off
            ZTest LEqual
            Cull Back
            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            TEXTURE2D(_MainTex); SAMPLER(sampler_MainTex);
            struct Attributes { float4 positionOS:POSITION; float2 uv:TEXCOORD0; float4 color:COLOR; };
            struct Varyings { float4 positionCS:SV_POSITION; float2 uv:TEXCOORD0; float4 color:COLOR; };
            Varyings vert(Attributes i) { Varyings o; o.positionCS=TransformObjectToHClip(i.positionOS.xyz);o.uv=i.uv;o.color=i.color;return o; }
            half4 frag(Varyings i):SV_Target { half4 c=i.color;c.a*=SAMPLE_TEXTURE2D(_MainTex,sampler_MainTex,i.uv).a;return c; }
            ENDHLSL
        }
    }
}
