# Dataset

`energuard_dataset.csv` is a **synthetic** dataset of 2,400 grid assets
provided with the hackathon starter kit. It contains no personal or
production data (OP36 4.8, 4.12).

## Formats

| File                          | Format                                      |
| ----------------------------- | ------------------------------------------- |
| `energuard_dataset.csv`       | Standard: `,` separator, `.` decimal. Used by the code |
| `energuard_dataset_EXCEL.csv` | `;` separator, `,` decimal, for Italian Excel |
| `energuard_dataset.xlsx`      | Formatted workbook with a column dictionary |

`utils_io.carica_csv()` reads both CSV variants.

## Columns

| Column                          | Type        | Description                                       | In model |
| ------------------------------- | ----------- | ------------------------------------------------- | -------- |
| `asset_id`                      | string      | Asset identifier (`AST-00001`)                    | No       |
| `tipo_asset`                    | categorical | `linea_AT`, `trasformatore`, `cabina_primaria`, `turbina_eolica` | Yes |
| `area_geografica`               | categorical | `Nord`, `Centro`, `Sud`, `Isole`                  | **No** ([D-03](../decisions/index.md#d-03)) |
| `eta_anni`                      | int         | Asset age in years                                | Yes      |
| `temperatura_media`             | float       | Mean operating temperature (°C)                   | Yes      |
| `vibrazione_indice`             | float       | Vibration index                                   | Yes      |
| `carico_pct`                    | float       | Mean load (%)                                     | Yes      |
| `umidita_media`                 | float       | Mean ambient humidity (%)                         | Yes      |
| `manutenzioni_ultimi_5anni`     | int         | Maintenance interventions in the last 5 years     | Yes      |
| `giorni_da_ultima_manutenzione` | int         | Days since last maintenance                       | Yes      |
| `criticita_utenza`              | categorical | `standard`, `alta`, `critica` (e.g. hospitals)    | Yes      |
| `guasto_entro_30gg`             | 0/1         | **Target**: failure within 30 days                | Label    |

## Known anomaly: South vs Islands

The hackathon deliberately hides a label bias in the data. Findings
([D-04](../decisions/index.md#d-04)):

| Area   | Recorded failure rate | Mean age | Maintenance (5 y) | Days since last |
| ------ | --------------------- | -------- | ----------------- | --------------- |
| Nord   | 0.09                  | 14.1     | 4.1               | 167             |
| Centro | 0.13                  | 17.3     | 3.8               | 208             |
| Sud    | 0.24                  | 23.2     | 2.1               | 343             |
| Isole  | 0.45                  | 24.9     | 1.7               | 386             |

- Sensor readings (temperature, vibration, load, humidity) and the mix of
  asset types and criticality are the same in all areas.
- South and Islands have almost identical profiles, yet recorded failures
  are 0.24 vs 0.45. At equal risk (vibration ≥ 6 or age ≥ 20) the rates
  are 0.26 vs 0.49.
- The South is the only badly calibrated area: the model predicts about
  0.40 and observes 0.24.

**Main hypothesis:** failures in the South are under-reported. **Alternative:**
recording processes differ between territories. The data cannot tell them
apart; a field check is needed. See the
[impact assessment](../compliance/impact-assessment.md).
