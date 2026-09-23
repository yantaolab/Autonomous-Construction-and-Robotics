# DISC5105 Week 3 — Assignment A2

## Smartphone Sensor-Based Posture Classification

Build and compare three machine-learning models that recognise a construction
worker's posture from smartphone sensor signals.

**This is an in-class assignment.** You complete it during the tutorial and
submit a PDF before you leave.

---

## What you are building

An ergonomic assessment tool that works from a phone in the worker's pocket.
Given accelerometer, gravity and gyroscope signals, classify which of four
postures the worker is in:

| Label in data | Posture |
|---:|---|
| 1 | Standing |
| 2 | Walking |
| 5 | Bending |
| 8 | Squatting |

Bending and squatting are the postures that matter for ergonomic risk, so the
point of the exercise is not accuracy in the abstract — it is whether the model
can find the postures that would trigger an intervention on a real site.

## Why this matters

Manual ergonomic assessment needs an observer watching a worker. A phone the
worker already carries could do it continuously, across a whole site, with no
observer. The obstacle is whether the signal from a pocket is informative
enough — which is exactly what you are testing.

**Data source.** A 20-minute recording of a scaffolder moving steel bars,
labelled from synchronised video, containing a deliberate mix of standing,
walking, bending and squatting.

---

## Learning outcomes

By the end of this assignment you should be able to:

1. Inspect an annotated smartphone-sensor dataset and identify the posture labels.
2. Prepare features and labels for a supervised multi-class classification task.
3. Apply feature selection and explain why selected sensor features may help
   distinguish postures.
4. Build KNN, SVM and Random Forest classification models.
5. Use a validation set for model selection and reserve a test set for final
   evaluation.
6. Evaluate and compare models using Accuracy, macro Precision, macro Recall,
   macro F1-score and confusion matrices.

---

## Files

| File | What it is |
|---|---|
| `CIVL4210_Assignment_2_for_student_Aug_30,_2026.ipynb` | The notebook you complete. Open in Google Colab. |
| `DISC5105_Week3_A2_Assignment_Questions.docx` | The question sheet you write your answers into. |
| `preprocessed dataset 823.csv` | The dataset. Download from Canvas and upload into Colab. |
| `Smartphone based method introduction Sep.14.pptx` | Lecture slides — background and method. |

Use the **latest dated version** of any file. Where a filename carries a date,
the newer date supersedes the older.

---

## The dataset

`preprocessed dataset 823.csv` — **46,499 rows × 14 columns** of raw sensor
samples.

**Sensor columns you will use:**

| Family | Columns |
|---|---|
| Accelerometer | `Accelerometer.xlsx_x`, `_y`, `_z` |
| Gravity | `Gravity_x`, `Gravity_y`, `Gravity_z` |
| Gyroscope | `Gyroscope_x`, `Gyroscope_y`, `Gyroscope_z` |

**Label column:** `Label_2`

**Columns you must NOT feed the model:** `Unnamed: 0`, `seconds_elapsed`,
`time`, `Real Time`. These are identifiers and timestamps. A timestamp can let
a model recover *when* a sample occurred and so guess the posture without
learning anything about movement — that is leakage, not learning.

**On the magnetometer.** Magnetometer channels are excluded because the steel
reinforcement on site strongly disturbs magnetic readings. They are already
removed from the provided CSV, so there is nothing for you to drop — but you
should be able to say *why* they are gone.

### Class distribution

| Posture | Samples | Share |
|---|---:|---:|
| Standing (1) | 5,404 | 11.6% |
| Walking (2) | 14,114 | 30.4% |
| Bending (5) | 2,840 | **6.1%** |
| Squatting (8) | 24,141 | **51.9%** |

**The data is imbalanced — about 8.5× more squatting than bending.** This one
fact drives several instructions below. A model that never predicts "bending"
at all still scores about 94% accuracy on the other three classes, which is why
**accuracy is not an acceptable basis for choosing your model**, and why the
primary metric is macro F1-score: it averages over the four classes equally, so
failing on the rarest posture cannot be hidden by succeeding on the commonest.

Note that bending is both the rarest class *and* one of the two postures that
ergonomic assessment exists to detect.

---

## Requirements

- Use the prepared dataset provided for A2.
- Use the **stratified 60/20/20** train–validation–test split in the notebook.
- Fit models **and feature selection** on the **training set only**.
- Use the **validation set** to review performance during development.
- Use the **test set only once**, for the final comparison.
- Train and compare all three models:
  - K-Nearest Neighbours (KNN)
  - Support Vector Machine (SVM)
  - Random Forest
- Use **macro F1-score** as the primary metric for selecting the best model.
- Export the completed notebook — code, outputs, figures and written answers
  all visible — as a PDF.

---

## How to run it

1. Open the `.ipynb` in **Google Colab**. The notebook uses
   `google.colab.files`, so it will not run unchanged on a local Jupyter.
2. Download `preprocessed dataset 823.csv` from Canvas.
3. Run the cells in order. The upload cell will prompt you for the CSV.
4. Do not change the `random_state` values. They are fixed so your numbers are
   reproducible and comparable with your classmates'.

### What the notebook does for you

The pipeline is already written. Your job is to run it, read the output, and
explain what you see.

