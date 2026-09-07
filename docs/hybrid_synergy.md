# Why S4 Hybrid performs much better than the individual measures

> Evidence basis: retained EPA SWMM 5.2.4 `.rpt` files from the verified **heavy** synthetic demo on 2026-09-07. This is a synthetic-model interpretation, not a general engineering claim.

## Structural audit first

Before interpreting the result, the S4 input was checked for scenario leakage.

The independent audit confirms:

```text
S4 = S1 ∪ S2 ∪ S3
extra mutations = 0
missing mutations = 0
rainfall identical across S0–S4 = yes
semantic INP changes outside the manifest = 0
```

The exact retained evidence is in [`docs/evidence/hybrid_audit_snapshot.json`](evidence/hybrid_audit_snapshot.json). The same audit is reproducible after a batch run with:

```bash
python scripts/run_demo_batch.py --rainfall heavy
python scripts/audit_hybrid_synergy.py
```

The second command fails if the S4 manifest contains an extra/missing mutation, if scenario rainfall differs, or if an INP token changes outside the declared manifest.

## What the reports show

| Scenario | C05 max flow (m³/s) | P01 max flow (m³/s) | O01 discharged volume (m³) | ST01 max volume (m³) | J05 flood volume (m³) | Total flood volume (m³) |
|---|---:|---:|---:|---:|---:|---:|
| S0 Baseline | 0.040 | 0.000 | 1 | 117 | 1,065 | 3,338.20 |
| S1 PumpAssist | 0.028 | 0.028 | 197 | 0 | 1,047 | 3,320.33 |
| S2 PipeUpsize | 0.283 | 0.000 | 1 | 118 | 1,060 | 3,321.33 |
| S3 StorageExpand | 0.040 | 0.000 | 1 | 174 | 1,033 | 3,306.33 |
| S4 Hybrid | 0.323 | 0.180 | 786 | 148 | 466 | 2,730.55 |

The values above are read from the SWMM report sections `Link Flow Summary`, `Pumping Summary`, `Outfall Loading Summary`, `Storage Volume Summary`, and `Node Flooding Summary`.

![C05 and P01 maximum flows by scenario](../assets/hybrid_bottleneck_flows.png)

![J05 flood volume and O01 discharged volume](../assets/hybrid_j05_outfall_volume.png)

## Engineering interpretation

The synthetic drainage path behaves like a **serial bottleneck chain**:

```text
upstream junctions -> C05 -> ST01 -> P01 -> O01
                         conveyance   storage   discharge
```

### S1: PumpAssist alone is starved by C05

S1 changes P01 to the higher-capacity pump curve, but the upstream C05 remains the 0.20 m bottleneck. The report shows C05 and P01 both peak at only about **0.028 m³/s**, far below the Hybrid pump peak of **0.180 m³/s**. In other words, the pump has capacity available but cannot be fed fast enough through the narrow conduit.

Result: only **17.87 m³** total flood reduction relative to S0.

### S2: PipeUpsize improves conveyance, but water still cannot leave the system

S2 increases C05 peak flow from **0.040 to 0.283 m³/s**, proving the conduit mutation is hydraulically active. However, P01 remains effectively off and O01 receives only about **1 m³** over the event. More water can reach ST01, but the downstream discharge bottleneck remains.

Result: only **16.87 m³** total flood reduction. The report also shows J05 flooding duration increasing from **2.12 h to 2.70 h**. This is a useful reminder that a small improvement in total flood volume does not imply that every local risk metric improves.

### S3: StorageExpand adds room, but the narrow C05 limits access to it

S3 increases ST01 maximum stored volume from **117 to 174 m³**, so the storage mutation is active. Yet C05 remains near **0.040 m³/s**, and the outlet pump remains effectively off. The added storage therefore cannot be used quickly enough to materially relieve the upstream network during the peak period.

Result: **31.87 m³** total flood reduction. ST01 reaches its reported maximum at **03:00**, the end of the simulation, which is consistent with storage retaining water rather than actively evacuating it through the nearly-off outlet.

### S4: all three serial constraints are relieved together

S4 combines the wider C05, expanded storage curve and active P01. The reports show the complete chain becoming usable at the same time:

- C05 max flow: **0.323 m³/s**
- P01 max flow: **0.180 m³/s**
- O01 total discharged volume: **786 m³**
- J05 flood volume: **1,065 -> 466 m³**

The large system-level benefit is therefore not caused by an undeclared S4 mutation. It is consistent with the hydraulic interaction of **conveyance + buffering + discharge**.

## Quantifying the observed interaction

Relative to S0:

- S1 reduction: **17.87 m³**
- S2 reduction: **16.87 m³**
- S3 reduction: **31.87 m³**
- sum of individual reductions: **66.62 m³**
- S4 reduction: **607.65 m³**
- difference between S4 reduction and that simple sum: **541.03 m³**

This is an **observed nonlinear interaction in this synthetic model**, not a formal or transferable “synergy coefficient.” SWMM's dynamic-wave routing, surcharge/flooding behavior, storage and pumping make the response non-additive.

A particularly useful diagnostic is J05: its flood-volume reduction is **599 m³**, which accounts for about **98.6%** of the S0-to-S4 reduction in total flood volume. That localizes the main benefit to the bottleneck immediately upstream of C05/ST01 rather than suggesting a mysterious system-wide numerical artifact.

## Interview-ready explanation

A concise explanation that is supported by the model is:

> 单独增加泵、扩管或调蓄空间时，排水链条上仍有其他瓶颈，所以改善有限。扩大 C05 后输水能力上去了，但没有泵就排不出去；只有泵时又受 C05 限流；只有调蓄时也受 C05 和外排能力限制。S4 同时改善输水、调蓄和外排，P01 才真正达到 0.18 m³/s，J05 的溢流量由约 1065 m³ 降到 466 m³，因此出现明显的非线性组合效果。

Do not generalize this to “combined measures are always better.” It is a result of the current synthetic topology and parameter set.
