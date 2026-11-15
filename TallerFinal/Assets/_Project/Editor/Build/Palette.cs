using UnityEngine;
using static Dream.EditorTools.Build.BuildKit;

namespace Dream.EditorTools.Build
{
    // Materiales compartidos de la version en gris, ya en la paleta del sueno (rosa, menta, crema).
    public static class Palette
    {
        public static Material Pink => ScanMat("M_Azulejo_Rosa", "long_white_tiles", new Color(1f, 0.8f, 0.85f), 1.2f, 0.5f, 0.95f);
        public static Material MintTile => ScanMat("M_Azulejo_Menta", "long_white_tiles", new Color(0.76f, 0.95f, 0.88f), 1.2f, 0.5f, 0.95f);
        public static Material Cream => Mat("M_Crema", new Color(1f, 0.96f, 0.92f), 0.3f);
        public static Material WhiteTile => ScanMat("M_Azulejo_Blanco", "long_white_tiles", new Color(0.97f, 0.98f, 1f), 1.2f, 0.55f, 0.97f);
        public static Material Wood => ScanMat("M_Madera_Clara", "white_planks_clean", new Color(1f, 0.93f, 0.86f), 1.5f);
        public static Material Hedge => Mat("M_Seto", new Color(0.27f, 0.42f, 0.3f), 0.15f);
        public static Material Leaf => Mat("M_Hoja", new Color(0.36f, 0.56f, 0.36f), 0.35f, 0f, null, 0f, false, true);
        public static Material Bark => ScanMat("M_Corteza", "bark_willow", new Color(0.95f, 0.9f, 0.88f), 2.5f);
        public static Material Cloud => Mat("M_Nube", new Color(1f, 0.98f, 0.98f), 0.05f, 0f, new Color(1f, 0.95f, 0.96f), 40f);
        public static Material Black => Unlit("M_Negro_Absoluto", Color.black);
        public static Material Carpet => ScanMat("M_Moqueta_Rosa", "velour_velvet", new Color(1f, 0.55f, 0.7f), 0.9f, 0f, 0.4f);
        public static Material Stone => ScanMat("M_Piedra_Clara", "marble_01", new Color(1f, 0.97f, 0.95f), 2f);
        public static Material BlindingLight => Mat("M_Luz_Cegadora", Color.white, 0f, 0f, new Color(1f, 0.98f, 0.94f), 60000f);
    }
}