**Step 3 — feature extraction.** Sensor data is a continuous time series, but
KNN/SVM/RF need one row per example. The notebook slides a window over the
signal and computes summary features per window:

- acceleration and gyroscope **magnitude** (combines 3 axes into one scalar, so
  the feature does not depend on which way the phone points)
- **jerk** magnitude (rate of change of acceleration — captures sudden
  starts and stops)
- **statistics**: mean, standard deviation, min, max, skewness, kurtosis
- **frequency-domain**: energy and entropy
- **pitch and roll** derived from gravity (body orientation)
- **correlation between axes**

**Step 3 — feature selection.** Recursive Feature Elimination (RFE) with a
Random Forest estimator, fitted on training data only, selects the **top 20**
features.

**Steps 5–6 — the three models**, with the settings you must be able to state:

| Model | Key settings |
|---|---|
| KNN | `StandardScaler` → `n_neighbors=5`, `weights="distance"`, Minkowski `p=2` |
| SVM | `StandardScaler` → RBF kernel, `C=10`, `gamma="scale"`, `class_weight="balanced"` |
| Random Forest | 300 trees, unlimited depth, `class_weight="balanced"` |

KNN and SVM sit inside a `Pipeline` with `StandardScaler` because both are
distance-based: without scaling, a feature that happens to be measured in
larger numbers would dominate the distance calculation regardless of how
informative it is. Random Forest splits one feature at a time and so does not
need scaling.

Putting the scaler **inside** the pipeline is what keeps the split honest — it
is refitted on the training fold rather than on all the data.

---

## What you submit

Answer every part in the question sheet, then export as PDF.

| # | Part | Marks |
|---|---|---:|
| 1 | Objectives and context — identify the four classes, state the objective | 5 |
| 2 | Dataset inspection — shape, dtypes, label column, class distribution | 15 |
| 3 | Data preparation — split sizes, plus notes on leakage | 15 |
| 4 | KNN baseline — pipeline, validation metrics, confusion matrix, interpretation | 15 |
| 5 | Feature selection — top-20 list and explanations for **at least three** features | 20 |
| 6 | SVM and Random Forest — models, validation results, stated settings | 15 |
| 7 | Final test comparison — table, plot, best model justified on macro F1 | 15 |
|   | **Total** | **100** |

> The question sheet says "at least two" features in the feature-interpretation
> question; the notebook and the 20-mark row above both say **three**. Answer
> **three** — the mark scheme is written for three, and the response table has
> three rows.

### The written answers, specifically

**Q2 — dataset inspection.** Report rows and columns, the label column name,
the main sensor variables, the class distribution, and whether the data is
balanced. Say what the imbalance implies, not just that it exists.

**Q3 — data preparation.** Report samples in each split, then explain in 2–4
sentences:
1. Why stratified splitting is used.
2. Why feature selection and scaling must be fitted on training data only.
3. Why the test set is reserved for final evaluation.

For (1), connect it to the class distribution above — with bending at 6% of the
data, a non-stratified split can leave a subset with very few bending samples,
making the metric for that class mostly noise.

**Q4 — feature interpretation.** Pick three selected features **from different
feature families** and explain each with this chain:

> **sensor feature → body movement or posture → value for classification**

Good answers name the postures being separated. "Jerk standard deviation is
high" is not an answer; "walking produces repeated heel strikes, so jerk
variability is higher than in standing, which separates the two moving classes
from the two static ones" is.

**Q7 — model comparison.** Fill in the comparison table, insert the plot, name
the best model on **macro F1-score**, and justify it in 2–3 sentences using the
test metrics and the confusion matrix. State a per-class observation: which
posture does your best model handle worst, and is that the rare class?

**Do not justify your choice with accuracy alone.** See the class distribution
above for why.

---

## Submission

Export the notebook as PDF with all code, outputs, figures and written answers
visible, and submit before leaving the tutorial.

**Filename:** `DISC5105_Week3_A2_<YourName>.pdf`

Before you submit, check that:

- [ ] Every cell has been run, in order, and its output is visible.
- [ ] The class-distribution table or chart appears.
- [ ] The three split sizes are reported.
- [ ] The 20 selected features are listed.
- [ ] Validation metrics and confusion matrices appear for all three models.
- [ ] The test comparison table and plot appear.
- [ ] Your best-model choice is stated and justified on macro F1-score.
- [ ] Three features are explained, from three different families.

---

## Common mistakes

| Mistake | Why it costs marks |
|---|---|
| Picking the model with the highest accuracy | The imbalance makes accuracy misleading. Macro F1 is the stated criterion. |
| Fitting the scaler or RFE on all data before splitting | Test-set information leaks into training; your reported score is no longer an estimate of real performance. |
| Reporting test metrics during development | The test set is a one-time measurement. Using it to choose between models turns it into a validation set. |
| Feeding `time` / `Real Time` / `Unnamed: 0` to the model | These are identifiers, not movement. A high score from them means nothing. |
| Explaining a feature without naming a posture | The question asks why it *distinguishes the four postures*, not what it measures. |
| Three features from the same family | The question requires different families. Three statistical features is one family. |
| Submitting a PDF with unrun cells | Outputs and figures carry marks; empty cells score zero. |
