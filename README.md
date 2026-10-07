# Stack Overflow Developer Survey 2025 Analysis

Course project for **Introduction to Data Science** (Faculty of Science, University of Kragujevac).

## Project description

The project analyzes data from the **Stack Overflow Developer Survey 2025**, the annual survey Stack Overflow runs among developers worldwide. The survey covers respondent demographics, work experience, technologies used, employment type and education, as well as compensation data.

**The goal** is to build a regression model that predicts a respondent's total yearly compensation from the other survey attributes. The target variable is `ConvertedCompYearly`, compensation converted to US dollars, because the amount reported in the respondent's own currency (`CompTotal`) is not comparable across countries. Its base-10 logarithm is modeled, since the raw distribution is extremely skewed.

The work proceeded in five steps, in this order:

1. **dataset overview**: source, survey structure, sample composition, missing values and candidates for the target variable,
2. **choosing and validating the target variable**: how the two compensation columns relate and which one is usable,
3. **cleaning**: population, duplicates, structural errors, outliers, missing values and the train/test split,
4. **feature engineering**: deriving new variables from multiple-choice columns and ranking questions,
5. **modeling**: linear regression with diagnostics, Ridge, Lasso and principal component regression, with model selection and evaluation on the test set.

The data is downloaded from Kaggle with the `kagglehub` library and is not stored in the repository.

## Result

The selected model is **Lasso** (λ = 0.00155), which keeps **423** of 707 columns. On the test set, which was not used in any decision:

| metric | value |
| --- | --- |
| R² (on log salary) | **0.6720** |
| typical error | **23.8%**, i.e. **$16,630** |
| prediction within a factor of two | for **87.6%** of respondents |
| prediction within 25% | for **51.6%** of respondents |

To give that number a frame of reference, three baselines were measured before any model was built (cross-validation on the training set): predicting a constant gives **−0.0001**, country alone **0.5429**, and all survey attributes without any derived variable **0.6668**. The variables derived in the fourth step add **+0.0101** over that last bar, which is less than they appeared to add on the training set.

The ranking of models on the test set matched the ranking from cross-validation, which confirms that choices were not made based on the outcome.

The model **is not equally usable across the whole range**: in the middle eighty percent of salaries the typical error is between 17.7% and 32.2%, while for the seventeen respondents who reported less than a thousand dollars it misses by 1,199%.

## Workflow

| Notebook | What it does | Result |
| --- | --- | --- |
| `00_dataset_overview.ipynb` | describes the source, survey structure, sample composition, missing values and candidates for the target variable | `column_overview.csv`: an overview of all 170 columns |
| `01_target_variable.ipynb` | chooses the target variable and checks how it was derived | `ConvertedCompYearly`, modeled on a log scale |
| `02_data_cleaning.ipynb` | population, duplicates, structural errors, outliers, missing values, train/test split | `train.csv.gz` and `test.csv.gz`: 18,260 respondents, 129 columns |
| `03_feature_engineering.ipynb` | derives variables from multi-select columns and rankings, condenses country, checks for overlap | `train_features.csv.gz` and `test_features.csv.gz`: 429 columns |
| `04_modeling.ipynb` | linear regression with diagnostics, Ridge, Lasso and principal component regression, with model selection and evaluation on the test set | `test_predictions.csv.gz` and `model_coefficients.csv` |

Path through the data: **49,123 respondents → 34,106 in the population → 19,461 with reported salary → 18,260 after removing outliers.** Columns: **170 → 129 after cleaning → 429 after feature engineering**, or 709 model columns after encoding.

Every decision about the data was checked by measurement, and the findings are recorded in the notebooks themselves, together with the motivation, code, output and interpretation.

### Merged version

The notebooks were written **one after another, in the order above**, and each is a self-contained unit that can be read on its own. They were merged into a single document **at the end**, when everything else was done.

If it is more convenient to have everything in one place, there is **`report/final_report.ipynb`**: all five steps in one document, with continuous numbering throughout: **43 sections and 38 figures**. The analysis is the same as in the separate notebooks. The merge changed section and figure numbers and the references to them, changed wording that referred to separate notebooks ("in the previous part" instead of "in the previous notebook"), and added a title section at the beginning.

**Note:** the notebooks are large and cross-references between sections are numerous, so some reference may have unintentionally ended up wrong when the numbering was remapped. If something does not match, the separate notebooks in `notebooks/` are authoritative, since their numbering is the one the work was written in.

## Exported HTML versions

The `html_preview/` folder contains the same content exported to HTML, with all outputs, tables and figures, for reading in a browser without running Jupyter or installing dependencies:

| file | what it is |
| --- | --- |
| `00_dataset_overview.html` | dataset overview |
| `01_target_variable.html` | target variable |
| `02_data_cleaning.html` | cleaning and preparation |
| `03_feature_engineering.html` | deriving new variables |
| `04_modeling.html` | modeling |
| `final_report.html` | all five steps in one document |

## Repository structure

| Folder | Contents |
| --- | --- |
| `sandbox/` | Initial exploration of the dataset: the first, self-contained phase of the work (basic data overview, missing values, target distribution and an accompanying report). A closed unit, kept as a record of the starting analysis. |
| `data/raw/` | Raw data, as downloaded from the source. Contents are not versioned. |
| `data/processed/` | The cleaned and prepared dataset, plus the predictions and coefficients of the selected model. Versioned, so the results can be checked without rerunning anything. |
| `notebooks/` | Working Jupyter notebooks, one for each step of the work. |
| `report/` | `final_report.ipynb`: all five steps merged into one document, with unified section and figure numbering. |
| `html_preview/` | Exported HTML versions of all notebooks and the merged document, for reading without Jupyter. |
| `src/` | `data_loader.py`: downloading and loading the raw data. Everything else is done in the notebooks, because each step is tied to its explanation. |

## Running

Python 3.10 or newer is required.

```bash
# 1. Kreiranje i aktiviranje virtuelnog okruženja
python -m venv venv

# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

# 2. Instalacija zavisnosti
pip install -r requirements.txt
```

The notebooks are then started from the activated environment:

```bash
jupyter notebook
```

The notebooks are run **in order, from `00` to `04`**, because each one reads what the previous one wrote to `data/processed/`. The files in that folder are already in the repository, so each notebook can also be run on its own, without the previous ones.

## Data

Survey data © Stack Overflow, from the [Stack Overflow Developer Survey 2025](https://survey.stackoverflow.co/), licensed under the [Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/1-0/). The processed files in `data/processed/` are derived from it and are shared under the same license.

Raw data is not stored in the repository. It is downloaded from Kaggle on the first run and placed in `data/raw/`:

```python
from src.data_loader import load_raw

responses, schema = load_raw()
```

The download happens only once; every later run reads the local copy from `data/raw/`.

## Open issues

Findings and limitations are presented in the conclusions of each step; these are the ones that concern the work as a whole:

- **The sample is not a random sample of developers** but of those who filled in the survey and reported a salary, and reporting a salary depends on observed attributes. The model describes that population.
- **63 of the 423 coefficients are estimated from fewer than fifty respondents**, and the two strongest from two people each, so a coefficient's size should not be read without the number of respondents behind it.
- **Interactions were not tried**, and nonlinear models (trees and ensembles) are outside the scope of the course, so they are left as the first next step.
