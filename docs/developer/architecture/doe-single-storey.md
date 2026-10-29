# DOE single-storey generators

> **Status:** Accepted (stage P2 of the [DOE geometry design note](../plans/2026-10-25-doe-geometry-generators.md); the owner, with PR #1, D-176) · **Code:** `src/Lod.Generators/Doe/Restaurant/`, `StoreRow/`, `RetailBox/`, `Supermarket/`, `Warehouse/`, and their shared `SingleStorey/`; `src/Lod.Grasshopper/Components/DoeRestaurantComponents.cs`, `DoeStoreRowComponents.cs`, `DoeRetailBoxComponents.cs`, `DoeSupermarketComponents.cs`, `DoeWarehouseComponents.cs` · **Tests:** `tests/Lod.Generators.Tests/Doe/` folders of the same names · **Smoke spec:** `scripts/rhino-smoke/specs/doe-single-storey.py` · **Builds on:** [DOE layout records and the grid plan layout](doe-layouts.md), [DOE generator components](doe-components.md), [ADR-025](../decisions/ADR-025-doe-reference-geometry-generators.md)

Stage P2 adds the five generators of the single-storey DOE reference types, six layout records in all. Each is a `PlanGenerator` (ADR-006) on
the grid of its record: its typed parameter record has a static `Default` read from the record, which reproduces the source plan, and its
layout is the record's storey on cuts that the S3 rule moves (`GridAxis`) or, for the strip mall, a row of stores built from runs. The presets
come as one `DoeProgramMap` keyed by program key (S4); a key of the plan without a preset is `MissingPreset`. Each generator lists the keys its
map needs (`ProgramKeys`, in ordinal order). The Grasshopper components are on the shared DOE component support of stage P1 ([below](#grasshopper-components)).

## Generators

| Generator | Record | Zones (program key) | Parameters | Gap |
| --- | --- | --- | --- | --- |
| `RestaurantGenerator` | `full-service-restaurant`, `quick-service-restaurant` (`Type`) | `Dining` along the south, `Kitchen` behind | `Length`, `DiningDepth`, `KitchenDepth` | G2 |
| `StoreRowGenerator` | `strip-mall` | `LGstore<n>`, `SMstore<n>` (`Strip mall - type 1`, `2`, `3`) | `Depth`, `LargeStoreWidth`, `SmallStoreWidth`, `Stores` (runs) | none |
| `RetailBoxGenerator` | `stand-alone-retail` | `Point_Of_Sale`, `Front_Entry` (`Entry`), `Front_Retail` (`Retail`) along the south; `Core_Retail` (`Retail`); `Back_Space` along the north | `Length`, `Depth`, `BackSpaceDepth`, `FrontDepth`, `EntryWidth` | none |
| `SupermarketGenerator` | `supermarket` | `Produce`, `Sales`; `Bakery`, `Deli` along the east; `DryStorage`, `Office` along the north | `Length`, `Depth`, `StorageDepth`, `PreparationDepth` | none |
| `WarehouseGenerator` | `warehouse` | `Office` (south-west corner), `FineStorage` (`Fine`), `BulkStorage` (`Bulk`) | `Length`, `Depth`, `OfficeDepth`, `FineStorageDepth` | G4 |

Every parameter record also has `FloorHeight` (the record's storey height by default) and `OrientationDegrees` (0), and every plan is one
storey on the ground. Zone IDs, names, and program keys are the record's; the space type of a zone is `DoeSpaceTypes.Of(key)`.

## Size and unit variation (S3)

S3 as amended in P1 (D-164). A band a size parameter sets keeps its length; it must be finite and at least `GridAxis.MinimumFixedBand`, 0.5 m,
per band, not per grid interval. The other intervals are flexible: they share a change of the plate length or depth in proportion to their slack
(length less 1 m, `GridAxis.Resize` through `SingleStoreyRecord.Cuts`), so they all reach 1 m (`GridAxis.MinimumFlexibleInterval`) at the
shortest valid plate. A value below a limit, or one that is not finite, is `InvalidParameter`, with a message that names the parameter: a band
below 0.5 m (`… must be finite and at least 0.5 m`), a band changed past its maximum, the plate less the other bands and the flexible intervals at
1 m (`… exceeds its maximum … m`), or a plate too short for its bands (`… is shorter than the shortest valid … m`).

| Generator | Along x | Along y |
| --- | --- | --- |
| Restaurant | the plate, `Length`, a band | dining room `DiningDepth` and kitchen `KitchenDepth`, bands; the plate depth is their sum |
| Strip mall | each store `LargeStoreWidth` or `SmallStoreWidth`, bands; the plate length is their sum | the plate, `Depth`, a band |
| Stand-alone retail | point of sale and front retail flexible, either side of the entry `EntryWidth` (a band); their slack is equal, so the entry stays centred | front band `FrontDepth`, one band whose entry takes its source half, core retail flexible, back space `BackSpaceDepth`, a band |
| Supermarket | produce and sales flexible, preparation band `PreparationDepth` (bakery, deli, office) | bakery and deli flexible, storage band `StorageDepth` (dry storage, office) |
| Warehouse | office and the fine storage beside it, both flexible | office `OfficeDepth`, a band; the fine storage north of it up to `FineStorageDepth`, a band of at least 0.5 m; bulk storage flexible |

**Limits and valid ranges** at the other parameters' defaults (m; the factor of the default in brackets). These are validity limits under S3, not
plausibility: a plan inside them lays out, keeps its zones and adjacencies, and validates, but may be no building anyone would design. The warehouse,
for example, is valid down to a 2 m length with a 1 m office, and a strip mall store down to 0.5 m wide. `FloorHeight` is any positive value;
plates have no upper limit. Every size parameter of every record reaches at least ±20 % of its default, and its 0.5× and 2× are valid.

| Record | Parameter | Valid range |
| --- | --- | --- |
| full-service restaurant | `Length` 22.6087, `DiningDepth` 16.4427, `KitchenDepth` 6.166 | each ≥ 0.5 (0.02, 0.03, 0.08); no upper limit |
| quick-service restaurant | `Length` 15.2428, `DiningDepth` 7.6214, `KitchenDepth` 7.6214 | each ≥ 0.5 (0.03, 0.07, 0.07); no upper limit |
| strip mall | `Depth` 22.86, `LargeStoreWidth` 15.24, `SmallStoreWidth` 7.62 | each ≥ 0.5 (0.02, 0.03, 0.07); no upper limit; each run's count ≥ 1 |
| stand-alone retail | `Length` 54.27 | ≥ `EntryWidth` + 2 = 6 (0.11) |
| | `Depth` 42.27 | ≥ `FrontDepth` + `BackSpaceDepth` + 1 = 14 (0.33) |
| | `BackSpaceDepth` 7 | 0.5 (0.07) to `Depth` − `FrontDepth` − 1 = 35.27 (5.04) |
| | `FrontDepth` 6 | 0.5 (0.08) to `Depth` − `BackSpaceDepth` − 1 = 34.27 (5.71) |
| | `EntryWidth` 4 | 0.5 (0.13) to `Length` − 2 = 52.27 (13.07) |
| supermarket | `Length` 79.1901 | ≥ `PreparationDepth` + 2 = 11.8988 (0.15) |
| | `Depth` 52.7944 | ≥ `StorageDepth` + 2 = 10.975 (0.21) |
| | `StorageDepth` 8.975 | 0.5 (0.06) to `Depth` − 2 = 50.7944 (5.66) |
| | `PreparationDepth` 9.8988 | 0.5 (0.05) to `Length` − 2 = 77.1901 (7.80) |
| warehouse | `Length` 45.7178 | ≥ 2 (0.04) |
| | `Depth` 100.579 | ≥ `FineStorageDepth` + 1 = 31.4785 (0.31) |
| | `OfficeDepth` 9.1435 | 0.5 (0.05) to `FineStorageDepth` − 0.5 = 29.9785 (3.28) |
| | `FineStorageDepth` 30.4785 | `OfficeDepth` + 0.5 = 9.6435 (0.32) to `Depth` − 1 = 99.579 (3.27) |

T5 tests every size parameter at 0.5×, 1×, and 2× of its default, each limit (the plan keeps its zones and adjacencies) and a value just beyond
it (`InvalidParameter`), and every band at 0.5 m and just below.

Two choices follow from T5, which asks every size parameter at 0.5×, 1×, and 2× of its default to give a valid plan (both accepted by the
controller):

- The restaurant's depth parameter is the dining room's depth, not the plate's. With the plate depth fixed, twice the quick-service kitchen
  (15.24 m) would fill the whole 15.24 m plate. No rule asks the kitchen to be smaller than the dining room: the quick-service source has both
  7.62 m deep.
- The warehouse's office size is its depth; along x the office and the fine storage beside it share a length change by their slack (24.91 and
  18.81 m). An office of a fixed width (25.91 m) would not fit the half-length plate (22.86 m), nor twice that width the default plate.

**Repeated units (strip mall).** `Stores` lists runs of stores west to east, each `StoreRun(Size, Tenancy, Count)` with `Count` at least 1; the
order of the runs is the order of the stores, and each store takes the program key of its tenancy (`StoreRowGenerator.ProgramKey`). Large stores
are `LGstore1`, `LGstore2`, … and small ones `SMstore1`, … in row order, as the source names them. The default runs are the source's ten stores:
a large and a small store of type 1, three small stores of type 2, a large store and four small stores of type 3. An empty list, a null entry, a
count below 1, and an undefined size or tenancy are `InvalidParameter`.

## Gaps (S7)

- **G2** (restaurants): the source's pitched attic is not drawn; the zones reach a flat roof at their top, one floor height high.
- **G4** (warehouse, D-161, D-162): in the source the office is lower than the storey, under a floor of the fine storage. The office is drawn to
  the storey height and the fine-storage floor above it is dropped (236.88 m²). The answer key marks the office and the fine storage with G4, so
  the harness excludes their quantities, and the floor area totals take the key's adjusted figures.

Provenance records the record (`Record=<name>`), the gaps that apply (`Gaps=G2`, `Gaps=G4`, or `Gaps=none`), the reference file with its SHA-256
(`Source=<file> sha256:<hash>`), and every parameter; the strip mall's runs are `Stores=Large:Type1x1;Small:Type1x1;…`.

## Acceptance

Every record, generated at its defaults, passes T1–T3 against its answer key through the comparison harness with the fixture programs (T1 takes
the storey's elevation and multiplier from the plan stacked once with `Stack`). T4 runs on the generators' path (D-163): one program per key from
the answer key's per-key glazing (`HarnessFixtures.KeyGlazing`, `programGlazing`), so the window area per orientation in total and per program
key is the source's within 1 %; no zone of the six records has a ratio that differs from its key's (`glazingRatioDifferences` is empty), so every
zone's window area is checked as well. T5 is above; for the strip mall's counts each run at 1 and at twice its default gives one zone per store,
each sharing walls with its row neighbours only. Every T5 plan validates, every zone's area follows the parameters, and the plan and every zone
part are one floor height high. T6 runs every simplifier and aggregator, canonical and at the integration suite's two rotated placements, and
snapshots each canonical plan (`Snapshots/<record>-canonical.txt`). The shared checks are in
`tests/Lod.Generators.Tests/Doe/SingleStorey/SingleStoreyAcceptance.cs`.

## Grasshopper components

One component per record, as for the offices ([doe-components.md](doe-components.md)), each on `DoeGeneratorComponent` with the inputs in its
order (counts, sizes, *Floor Height*, *Orientation*, *Program Map*, *Preview Location*), its record's defaults, and the outputs *Plan* (one
plan), *Multipliers* (`[1]`), and *Program Keys*.

| Component (nickname) | Inputs, with defaults | GUID |
| --- | --- | --- |
| *DOE Full-Service Restaurant* (DoeFSR) | Length (22.6087), Dining Depth (16.4427), Kitchen Depth (6.166), Floor Height (3.0488), Orientation (0), Program Map, Preview Location | `b4ca8365-a4dc-4af7-a6b5-0fc68cdb37a9` |
| *DOE Quick-Service Restaurant* (DoeQSR) | Length (15.2428), Dining Depth (7.6214), Kitchen Depth (7.6214), Floor Height (3.0488), Orientation (0), Program Map, Preview Location | `cf72627b-3035-4f91-858c-f51772989c07` |
| *DOE Strip Mall* (DoeSMall) | Store Counts (1, 1, 3, 1, 4), Store Sizes (Large, Small, Small, Large, Small), Store Tenancies (1, 1, 2, 3, 3), Depth (22.86), Large Store Width (15.24), Small Store Width (7.62), Floor Height (5.18), Orientation (0), Program Map, Preview Location | `94be46f9-90c9-49ec-8104-8d572004856e` |
| *DOE Stand-alone Retail* (DoeRet) | Length (54.27), Depth (42.27), Back Space Depth (7), Front Depth (6), Entry Width (4), Floor Height (6.096), Orientation (0), Program Map, Preview Location | `1bf76d74-0917-4acc-8d9c-e0eaa36adcbe` |
| *DOE Supermarket* (DoeSMkt) | Length (79.1901), Depth (52.7944), Storage Depth (8.975), Preparation Depth (9.8988), Floor Height (6.096), Orientation (0), Program Map, Preview Location | `2f12351b-adfd-40aa-a763-be4394bd814b` |
| *DOE Warehouse* (DoeWare) | Length (45.7178), Depth (100.579), Office Depth (9.1435), Fine Storage Depth (30.4785), Floor Height (8.534), Orientation (0), Program Map, Preview Location | `814d27a4-8483-4aba-bf78-2bf4daa62f46` |

The strip mall's three store lists (counts first, as the base orders them) give one item per run, west to east; `StoreRowParameters.Runs` turns
them into runs: lists of different lengths, a size other than `Large` or `Small` (read in any case, white space around it ignored, as BEMGen's
other enum-like inputs, D-120, D-121), and a tenancy other than 1, 2, or 3 are
`InvalidParameter`, and a count below 1 is the generator's. The strip mall lists all three tenancy keys in *Program Keys*, whatever the runs; a key
the runs do not use is unused.
