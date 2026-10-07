# User guide

!!! abstract "You are in the user guide"
    This part of the site is for people who build energy models with BEMGen in Grasshopper. If you want to change BEMGen itself, go to the [developer documentation](../developer/index.md).

## Reading order { .ea-strip data-index="01" data-note="First time through" }

Read the pages in this order the first time.

<div class="grid cards compact" markdown>

1.  [Getting started](getting-started.md)

    What you need, how to install the plugin, and a first definition that runs.

2.  [What's new in 1.1.0](whats-new.md)

    *Conditioned Merge* and *Join Pieces*, *Mix Programs*, infiltration on *Envelope Preset*, and what happens to definitions saved with an earlier version.

3.  [Concepts](concepts.md)

    The words this guide uses: plan, zone, program preset, simplifier, floor aggregator, multiplier, validation, provenance, levels of detail.

4.  [Workflow](workflow.md)

    Every step from presets to *Convert2BEM* and *Convert2IDF*, with the choices at each step.

5.  [End-to-end example](example-end-to-end.md)

    One complete definition with every input value and the results you should see.

6.  [Typologies](typologies.md)

    The eighteen plan generators, their inputs and defaults, and their example definitions.

7.  [Component reference](components/index.md)

    Every component with its icon, inputs, outputs, and defaults, generated from the plugin.

</div>

## Conventions { .ea-strip data-index="02" data-note="How this guide writes" }

- Component names are in italics, as they appear on the Grasshopper canvas with *Draw Full Names* on: *Linear Plan Generator*, *Perimeter Core*, *Stack Floors*. Nicknames, the short names shown by default, are given in parentheses the first time, for example *Perimeter Core* (Z2).
- Input and output names are in italics too: the *Depth* input, the *Provenance* output.
- All BEMGen components are on the **BEMGen** tab of the Grasshopper toolbar, in panels numbered along the pipeline: *0 Info*, *1 Program*, *1 Program Presets*, *2 Generate*, *3 Simplify*, *4 Aggregate*, *5 Convert*, *6 Inspect*.
- Lengths given to plan generators and simplifiers are in **metres**, whatever the units of the Rhino model. Areas are in m², volumes in m³, temperatures in °C, angles in degrees.
