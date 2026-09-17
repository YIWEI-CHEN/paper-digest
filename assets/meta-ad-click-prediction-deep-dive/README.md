# Meta Ad Click Prediction deep dive

Editable sources live in this asset directory:

- `content.json`: Traditional Chinese / English chapters, six teaching scenarios, and annotated sources.
- `diagrams.json`: Original SVG layouts (nodes, directed paths, bilingual labels and attribution captions). These are newly drawn design syntheses, not copied source images.
- `template.html`: Offline layout, language switching, navigation, print behavior and sampling calculator, adapted from the shopping-assistant guide.

Build from the repository root:

```powershell
python scripts/build_meta_ad_click_prediction.py
python scripts/build_ml_system_design_practice.py
```

The new builder shares text/table/scenario renderers with `scripts/build_copilot_shopping_assistant.py`; it does not run or modify the shopping guide's build. Output is `summaries/zh-TW/meta-ad-click-prediction-deep-dive.html`, a single bilingual HTML file with inline CSS, JavaScript and three SVG diagrams. `?lang=zh`, `?lang=en` and `?lang=both` select a reading mode. External source links require a network; the guide itself does not.

The handbook generator adds an entry to its `ads` case. The index row uses `Misc 2026` and points both language choices to the generated HTML.

All workload numbers, timing fixtures and integrated architecture choices are illustrative. The implementation plan and pseudocode do not claim trained models or measured performance. The calculator derives posterior correction from class-dependent retention and must not be applied again to predictions already corrected through appropriate inverse weighting.
