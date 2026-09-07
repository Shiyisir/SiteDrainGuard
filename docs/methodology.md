# Methodology

## Synthetic site

The demo contains eight synthetic subcatchments (about 9.45 ha), eight junctions, one storage node, one outfall, nine conduits and one pre-placed pump. Coordinates are local planar coordinates. The values are designed to create an observable but small scenario-comparison problem; they are not a real site or a design recommendation.

## Rainfall

Built-in CSV events use a fixed `elapsed_min,intensity_mm_h` schema. The loader rejects missing columns, non-numeric values, negative or excessive intensities, duplicate/non-monotone timestamps, nonuniform steps, fewer than three rows and durations over 24 hours. The selected event is written into the copied `[TIMESERIES]` section only.

## SWMM and scenarios

The model uses SI flow units (`CMS`) and dynamic-wave routing. S0–S4 share the same base model, rainfall event, routing options and simulation period. Only the declared scenario mutations vary: pump curve, C05 diameter and storage-curve ordinates. A manifest records before/after tokens.

## Metrics

Node statistics provide maximum depth, full depth, flooding volume, flooding duration, peak flooding rate and maximum ponded volume. The dashboard aggregates these into total flood volume, flooded node count, maximum depth/depth ratio, longest flooding duration and outfall peak flow. Flooding volume is displayed as m³ and duration as hours after the unit audit documented in `docs/data_dictionary.md`.

## Risk

GREEN/YELLOW/ORANGE/RED are transparent display heuristics based on depth ratio, flooding volume and flooding duration. They are not regulatory or design classifications.

## Cost effectiveness

Costs come from `costs.yaml` and are explicitly assumptions. Reduction is always measured against S0. Negative reduction remains negative; unit avoided-volume cost is shown only when a scenario has positive avoided volume.

## Rational Method and sensitivity

The Rational Method check uses `Q = 0.00278 C i A` with C=0.82, intensity in mm/h and area in ha. It warns on extreme ratios but never declares SWMM calibrated. One-at-a-time sensitivity runs S0 at rainfall intensity scales 0.8, 1.0 and 1.2.
