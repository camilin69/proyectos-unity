# Test run EsneiderProtocoloLazaro · 2026-09-17 22:55 · passed 33 · failed 2 · skipped 0

| Test | Estado | Duración | Mensaje |
|---|---|---|---|
| Esneider.Tests.ActionTransactionTests.CancelBeforeCommitDoesNothing | Passed | 0,02s |  |
| Esneider.Tests.ActionTransactionTests.CommitFiresOnceAndSurvivesCancel | Passed | 0,00s |  |
| Esneider.Tests.ActionTransactionTests.CommitOutsideDurationIsRejected | Passed | 0,00s |  |
| Esneider.Tests.ActionTransactionTests.CompleteRunsPendingCommitsExactlyOnce | Passed | 0,00s |  |
| Esneider.Tests.HealthTests.CrowbarCounts_3And6 | Passed | 0,00s |  |
| Esneider.Tests.HealthTests.HealNeverExceedsMax | Passed | 0,00s |  |
| Esneider.Tests.HealthTests.InvulnerabilityWindowBlocksSecondHit | Passed | 0,00s |  |
| Esneider.Tests.HealthTests.SameAttackIdAppliesOnce | Passed | 0,00s |  |
| Esneider.Tests.HealthTests.ThreeBoltsKillFromFull_90_60_30_0 | Passed | 0,00s |  |
| Esneider.Tests.InventoryTests.PartialPickupKeepsRemainderInWorld | Passed | 0,00s |  |
| Esneider.Tests.InventoryTests.PistolReload_5_20_Becomes_12_13 | Passed | 0,00s |  |
| Esneider.Tests.InventoryTests.ShotgunTwoCommits_2_10_Becomes_4_8 | Passed | 0,00s |  |
| Esneider.Tests.InventoryTests.WeaponPickupGivesLoadedAndReserve | Passed | 0,00s |  |
| Esneider.Tests.SaveStoreTests.CommitThenLoadRoundTrip | Passed | 0,03s |  |
| Esneider.Tests.SaveStoreTests.FutureSchemaVersionIsPreservedNotOpened | Passed | 0,02s |  |
| Esneider.Tests.SaveStoreTests.OrphanTempIsNotACheckpoint | Passed | 0,01s |  |
| Esneider.Tests.SaveStoreTests.RegistryEventsAreIdempotent | Passed | 0,01s |  |
| Esneider.Tests.SaveStoreTests.SemanticRejections | Passed | 0,00s |  |
| Esneider.Tests.SaveStoreTests.TruncatedActiveFallsBackToBackup | Passed | 0,03s |  |
| Esneider.Tests.SaveStoreTests.TwoCheckpointsRotateGenerations | Passed | 0,02s |  |
| Esneider.Tests.SaveStoreTests.WrongChecksumIsRejected | Passed | 0,01s |  |
| Esneider.Tests.EnemyAiPlayTests.Vigia_LosesSightBehindPillar_SearchesLastKnownPosition | Passed | 2,97s |  |
| Esneider.Tests.EnemyAiPlayTests.Vigia_SeesPlayer_ConfirmsAfterSuspicion_ThenTelegraphsAndEmitsNet | Passed | 5,88s |  |
| Esneider.Tests.PersistencePlayTests.CP06_GuaranteeAppliesOnceAndNeverReduces | Passed | 0,11s |  |
| Esneider.Tests.PersistencePlayTests.NoCheckpointWhileCapturedOrBusy | Passed | 0,89s |  |
| Esneider.Tests.PersistencePlayTests.QA09_SnapshotRestoresInventoryEnemiesPickupsAndCrate | Failed | 0,71s | Expected: True   But was:  False |
| Esneider.Tests.PersistencePlayTests.QA10_LoadFromDiskAfterRestart_NoDuplication | Failed | 0,07s | el pickup recogido no reaparece: sin duplicación   Expected: False   But was:  True |
| Esneider.Tests.PersistencePlayTests.QA11_InvalidActiveSaveRecoversBackup | Passed | 0,08s |  |
| Esneider.Tests.SandboxPlayTests.Pistol_ShotThroughCoverIsBlocked_ShotgunFalloffApplies | Passed | 2,52s |  |
| Esneider.Tests.SandboxPlayTests.QA01_CrowbarKillsVigiaIn3AndCustodioIn6 | Passed | 9,23s |  |
| Esneider.Tests.SandboxPlayTests.QA02_ThreeBolts_90_60_30_0 | Passed | 3,07s |  |
| Esneider.Tests.SandboxPlayTests.QA03_NetBehindPillarIsBlocked | Passed | 1,27s |  |
| Esneider.Tests.SandboxPlayTests.QA04_NetCaptureEndsWithin2_5Seconds | Passed | 3,31s |  |
| Esneider.Tests.SandboxPlayTests.QA06_ReloadCancelBeforeAndAfterCommit | Passed | 3,19s |  |
| Esneider.Tests.SandboxPlayTests.QA08_HealAtFullDoesNotConsume_AndCancelBeforeCommitKeepsUnit | Passed | 2,27s |  |

DONE FAIL
