# DATA_BASELINE — export de definiciones ejecutables (95.3)

contentVersion `0.1.0` · plano `GDD-68-r1` · validación datos: **PASA** · validación plano: **PASA**

| Campo | Valor ejecutable | Fuente GDD |
|---|---|---|
| Player HP / invulnerabilidad | 90 / 0.65s | 10/103.1 (velocidades: VAL sección 9) |
| FOV | 75° (70–100) | 9/81 |
| Curación | jeringa +45 1.6s/commit 1.1s; ración +20 2s/commit 1.4s; máx 3/2 | 10/86 |
| Weapon_Crowbar | daño 20×1; cargador 0+0; pickup 0+0; ciclo 0.85s; recarga 0/0s; ruido 12 m | 11/60/103.1 |
| Weapon_Pistol | daño 30×1; cargador 12+80; pickup 10+10; ciclo 0.35s; recarga 1.9/1.35s; ruido 28 m | 11/68/80/86/103.1 |
| Weapon_Shotgun | daño 7.5×8; cargador 6+36; pickup 5+5; ciclo 1.1s; recarga 0/0s; ruido 36 m | 11/68/80/86/103.1 |
| Enemy_Vigia | HP 60; vel 0.7/2.6; rango 3–9; aviso 1.1s; rec 1.4s; cd 3.5s; daño 0; visión 12m90°/16m100° | 12/14/77/78/103.1 |
| Enemy_Custodio | HP 120; vel 0.6/2.2; rango 4–14; aviso 1s; rec 1.6s; cd 3s; daño 30; visión 12m90°/16m100° | 13/14/77/78/103.1 |
| Boss | HP 1200; fases 800/400; ataques BOSS-RAYO 30 (1.2/2s), BOSS-BARRIDO 30 (1.4/2.2s), BOSS-CARGA 45 (1.5/2.4s), BOSS-PULSO 30 (1.8/2.4s) | 15/61/79/103.1 |
| Superficies | SUR-CON 0.65/0.55 ×1, SUR-MET 0.5/0.4 ×1, SUR-GRT 0.6/0.5 ×1.25, SUR-WET 0.55/0.45 ×1, SUR-CER 0.6/0.5 ×1, SUR-GLS 0.45/0.35 ×1, SUR-FAB 0.7/0.6 ×0.75, SUR-RUB 0.8/0.7 ×0.65, SUR-BOT 0.5/0.4 ×1 | 96 |
| Regiones | 25 (22 salas + 3 conectores) | 68/88 |
| Checkpoints | CP-00, CP-01, CP-02, CP-02B, CP-03, CP-04, CP-04B, CP-05, CP-06, CP-07 | 68.9 |
| Eventos | 26 | 93 |
| Población plano | 23V/14K/1B; balas 140; cartuchos 50 | 68.7/68.8 |

## Informe de validación
```
DataValidator: PASA · 0 errores · 0 avisos

DataValidator: PASA · 0 errores · 0 avisos

```

## GUIDs estables (MD5 de `ESNEIDER:<ID>`)

| ID | GUID |
|---|---|
| S1-R01 | bba5954b-c430-c035-7b15-59b05a624772 |
| S1-R02 | 79869ec8-c9b9-8fc3-6107-60ffcd5e55a2 |
| S1-R05 | fdb4d6d2-c466-ec6e-fb29-df6ca4c9ec6c |
| S1-R03 | 5ee4bbd4-f7de-b071-2016-86b2da7f0a6b |
| S1-R04 | 4872da67-12de-6067-a3f6-3774d4720500 |
| S2-R01 | 522ff4a9-9a51-c8e2-9e9b-f3863daa7470 |
| S2-R06 | 5e387f3b-756b-5859-a444-30fa2554e1e2 |
| S2-R03 | b01d5b60-3cf2-8477-e65c-301534ae7d1c |
| S2-R02 | f210656e-2584-3c07-6f1a-82b568cdae5d |
| S2-R04 | 2253ca17-09a8-fa3c-c83d-ac01b63c1056 |
| S2-R05 | 76877cea-0025-c838-9d5f-8773514cb6f6 |
| S3-R02A | bdeb42b8-f0d6-2929-c050-71f127ab0fef |
| S3-R02B | 53239959-da10-c4ba-c2d1-9032c65785ec |
| S3-R05 | 9ca46e84-eda5-f29d-a269-3f1d69f74d19 |
| S3-R01 | 54083740-d69c-1e76-2384-470b2c71fa23 |
| S3-R03 | 492fe050-cfdf-5e32-7f07-f6d7fff1deab |
| S3-R04 | 7cd975fd-3250-10bd-e0fa-72b4fc7d9661 |
| S4-R05 | ac17b515-99f8-e559-f3e2-c2b7faaad299 |
| S4-R03 | e2d214a0-4bee-a63d-c6ce-71cc8eca4789 |
| S4-R04 | dbf86ac9-4ab3-70cd-8088-1713442a855e |
| S4-R02 | 64cb4905-ee01-9a3d-eedb-d27a817a86b2 |
| S4-R01 | d1b85911-8927-7e1f-bf05-5a6efc90d8ea |
| C-01 | 9cd6a38d-377f-e109-df18-8c22217c5db9 |
| C-02 | 29cc5d6c-6ed4-a325-4575-fe7c247535e9 |
| C-03 | 0eab6c15-fe73-ea79-1a07-a0824636f5a1 |
| CP-00 | 1d869903-a537-090e-1041-06151c6706c5 |
| CP-01 | bc518dfd-553d-5c43-6008-29e1dc76ade9 |
| CP-02 | bdaafd9e-43f0-f4ff-b8a3-18bb929ee06b |
| CP-02B | ad075eb3-58f3-8f25-a182-7423f5b8d820 |
| CP-03 | a0f35adf-6a34-d17d-ce42-46a4b0cc325f |
| CP-04 | e6953a5c-b0a7-79bd-ff46-f2ed79e7eea6 |
| CP-04B | 23c407d0-098e-d83f-9fd9-47d591a64574 |
| CP-05 | 12b0bebf-db02-1c77-8b49-8a695d8ef414 |
| CP-06 | b65d70f4-f053-5573-86c2-b2328bf5267d |
| CP-07 | 2680175f-5290-9933-c588-d77086f97af8 |
