# Cover art

The map art on the report covers (`assets/art/*.svg`) is generated, not drawn. Each file is white outlines and shading that sit on the cover's color.

| File | What it shows | Source |
|---|---|---|
| `cover-ccd.svg` | Center City neighborhoods highlighted, tight zoom | BPN dashboard neighborhood boundaries |
| `cover-hpf.svg` | Neighborhoods named in the Housing Production Fund memo (Logan Square, Hawthorne, Callowhill, Francisville, Spruce Hill, Fishtown, Port Richmond) | Memo text + dashboard neighborhood boundaries |
| `cover-phloz.svg` | Neighborhoods holding the most of the 82 recommended Opportunity Zone tracts (placed by each tract's nearest transit station) | `ranking_bpn_82_combined.csv` + dashboard station and neighborhood data |
| `cover-paoz.svg` | Pennsylvania counties shaded by recommended tracts (135 outside Philadelphia, plus 82 in Philadelphia) | `recommended_135_non_philly.csv` + US Census county outlines (us-atlas) |

Shading on the neighborhood maps other than the highlighted areas is decorative.

## Regenerating

`philly_cover_art.py` needs `public/data/phila-neighborhoods.json` and `toc-stations.json` from the BPN dashboard project. `pa_cover_art.py` needs `counties-10m.json` from the `us-atlas` package and the statewide CSV. Edit the paths at the top of each script, then run it.

To make a new cover, add a list of neighborhood names to `philly_cover_art.py` and call `build(..., fit(names))`.
