# Amazon Product Recommendation System deep dive

Editable sources for the standalone Traditional Chinese / English guide.

- `content.json`: 15 chapters, 18 follow-up/rehearsal answers, and 5 scenarios. Paired strings are `[zh-TW, en]`.
- `sources.json`: 22 reading/code references with bilingual reading notes and provenance limits.
- `template.html`: layout, language controls, navigation, interactions, and compact print styles.
- `../../scripts/build_amazon_product_recommendation.py`: standard-library builder and 3 original SVG diagrams.
- Output: `../../summaries/zh-TW/amazon-product-recommendation-deep-dive.html`.

Build from the repository root:

```powershell
python scripts/build_amazon_product_recommendation.py
```

The HTML works offline, including diagrams and interactions. External source links need a network. Use `?lang=zh`, `?lang=en`, or `?lang=both`. Printing expands all answers and scenarios, then restores the screen state. The example architecture, sizing numbers, policies, and pseudocode are teaching designs; no model training or measured performance is claimed.

The handbook entry is maintained in `scripts/build_ml_system_design_practice.py` and `assets/ml-system-design-practice/ml_system_design_template.html`; regenerate it with `python scripts/build_ml_system_design_practice.py`. The homepage entry is in `index.html`, classified as **Misc 2026**.
