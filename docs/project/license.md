# License

EnerGuard is licensed under the
[Apache License 2.0](https://github.com/GuidoMerliniEnel/ai-act-hackaton/blob/main/LICENSE).
Attributions are in
[`NOTICE`](https://github.com/GuidoMerliniEnel/ai-act-hackaton/blob/main/NOTICE).

Every source file carries an SPDX header:

```python
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Enel SpA
```

## Third-party dependencies

| Package                          | License      | Use            |
| -------------------------------- | ------------ | -------------- |
| scikit-learn, numpy, pandas, joblib | BSD-3-Clause | Model and data |
| shap                             | MIT          | Explanations   |
| streamlit                        | Apache-2.0   | Dashboard      |
| requests                         | Apache-2.0   | LLM calls      |
| zensical                         | MIT          | Documentation  |

The CI license gate blocks AGPL, SSPL and GPL-3.0 dependencies, in line
with the Enel OSPO policy and OP36 4.15 (Intellectual Property by Design).

## Provenance

The code builds on the EnerGuard starter kit provided by the hackathon
organisers (Deloitte × Enel FNC). The dataset is synthetic.
