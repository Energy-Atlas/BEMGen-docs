# What's new

This page says what each version changed and what to do about definitions saved with an earlier one. The other pages of this guide describe version 1.9.0.

## 1.9.0

Version 1.9.0 reads release 2.3.0 of the Energy Archetype Atlas and refuses the texts of earlier releases. It offers the IECC programs on the DOE *Programs* components, adds *Get from Atlas…* to *Mix Programs* and *Construction JSON*, moves *Schedule Draw* to generator 4.1.0, and carries the fixes made since 1.8.0: a rule for zones without HVAC under the heat-transfer options, the refusal of an unresolved climate, and code-rule daylighting on request. Every component keeps its GUID and icon; new inputs and outputs are added after the existing ones.

### Atlas release 2.3.0

BEMGen reads the exports of atlas release 2.3.0, and only those: program JSON 6.0.0, unified construction JSON 4.0.0 (the building-level equivalent), and detailed construction JSON 5.0.0. Release 2.3.0 is the release to download now, or to take with *Get from Atlas…*.

- **Texts of releases 2.0.0 to 2.2.0 are refused**, whether they are wired in or stored in a definition. A program JSON 5.4.0 or a unified construction JSON 3.1.0 is refused with the ID the program or set has in release 2.3.0, or with the remark that its ID did not change. Take the program or set again from the atlas site with *Get from Atlas…*, or export it again from release 2.3.0.
- **A DOE program map stored by 1.8.0** holds texts of release 2.2.0, so *DOE … Programs* refuses the whole map and names each moved program's new ID. *Get from Atlas…* stores it again.
- **A stored *Generator JSON* of *Schedule Draw*** names no release. It fails with a message that a program of an earlier release has another ID when the program's ID moved; when the ID did not move, it is accepted and draws the same.
- **A dwelling's window ratios follow its *Context*.** A program JSON of a dwelling can hold several window ratios, one for each construction context; *Context* (for example `foundation=slab`) chooses one, and *Source* names it. Without the keys it needs, *Program JSON* warns with `ProgramJsonFenestrationContextRequired` and does not use the JSON's window ratios.
- ***Assumptions*** lists the filled version's absent demands, the demands it records as known zeros (`metadata.absent_demands`), after its resolutions.
- **Checksums.** The SHA-256 that *Program JSON* and *Construction JSON* record is now that of the canonical form of the JSON, sorted by key and without extra whitespace, as the atlas site's `json_sha256` is. A pretty-printed file, a panel with CR LF line endings, and the site's text have one checksum. A definition's *Source* shows a new checksum once. A program or set taken from the site also records the atlas store file it came from (`Json.Store`, or `atlas store …` for a construction set), for as long as the text is not edited.
- **Imported now.** The 152 DOE Ref unified construction documents (stand-alone retail, small hotel, supermarket, and warehouse) that 1.8.0 refused for their internal mass import, because the atlas corrected them in release 2.3.0.

### IECC programs on the DOE Programs components

The strip *Get from Atlas…* on each *DOE … Programs* component now offers eleven families, the five of 1.8.0 and the IECC editions 2006, 2009, 2012, 2015, 2018, and 2021, for the eleven prototypes that the atlas has IECC programs for. The IECC families are not offered for the DOE small, medium, and large office, whose IECC folders hold whole-building programs only, nor for the supermarket, which they lack. See the [component reference](components/program-presets.md).

