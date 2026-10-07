---
hide:
  - navigation
  - toc
---

<div class="ea-hero" markdown>

# Generate building energy models<br>*at urban scale.*

BEMGen is a Grasshopper plugin for Rhino 8 that generates building energy models at several levels of detail and checks every simplification numerically before it is converted.

</div>

## Documentation { .ea-strip data-index="01" data-note="Two parts" }

<div class="grid cards" markdown>

-   [User guide](user/index.md)

    For people who build energy models with BEMGen in Grasshopper: installing the plugin, the concepts, the workflow from presets to an IDF file, a complete worked example, the eighteen typologies, and the reference of every component.

    [Open the user guide](user/index.md){ .md-button }

-   [Developer documentation](developer/index.md)

    For people who change BEMGen itself: the architecture, the domain model, validation, the converters, the architecture decision records, the decision log, and the stage plans, taken from BEMGen's own documents with each version.

    [Open the developer documentation](developer/index.md){ .md-button }

</div>

## About BEMGen { .ea-strip data-index="02" data-note="Research question" }

BEMGen is a Grasshopper plugin for Rhino 8 that generates building energy models at several levels of detail. It builds a detailed floor plan of a building typology, simplifies its thermal zoning, stacks the floors into a building, checks that the simplified model still holds the same floor area, loads, schedules, and glazing as the detailed one, and converts the result into Grasshopper data for a ClimateStudio definition (*Convert2BEM*) or into an EnergyPlus input file (*Convert2IDF*).

BEMGen exists for a research question: how much do geometric simplification, thermal zoning, and window representation change simulated energy use when everything else (programs, internal gains, schedules, setpoints, glazed area) is held equivalent? Every simplification is therefore checked numerically before it can be converted.

!!! note "Illustrative example values"
    The program presets and the envelope preset that ship with BEMGen hold illustrative round numbers for development and testing. They are not taken from ASHRAE 90.1, the DOE prototype buildings, or any other standard, and no result based on them should be presented as if they were.

## Licence and downloads { .ea-strip data-index="03" data-note="MIT License" }

BEMGen is released under the MIT License, copyright 2026 Environmental Systems Lab. Its source code is in the BEMGen repository, which is private for now; access is given on request. The plugin and the example definitions are on the [Releases page](https://github.com/energy-atlas/BEMGen-docs/releases) of this site's repository.