- **Source version only.** The atlas publishes the IECC programs in their source version. Choose *Source* in the window; *Filled* is refused key by key with the site's reason, and the window says `only the source version of …`.
- **The split keys.** The 90.1 and IECC folders split or rename a few of the reference building's space types. A key without a program of its own can take the atlas's area-weighted mix of its split spaces: the small hotel's `GuestRoom` takes `GuestRooms_Mixed` (90.1-2007, 90.1-2013, 90.1-2019, and the IECC families), and the hospital's `Office` takes `Office_Mixed` (90.1-2013, 90.1-2019, and the IECC families). The window's coverage names the mix, for example `GuestRoom takes GuestRooms_Mixed`.
- **Keys still without a program.** The secondary school's `Gym - audience` and the stand-alone retail's `Retail` stay without one, where a family splits them. The retail's mix would count its point-of-sale program twice, so it is not used. As before, such a key is named in an error, *Program Map* is not output, and *Presets* leaves its position empty, so you can complete the map with *DOE Program Map*.
- **New output.** Each *DOE … Programs* component has a fifth output, *Left Out*, a tree with one branch for each key: what the key's program does not hold, as *Program JSON*'s *Left Out* lists it, empty for a key without a program and without an atlas map.
- The ASHRAE *Climate Zone* of a stored map is needed to convert, as [below](#unresolved-climate-zones-are-refused).

### Get from Atlas on Mix Programs

*Mix Programs* has the strip *Get from Atlas…* at its bottom; double-click it to open its window. The network is used only after you click in the window; the programs and weights are stored in the definition, so every solve reads only the definition. See the [component reference](components/program.md#mix-programs).

- **Choose the members.** Choose a template and a building type; the window lists the folders that have source programs. *Start from* offers each general mix and each department mix of the folder, with its members ticked and their weights, which are the members' floor-area shares in the prototype, or *Free selection*, every source program of the folder, unticked. In a free selection a program that is a member of a general mix has that mix's area share as its weight, and another program has none.
- **Untick and reweight.** Untick members and edit the weights (each greater than 0); the window shows each member's space type, represented area, weight, and normalised share. A ticked member without a weight asks for one.
- ***OK*** downloads the ticked members (at most four at a time, filled by default or as you choose), checks each one with the component's *Climate Zone*, *Year*, *Holidays*, and *Context*, tries the mix, and stores the programs and weights in the component with one undo step only if the mix is accepted. *Clear* removes the stored mix.
- **BEMGen mixes the members itself**, by the rule of *Mix Programs* (floor-area weights), not by taking the atlas's own mix program, so that you can untick and reweight and so that the result's *Source* names every member with its program, weight, checksum, and store file. The atlas's own mix programs remain available through *Program JSON*; the two can differ where the atlas's mixing rule differs.
- **Members are any-program presets** named by their space type, so with *Space Type* unset the mix is an any-program preset, which fits any preset input.
- ***Presets* and *Weights* are optional now.** A wire into *Presets* takes precedence over the stored mix (and then needs *Weights*, as before); a wired but empty *Presets* takes precedence too, with a warning. With the stored mix and no wire, *Weights*, when given, replaces the stored weights, one for each member in the stored order.
- **New inputs** *Climate Zone*, *Year* (2007), *Holidays*, and *Context* apply to a stored mix, as on *Program JSON*. **New outputs:** *JSON*, each member's program text in member order, for example for *Schedule Draw*, and *Left Out*, a branch for each member.

### Get from Atlas on Construction JSON

*Construction JSON* has the strip *Get from Atlas…* too. Its window lists the atlas's construction sets, grouped by the template and building type their IDs begin with, and a set's contexts, such as its climate zone. *Use this set* downloads the context's unified document, checks it, and stores it as the *JSON* input's value, with one undo step; a wire into *JSON* still takes precedence. See the [component reference](components/program.md#construction-json).

- **Only whole-building sets can be used.** The window marks and refuses, before any download, the contexts whose one document serves both representations: the atlas's IECC residential and manufactured-housing sets, which describe a source dwelling's constructions by the source's own surfaces. A ResStock set is a single-dwelling set and is refused by the import (`ConstructionJsonScopeNotSupported`). A context with no unified document gives the atlas's reason.
- An IECC commercial set is stored with the warning about its source design-flow infiltration, and *Convert2IDF* does not convert it, as before.
- ***Source*** records the atlas store file the set came from and the checksum of its canonical JSON.
- **Skylights.** A set's skylight glazing is read and used for a building's skylights (before, they took the window's glazing). A building with skylights and a set without skylight glazing gets the warning `SkylightGlazingFromWindow` and the window's glazing; a building without skylights lists the skylight glazing as unused, and says nothing else.

### Schedule Draw on generator 4.1.0

*Schedule Draw* now runs `atlas-schedules` 4.1.0, which carries atlas release 2.3.0 with it. See the [component reference](components/program.md#schedule-draw).

- **Install the new generator.** Download `atlas_schedules-4.1.0-py3-none-any.whl` and `SHA256SUMS.txt` from the atlas release [atlas-schedules-v4.1.0](https://github.com/Energy-Atlas/archetype-atlas/releases/tag/atlas-schedules-v4.1.0), check the file with `sha256sum -c SHA256SUMS.txt --ignore-missing`, and install it in a virtual environment (Python 3.11 or later): `python -m venv <folder>`, then `<folder>\Scripts\python -m pip install atlas_schedules-4.1.0-py3-none-any.whl`. An environment that has 4.0.0 is upgraded with `pip install --upgrade` and the same wheel. *Command* stays `<folder>\Scripts\atlas-schedules.exe`.
- **Generator JSON** takes the `generation.json` of the program's folder in atlas release 2.3.0: `v2.3.0/<family>/<template>/<type>/generation.json` in `atlas-release-2.3.0.zip` of the atlas release [v2.3.0](https://github.com/Energy-Atlas/archetype-atlas/releases/tag/v2.3.0). *Get from Atlas…* on the component stores it.
- **Setting.** The setting is still `schema_version` 2.0.0, but its generator version is `4.1.0` (its bundle schema stays `4.0.0`); a setting that names another generator version is refused.
- **More programs can be drawn.** Release 2.3.0 generates the DOE small, medium, and large office (their detailed office folders) and the IECC commercial programs, so *Get from Atlas…* now finds a `generation.json` for them, and they are drawn (an IECC program in its source version). The atlas still has none for some folders, such as the IECC apartments and the commercial folders without a sampling building type; the window says so.
- A program JSON drawn with 1.8.0 holds program JSON 5.4.0 and is refused; draw again from a program of release 2.3.0.

### Convert2IDF and Convert2BEM

- **Daylighting on request.** *Convert2IDF* has a new last input, *Daylighting*, false by default. With it true, each zone whose program has daylighting controls (from *Program JSON*) gets them: the program's setpoint, control type, minimum fractions, steps, and method, at up to two reference points 0.8 m above the floor. The 90.1 code rule of the program's edition (2010, or 2013 to 2019) places the points and shares the controlled areas from the zone's own windows and skylights, as openstudio-standards computes them for the DOE prototypes, so a merged zone takes its own geometry. A zone without a window or skylight, or whose daylit areas the edition does not require to be controlled, gets none, and a program without a code rule (an IECC or DOE reference program) gets the warning `DaylightingNoCodeRule` and none. The IDF header lists each zone and why it has none. EnergyPlus warns once for each zone that the reference points control less than all of its lights. With the input false, the default, no daylighting object is written and the lighting load is held fixed, as the LOD study requires; *Program JSON*'s *Left Out* says when the controls are written. See the [component reference](components/convert.md#convert2idf).
- **Heat-transfer options.** With *EnableInternalWallHeatTransfer* or *EnableFloorHeatTransfer* off, a wall, floor, or ceiling is written `Adiabatic` only when both zones it separates are conditioned. A surface of a zone without HVAC, such as an unconditioned stair or an elevator core, keeps its `Interzone:<zone ID>` link whatever the options say, so that such a zone is never left with only its exterior surfaces to lose heat through (EnergyPlus stopped on a small hotel's elevator core, a zone without HVAC with a large equipment load, when its walls were sealed). *Convert2BEM*'s *Boundaries* and the IDF follow the same rule. A building with a zone without HVAC therefore shows `Interzone` where 1.8.0 showed `Adiabatic` for that zone's surfaces.

### Unresolved climate zones are refused

Some programs have values that differ by ASHRAE climate zone (loads, schedules, window ratios, daylighting). *Program JSON*, the atlas maps and mixes, take the zone from their *Climate Zone* input, such as `5B`. Without one they take the general values, with a warning, and *Convert2IDF* refuses the building with the error `ClimateZoneUnresolved`, which names each program and what differs; *Override* does not apply. The zone must be given to the component that imports the program, because the window ratios by climate have already shaped the generated windows by then. If the `.stat` file next to the `.epw` weather file states an ASHRAE zone, the error names it, the IDF header records `Weather climate zone`, and programs resolved for another zone get the warning `ClimateZoneDiffersFromWeather`.

### Program JSON reads more

- **Hot water** is delivered at most at the source outlet when the atlas caps it (`cap_at_source_outlet`): the draw's target temperature is capped hour by hour at the outlet of the last heating stage, and *Overrides* records the requested target, its maximum, and the hours it is not met.
- **Fuels and water heaters.** An equipment load whose fuel its object does not meter (for example propane gas equipment) is written as given, with the warning `ProgramJsonFuelNotApplied`, and listed in *Left Out*. *Left Out* names each water heating demand's heater, fuel, efficiency, and outlet, which are not applied: BEMGen reports the hot water's thermal demand.
- **Calendar.** *Left Out* lists the source calendar's daylight saving when it is recorded (the IDF runs on standard time), and its holiday rules only when the source has them and no *Holidays* are given, with the warning `ProgramJsonBindingNotMet`.
- **Messages.** The messages name the real inputs; a newer program JSON schema tells you to update BEMGen, and an older one to export again.

### Downloads from the atlas site

All the atlas windows share one limit: at most four files are downloaded at a time. A download answered with HTTP 429 or a server error is asked for once more after a short wait. If GitHub Pages is limiting your network, the window says to wait a few minutes. A window shows any other fault in its status line.

### Opening older definitions

Definitions saved with 1.8.0 open with their saved values and solve as before except where this page says otherwise:

- *Mix Programs*, the *DOE … Programs* components, and *Convert2IDF* get their new inputs and outputs unset (*Daylighting* false), and *Mix Programs*' *Presets* and *Weights* become optional.
- A *Program JSON* or *Construction JSON* that stores a text of release 2.2.0 or earlier, and a DOE map stored by 1.8.0, show the refusal described above until the program, set, or map is taken again from the atlas. A *Schedule Draw* saved with 1.8.0 needs its setting's generator version changed to `4.1.0` and a `generation.json` of release 2.3.0.
- The checksums in *Source* change once, and a building with a zone without HVAC converts with the new boundaries.
- The example definitions in the examples zip have been rebuilt with 1.9.0: `program-json-office.gh`, `schedule-draw.gh`, and `doe-atlas-map.gh` hold texts of atlas release 2.3.0.

## 1.8.0

Version 1.8.0 takes programs from the [Energy Archetype Atlas site](https://energy-atlas.github.io/archetype-atlas/). The network is used only after you click in one of the windows below; every solve reads only the definition, so stored programs solve offline. The windows need Windows, where they use WebView2. Version 1.9.0 changed some of what this section says: the atlas release, the families and keys of the DOE maps, the checksum, and which programs *Schedule Draw* can draw; the 1.9.0 section above gives the current rules.

### Get from Atlas on Program JSON

*Program JSON* has two strips at its bottom; double-click one to open its window. See the [component reference](components/program.md#program-json).

- ***Get from Atlas…*** shows the atlas site. Open a program's page in the catalogue, choose *Filled* (the default) or *Source*, and click *Use this program*. The program JSON is downloaded, checked against the site's index, and stored as the *JSON* input's value, with one undo step. Programs that the atlas publishes only as source, such as the IECC programs, select *Source* and say why.
- ***Edit JSON…*** shows the stored text to paste or edit; *OK* checks it before it is stored.
- A wire into *JSON* still takes precedence over the stored text.

### Atlas program maps on the DOE Programs components

Each *DOE … Programs* component in *1 Program Presets* has the strip *Get from Atlas…*. Its window lists five atlas families, DOE Ref pre-1980, DOE Ref 1980–2004, 90.1-2007, 90.1-2013, and 90.1-2019, each with how many of the prototype's program keys it covers, such as `90.1-2019: 3 of 4 keys; Retail has no program.`. See the [component reference](components/program-presets.md).

- ***OK*** downloads every key's program of the chosen family (filled by default, or source), checks each, and stores them in the component with one undo step. Each key takes the atlas program of its own space type in the prototype's folder; the window-to-wall ratios stay the DOE reference building's, so the presets fit the generator's geometry. *Clear* returns to the illustrative presets.
- **New inputs** *Climate Zone*, *Year*, *Holidays*, and *Context* apply to a stored map, as on *Program JSON*. **A new output**, *JSON*, gives each key's program text, for example for *Schedule Draw*.
- **Keys without a program.** The 90.1 families split or rename a few space types: 90.1-2007 the secondary school's `Gym - audience` and the small hotel's `GuestRoom`, 90.1-2013 and 90.1-2019 also the hospital's `Office` and the stand-alone retail's `Retail`. Such a key is named in an error, *Program Map* is not output, and *Presets* leaves its position empty, so you can give it a preset and rebuild the map with *DOE Program Map*.
- The new example `doe-atlas-map.gh` is the DOE medium office with the atlas's 90.1-2007 programs stored in *DOE Medium Office Programs*.

### Generator JSON from the atlas site

*Schedule Draw* has the strip *Get from Atlas…* too. Its window finds the atlas folder of the program in *Program JSON* and stores that folder's `generation.json` as *Generator JSON*. The atlas has no `generation.json` for its detailed office folders, so programs of the DOE small, medium, and large office cannot be drawn yet; the window says so.

### Opening older definitions

Definitions saved with 1.7.0 open with their saved values; the DOE *Programs* components get the new inputs unset and solve as before. The checksum in *Program JSON*'s *Source* is now that of the text with LF line endings, so a definition whose stored text had CR LF line endings shows a new checksum once. The example definitions in the examples zip have been rebuilt with 1.8.0.

## 1.7.0

Version 1.7.0 moves *Schedule Draw* to version 4.0.0 of the atlas's schedule generator and reads release 2.2.0 of the Energy Archetype Atlas.

### Schedule Draw on generator 4.0.0

*Schedule Draw* now runs `atlas-schedules` 4.0.0, which carries atlas release 2.2.0 with it. See the [component reference](components/program.md#schedule-draw).

- **Install the new generator.** Download `atlas_schedules-4.0.0-py3-none-any.whl` and `SHA256SUMS.txt` from the atlas release [atlas-schedules-v4.0.0](https://github.com/Energy-Atlas/archetype-atlas/releases/tag/atlas-schedules-v4.0.0), check the file with `sha256sum -c SHA256SUMS.txt --ignore-missing`, and install it in a virtual environment (Python 3.11 or later): `python -m venv <folder>`, then `<folder>\Scripts\python -m pip install atlas_schedules-4.0.0-py3-none-any.whl`. An environment that has 3.0.0 is upgraded with `pip install --upgrade` and the same wheel. *Command* stays `<folder>\Scripts\atlas-schedules.exe`.
- **Generator JSON takes `generation.json`.** Give the `generation.json` of the program's folder in atlas release 2.2.0: `v2.2.0/<family>/<template>/<type>/generation.json` in `atlas-release-2.2.0.zip` of the atlas release [v2.2.0](https://github.com/Energy-Atlas/archetype-atlas/releases/tag/v2.2.0). The `generator.json` of earlier releases is refused, with a message that names the file to give.
- **Setting 2.0.0.** The setting's `schema_version` is `2.0.0`, its generator version `4.0.0` and bundle schema `4.0.0`, and it has no `view`: the program JSON's own version, filled or source, chooses the values drawn from. A 1.0.0 setting is refused with what to change.
- **Provenance** names the atlas release the generator read and its manifest checksum.
- **Drawn schedules.** A program JSON drawn with 1.6.0 still reads. Drawing it again gives the same schedules where the atlas found generator 4.0.0 equal to 3.0.0, as for the DOE Ref medium office of the example; the atlas's 90.1 apartment-building common-area programs now carry their heat fractions, so their draws can differ.

### Atlas release 2.2.0

*Program JSON* and *Construction JSON* read the exports of atlas release 2.2.0, the release to download now. Its contracts are those of 2.0.0 and 2.1.0, whose exports remain valid, and later releases of the same program JSON contract are read too.

### Opening older definitions

Definitions saved with 1.6.0 open with their saved values. To draw with a `schedule-draw.gh` saved with 1.6.0, replace its `generator.json` panel with the release 2.2.0 `generation.json` and its setting with a 2.0.0 setting. The example definitions in the examples zip have been rebuilt with 1.7.0.

## 1.6.0

Version 1.6.0 adds *Schedule Draw*, which draws stochastic schedules with the atlas's schedule generator, and reads release 2.1.0 of the Energy Archetype Atlas.

### Schedule Draw

A new component in *1 Program*, *Schedule Draw* (SDraw), draws stochastic 8,760-hour schedules for a program JSON with the atlas's schedule generator, as an optional add-on to the program's own schedules. From the *Program JSON* text, the *Generator JSON* of the program's release folder (`generator.json`), a *Setting*, and a *Seed*, it gives a *Drawn JSON* whose occupancy, lighting, equipment, hot-water, activity, and setpoint schedules are drawn; connect it to *Program JSON*. The same inputs and seed always give the same text, and *Provenance* records the generator, the seed, and the checksums. See the [component reference](components/program.md#schedule-draw).

- **It needs Python and the generator.** Install Python 3.11 or later, download `atlas_schedules-3.0.0-py3-none-any.whl` from the atlas release [atlas-schedules-v3.0.0](https://github.com/Energy-Atlas/archetype-atlas/releases/tag/atlas-schedules-v3.0.0), and install it in a virtual environment: `python -m venv <folder>`, then `<folder>\Scripts\python -m pip install atlas_schedules-3.0.0-py3-none-any.whl`.
- **It runs the generator as an external command**, only while *Run* is true. Set *Command* to `<folder>\Scripts\atlas-schedules.exe` and leave *Folder* unset. BEMGen passes it files and opens no network connection.
- **Calendar 2007.** Drawn schedules are for 2007, so keep *Program JSON*'s *Year* at 2007.
- Apartment-unit and composition recipes are not supported yet.
- The new example `schedule-draw.gh` opens with *Run* false and the program's own schedules; set *Command* and *Run* to draw.

### DOE Reference Program

A new component in *1 Program*, *DOE Reference Program* (DOEProg), gives source programs of the DOE MidriseApartment reference building (Chicago, 5A) by original zone name. A preset needs an explicit *WWR* and two separate acceptances: that the generated geometry is not the DOE geometry, and that the source's daylight-saving shift is left out. See the [component reference](components/program.md#doe-reference-program).

### Atlas release 2.1.0

*Program JSON* and *Construction JSON* read the exports of atlas release 2.1.0, the release to download now. Its contracts are those of 2.0.0, so exports of release 2.0.0 remain valid.

### Convert2IDF

- A zone's coplanar floors, ceilings, and roofs, and its walls without windows that run in a straight line, are merged into one surface where the result is a simple polygon. IDF files have fewer surfaces, the header lists the merges, and EnergyPlus no longer warns about incomplete view factors in large merged zones. Annual loads change slightly, by up to about 2 % for zonings that put many rooms in one zone.
- An input is appended: *Require Floor Research Eligibility* (FloorCheck, default false), an opt-in check for research comparisons of floor zonings.
- Floors made of two rectangles that meet at one corner now convert, and tiny internal masses from rounding are no longer written.

### Opening older definitions

Definitions saved with 1.5.0 open with their saved values, with *Require Floor Research Eligibility* false. The example definitions in the examples zip have been rebuilt with 1.6.0, and `schedule-draw.gh` is new.

## 1.5.0

Version 1.5.0 adds generators for the DOE commercial reference buildings and reads release 2.0.0 of the Energy Archetype Atlas.

### DOE reference buildings

Fifteen new generators in *2 Generate* draw the DOE commercial reference buildings, from *DOE Small Office* to *DOE Hospital*, with the DOE zones on every storey. See [Typologies](typologies.md#doe-reference-buildings).
- A DOE generator's zones take their presets from a *Program Map*, one preset per program key.
- Each generator has a matching *Programs* component in *1 Program Presets* that gives the map. *DOE Program Map* in *1 Program* builds a map from edited presets.
- The generator's *Multipliers* output goes into the floor aggregator beside its floors.

### Program JSON

*Program JSON* reads program JSON 5.4.0 as atlas release 2.0.0 exports it, in the filled or the source version. Program JSON 2.0.0 is no longer read.
- Two inputs are appended: *Climate Zone* (CZ), which selects the values that differ by climate, and *Context* (Ctx), which selects the loads that apply only with a construction context.
- *WWR* no longer has a default. Without it, the JSON's window ratios per orientation give the glazing, or 0.4 when the JSON has none.
- A filled program's hot water takes the weather file's water mains temperature.
- Programs may carry daylighting controls. *Convert2IDF* never writes them: daylight dimming stays part of the lighting load, and the IDF header names the zones that have controls.

### Construction JSON

*Construction JSON* reads the unified 3.1.0 and detailed 4.3.0 construction sets of atlas release 2.0.0. The older unified 2.0.0 and detailed 3.0.0 sets are no longer read.
- With a set, ground floors take the set's own F-factor or layered ground construction instead of the Example envelope's. An F-factor floor needs *Convert2IDF*'s *Weather* file.
- IECC construction sets are read but not converted: their infiltration is given per zone.

### Glazing per orientation

The preset components and *Program JSON* gain *WWR North*, *WWR East*, *WWR South*, *WWR West*, and *Skylight Ratio*, all unset by default.

### Convert2IDF

Every IDF with ground floors also requests the hourly inside-face conduction of each ground surface and `Output:Surfaces:List, Details`.

### Opening older definitions

Definitions saved with 1.4.0 open with their saved values; the new inputs are unset. A *Program JSON* or *Construction JSON* that holds an older atlas text now gives an error asking for an export from atlas release 2.0.0: give it the new text. The example definitions in the examples zip have been rebuilt with 1.5.0, and `program-json-office.gh` holds a program JSON 5.4.0 export.

## 1.4.0

Version 1.4.0 lets *Convert2IDF* take its constructions from a construction set instead of an envelope preset.

### Construction JSON

A new component in *1 Program*, *Construction JSON* (CJson), reads the text of a whole-building construction set of the Energy Archetype Atlas into a *Construction Set*: one layered construction per envelope role, the window's glazing and any solar multiplier, the internal-mass data, and the infiltration. *Source*, *Roles*, and *Unused* say what it read and what it could not use. A set for a single dwelling is refused, and a detailed set is read but cannot be converted; connect the whole-building set of the same context instead. See the [component reference](components/program.md#construction-json).

### Convert2IDF

- Two inputs are appended: *Construction* (Cons), the set to use instead of *Envelope* (connect one, not both), and *Fill From Example* (Fill, default false). A role the set lacks but the building needs is an error unless *Fill From Example* is true; the ground always takes the Example envelope's construction, with a remark.
- With a set, the internal masses are balanced against the set's reference heat capacity: the capacity the building's own walls and slabs do not represent is added as furnishing, wall, and floor mass, and the header lists the balance.
- A slab inside a zone that spans storeys is written as internal mass of twice its area with half its thickness, so its heat capacity counts once (each face exchanges heat with the zone; EnergyPlus internal mass has one face). This changes the IDF of *Single Zone Building* and *Single Zone per Floor Type* buildings, with any envelope.

### Opening older definitions

Definitions saved with 1.3.0 open as they were, with *Construction* unset and *Fill From Example* false. The example definitions in the examples zip have been rebuilt with 1.4.0.

## 1.3.0

Version 1.3.0 makes the file of *Convert2IDF* ready to simulate in EnergyPlus 26.2, with the outputs a comparison of levels of detail needs, and lets the storeys a floor multiplier leaves out cast shadows.

### Convert2IDF

- The IDF targets **EnergyPlus 26.2** (it was 25.2).
- A new input, *Weather* (Wthr, optional), takes the path of an `.epw` weather file. The IDF then holds `Site:Location` from the file's header, and the header and *Provenance* name the file with its SHA-256. Without one, the remark `NoWeatherFile` says that EnergyPlus takes the location from the weather file it runs with. A file that cannot be read stops the conversion with the error `InvalidWeatherFile`. The weather file itself is still given to EnergyPlus when you run it.
- The file requests **hourly outputs**: the meters behind heating, cooling, and the total load, written only for what the building uses (so no meter warning for gas a building does not have); the zone mean air temperature of every zone; the ideal-loads heating and cooling of every zone; the annual summary tables; and an SQLite file. What each one is for: [Experiment outputs](../developer/research/experiment-outputs.md).
- **Ground temperatures** are the building's monthly mean indoor setpoint minus 2 °C (18 °C before; 20.5 °C with the built-in presets). The setpoint is the midpoint of heating and cooling, weighted by floor area over the conditioned zones.
- **Non-convex outdoor surfaces**, such as the roofs of L-, U-, and court-shaped plans, are written as convex pieces with the same area, so that EnergyPlus computes their shadows correctly. The remark `SurfaceSplit` names them.
- A zone whose infiltration basis is an exterior area it does not have (an interior core under a per-area basis) gets no infiltration object, since its flow is zero; the remark `InfiltrationNotWritten` names it.
- The header holds a **case record**: lines naming the building, the zoning, the weather file, and the envelope, so that a simulated file can be identified without Grasshopper.
- *Provenance* gains the lines `WEATHER:`, `GROUND:`, and `SHADING:`, and says `ENERGYPLUS: 26.2`.

### Shading of unmodelled storeys

*Stacked Floor Zone Multiplier* models one storey for a group of identical storeys. The storeys it leaves out now cast shadows: both converters write their outdoor walls, at their true heights, as opaque shading surfaces. In a courtyard plan this keeps the wings shading each other as they do with every storey modelled. *Convert2BEM* has a new output, *Shading* (Shd, output 31); *Convert2IDF* writes the same surfaces as `Shading:Building:Detailed`. Under the other aggregators *Shading* is empty, because every storey is modelled.

### Opening older definitions

Definitions saved with 1.2.0 or 1.1.0 open as they were, with their values and wires; *Weather* is unset. Definitions saved with 1.0.2 or earlier still lose the infiltration values of their presets, as described under [1.1.0](#definitions-saved-with-an-earlier-version). The example definitions in the examples zip have been rebuilt with 1.3.0.

## 1.2.0

Version 1.2.0 reads programs from the Energy Archetype Atlas, and a program can now hold everything such a program describes: end uses, heat fractions, the occupants' activity, heating and cooling as separate sides, hot-water temperatures, loads per dwelling, and a calendar with holidays.

### Program JSON

*Program JSON* (PJson), in panel *1 Program*, turns the text of a program JSON 2.0.0 file from the atlas into a program preset. It reads only the **defaulted** export, in which the atlas has filled in every unknown value; a raw export is rejected with a message to export the defaulted form. It reads no file and no network: connect the JSON text itself, for example from a *Panel* or a file read by Grasshopper.

The text is checked against the program JSON schema and the contract's rules before anything is made, and every message names the place in the JSON it concerns. The preset then holds the JSON's loads, end uses, heat fractions, people, heating and cooling, hot-water temperatures, and every schedule, expanded hour by hour on the calendar of *Year* (default 2007, which must not be a leap year) and *Holidays* (MM-DD text, such as `07-04`, on which the JSON's holiday rules apply).

The inputs after *JSON* complete or override it:

- *Name* and *Space Type*: unset, the preset takes the JSON's name and has no space type, so it fits every preset input of a plan generator, as an [any-program preset](workflow.md#any-program-preset) does.
- *WWR*: the JSON holds no glazing, so the window-to-wall ratio is an input, 0.4 by default.
- *Loads*: each load you connect replaces the JSON's loads of its type and end use, or is added when the JSON has none, such as ventilation.
- *Heating On*, *Cooling On*, *Heating Setpoint*, *Cooling Setpoint*, *Activity*, *People Radiant*, and *People Sensible* replace the JSON's controls.

Its outputs are the *Preset*, its *Source* (the JSON's identity and checksum, the atlas program, the calendar, every override, and what was left out), the *Assumptions* the atlas's defaults made, the *Overrides*, and what was *Left Out*: shared services, which BEMGen does not model, and the design-day rules of the schedules. The example definition `program-json-office.gh` uses the atlas's Medium Office program as the office of an *Office Plate*.

### Richer programs

The general components of panel *1 Program* and the preset components gain inputs at the end; their earlier inputs are unchanged.

- ***Load*** has the basis `PerDwellingUnit` (a value per dwelling: a generated dwelling-unit zone holds one dwelling, and a merged zone the sum of its sources), an optional *End Use* that tells loads of one type apart (a program holds one load per type, end use, and basis), the heat fractions of lighting and equipment (*Radiant*, *Latent*, *Lost*, *Visible*, *Return Air*; unset, the values the IDF used before), and the *Target Temperature* and *Inlet Temperature* of hot water (unset, 60 °C and 10 °C).
- ***Program Preset*** and every built-in preset have *Heating On* and *Cooling On* (both true by default): a conditioned space can be only heated or only cooled, and needs at least one side. *Program Preset* also has the occupants' *Activity* schedule (unset, 120 W per person), *People Radiant* (0.3), and *People Sensible* (a number, or `autocalculate`, the default).
- ***Schedule*** has the kind `Activity` (W per person) beside `Fraction` and `Temperature`.
- ***Mix Programs*** and every zone merge carry all of it. A zone merge weights per-dwelling loads by the dwellings of each source; in a mix, a weight stands for the preset's share of dwellings as well as of floor area. Heat fractions are weighted by each load's share, hot-water temperatures by each load's flow, and the occupants' activity and fractions by the occupants each program brings. The heating setpoint mixes over the heated programs only and the cooling setpoint over the cooled ones; a heating setpoint above the cooling setpoint is an error. In a mix, occupancy given in more than one basis (per floor area, per dwelling, absolute) is an error when any preset has a per-person load or the presets with occupants differ in their people settings; give all occupancy in one basis.

The defaults are the values BEMGen used before, so the built-in presets give the same results as in 1.1.0.

### The converters

- *Convert2BEM* has nine new outputs, 22 to 30: *Load End Uses* (LE), *Heat Fractions* (HF), *Dwelling Units* (DU), *Activity* (Act), *People Radiant* (PR), *People Sensible* (PS), *Water Target* (WT), *Water Inlet* (WI), and *Calendar* (Cal). The heating or cooling setpoints of a zone that is only cooled or only heated are empty. See [Convert2BEM](workflow.md#6-convert2bem).
- *Convert2IDF* writes the program's heat fractions, people properties, and hot-water temperatures, and a zone with one side gets `ThermostatSetpoint:SingleHeating` or `ThermostatSetpoint:SingleCooling`. The run period takes its year from the building's calendar; without one, as with the built-in presets, it is 2007, which starts on a Monday, as 2018, the year used before, does.

### Opening older definitions

Definitions saved with 1.1.0 open as they were, with their values and wires; the new inputs take their defaults. Definitions saved with 1.0.2 or earlier still lose the infiltration values of their presets, as described under [1.1.0](#definitions-saved-with-an-earlier-version). The example definitions in the examples zip have been rebuilt with 1.2.0.

## 1.1.0

Version 1.1.0 added a plan simplifier, a way to mix programs, and a new place for infiltration.

### Conditioned Merge

*Conditioned Merge* (Z1c), in panel *3 Simplify*, is a fifth plan simplifier. It sorts the zones of a floor into two classes and merges each class:

- **Conditioned** zones, those whose program preset has heating and cooling setpoints (a *Conditioned* preset), become one zone, `Conditioned-1`.
- **Unconditioned** zones, such as the stairs, become another, `Unconditioned-1`.

Each merged zone takes the space type its sources share, or `Mixed` when they differ. Loads, schedules, and setpoints are combined as in every zone merge ([Workflow](workflow.md#3-simplify-the-plan)).

What sets it apart is the floor area it keeps. *Perimeter Core* and *Single Zone per Floor* give every zone a conditioned program as soon as one source is conditioned, so wherever they cover a stair, the conditioned floor area grows and *Validate* reports a note. *Conditioned Merge* never mixes the two classes, so the conditioned floor area is exactly that of the plan. On the default linear plan (432 m², of which the 72 m² stair is unconditioned) it gives a conditioned zone of 360 m² and a stair zone of 72 m², and *Validate* shows no note.

#### Join Pieces

*Semantic Merge* and *Conditioned Merge* both have a Boolean input *Join Pieces* (J), false by default.

- **False:** every connected piece of a class becomes its own zone. This is what *Semantic Merge* always did.
- **True:** every piece of a class becomes part of one zone. The stairs of a floor, for example, become one stair zone, even though they do not touch.

On the default *Stair Bay Bar* (three stair bays, 612 m²), *Semantic Merge* gives seven zones: three stairs and four groups of dwellings. With *Join Pieces* true it gives two: one stair zone of three pieces (108 m²) and one dwelling zone of four pieces (504 m²). *Conditioned Merge* gives the same two zones, named `Unconditioned-1` and `Conditioned-1`, and its conditioned area is exactly the plan's 504 m².

A zone made of several pieces is one zone for everything downstream: one set of loads, one multiplier, one `Zone` object in the IDF. The viewport previews draw one solid per piece, and *Convert2BEM* gives one closed Brep per piece in the *Zones* branch of the zone.

### Mix Programs

*Mix Programs* (Mix), in panel *1 Program*, mixes several program presets into one new preset. Give it the presets (*Presets*) and one weight for each (*Weights*): the preset's share of the floor area, in any unit, because only the ratios matter. Use it for a zone that holds several programs, such as a dwelling with a shop below.

The mix is calculated the way a zone merge combines the programs of zones with those floor areas:

- loads per floor area and in air changes per hour are weighted by the area share;
- loads per person are weighted by the occupants each preset brings;
- absolute loads, such as a fixture's flow, are added as they are, without weights;
- schedules and setpoints combine as they do when zones merge; the mix is conditioned if any preset is, and its setpoints are those of the conditioned presets;
- the space type is that of the preset with the largest weight, and the window-to-wall ratio is the weighted mean, unless you give a *Space Type* or a *WWR*.

For example, mixing *Dwelling Unit Preset* and *Corridor Preset* with the weights 0.7 and 0.3 gives a preset named `Mix of Example Dwelling Unit 0.7, Example Corridor 0.3` of space type `DwellingUnit`, with occupancy 0.021 people/m², lighting 5 W/m², equipment 3.5 W/m², and a window-to-wall ratio of 0.27, conditioned. The same program results from merging two zones of 70 m² and 30 m² with *Single Zone per Floor*.

A mix cannot combine absolute occupancy in one preset with a per-person load in another, because the number of people would then depend on a zone area the mix does not know; give occupancy per floor area instead. The mixed preset goes wherever a program preset goes, and its provenance records the presets and their weights. *Name* is optional; unset, it is built from the names and the normalised weights.

### Infiltration is set on Envelope Preset

Infiltration is no longer part of a program preset. It is one setting for the whole building, on *Envelope Preset*, and every zone gets it from its own surfaces or volume. *Envelope Preset* has three new inputs:

| Input | Nickname | Default | Meaning |
| --- | --- | --- | --- |
| Infiltration Rate | Inf | 0.3 | The design rate, not negative, in the unit of the basis. |
| Infiltration Basis | InfB | `AirChangesPerHour` | What the rate is per: `PerExteriorSurfaceArea` (m³/h per m² of the zone's outdoor walls, roofs, and exposed floors, windows included), `PerExteriorWallArea` (m³/h per m² of its outdoor walls), or `AirChangesPerHour` (1/h of its volume). Right-click the input to choose one, or extract it as a dropdown. |
| Infiltration Schedule | InfS | always on | Optional fraction schedule that multiplies the rate. |

The effect of this on the converters:

- *Convert2IDF* writes one `ZoneInfiltration:DesignFlowRate` object per zone, in EnergyPlus's own method for the basis. A zone made of several pieces takes the surfaces or volume of all its pieces.
- *Convert2BEM* has four new outputs, 18 to 21: *Infiltration Rate* (IR), *Infiltration Basis* (IB), *Infiltration Schedule* (IS), and *Infiltration Flows* (IF), the design flow of each zone in m³/h. See [Convert2BEM](workflow.md#6-convert2bem).
- The program preset components no longer have *Infiltration* and *Infiltration Schedule* inputs, and the example presets no longer carry rates. The mall, lobby, retail, and operating-theatre presets used to have their own rates (0.8, 0.6, 0.5, and 0.1 air changes per hour); the whole building now uses the one rate of its *Envelope Preset*.
- *Load* no longer accepts the load type `Infiltration` or the basis `PerExteriorWallArea`; it reports `'Infiltration': infiltration is not a program load: set it on the Envelope Preset.`

### Definitions saved with an earlier version

!!! warning "Infiltration values in old definitions are dropped"
    When you open a definition saved with version 1.0.2 or earlier, Grasshopper shows a message about the removed inputs of the preset components, and **any infiltration values or wires on those inputs are dropped**. The building then uses the infiltration of its *Envelope Preset*, 0.3 air changes per hour by default. If your presets used other rates, set the rate (and basis) on *Envelope Preset*, and connect it to the converters.

Definitions that use *Semantic Merge* open with *Join Pieces* false, so they give the same zones as before. The example definitions of 1.1.0 were rebuilt with the new components.
