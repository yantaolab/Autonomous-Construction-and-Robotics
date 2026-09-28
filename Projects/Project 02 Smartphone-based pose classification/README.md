# Assignment A2

## Smartphone Sensor-Based Posture Classification

Build a machine-learning pipeline that recognises a construction worker's posture from
smartphone sensor signals, then compare four models on it.

**A2 is one assignment, marked out of 100, worked on across two tutorials.** It is not
two assignments. You do Part A in the Week 4 tutorial and Part B in the Week 5 tutorial,
answering both in the **same** question document, `A2_Assignment_Questions_Sep_29,_2026.docx`.
The questions are numbered 1 to 11 straight through.

| | Part A | Part B |
|---|---|---|
| **Tutorial** | Week 4 | Week 5 |
| **Questions** | 1 – 6 | 7 – 11 |
| **Marks** | 55 | 45 |
| **Focus** | The full pipeline + a **Logistic Regression** baseline | **KNN, SVM, Random Forest** and a four-model comparison |
| **Notebook** | `Assignment_2_PartA_Week4_LogisticRegression_Sep_29,_2026.ipynb` | `Assignment_2_PartB_Week5_Model_Comparison_Sep_29,_2026.ipynb` |
| **Upload** | `A2_PartA_<YourName>.pdf` | `A2_<YourName>.pdf` |
| **Graded?** | **No** — progress record only | **Yes** — the one marked submission |

There are two notebooks only because a Colab session does not survive a week. There is
**one question document, one mark, and one submission that counts**: the complete
document, Parts A and B in one file, at the end of Week 5.

**The Week 4 upload is not graded.** It exists so the teaching team can see how far the
class got, and so you have a copy of your own work if Colab loses your session. No marks
are attached to it either way. Keep working in the same question document — if you start
a fresh one in Week 5, the 55 marks for Part A cannot be awarded.

### Why it is split this way

Part A ends with one number: the macro F1-score of a Logistic Regression model. Part B
trains three more flexible models on **exactly the same pipeline** and asks whether they
beat it.

That order is the point of the exercise. A Random Forest scoring 0.84 macro F1 means
nothing on its own — you cannot tell whether the forest earned it or whether the task
was easy enough that a straight line would have done as well. Measuring the simplest
model that can work, first, is what turns Part B's numbers into evidence.

That dependency is also why the two parts are one assignment. Part B's marks are not
awardable without Part A's baseline sitting in the same document.

---

## What you are building

An ergonomic assessment tool that works from a phone in the worker's pocket. Given
accelerometer, gravity and gyroscope signals, classify which of four postures the worker
is in:

| Label in data | Posture |
|---:|---|
| 1 | Standing |
| 2 | Walking |
| 5 | Bending |
| 8 | Squatting |

Bending and squatting are the postures that matter for ergonomic risk, so the point of
the exercise is not accuracy in the abstract — it is whether the model can find the
postures that would trigger an intervention on a real site.

## Why this matters

Manual ergonomic assessment needs an observer watching a worker. A phone the worker
already carries could do it continuously, across a whole site, with no observer. The
obstacle is whether the signal from a pocket is informative enough — which is exactly
what you are testing.

**Data source.** A 20-minute recording of a scaffolder moving steel bars, labelled from
synchronised video, containing a deliberate mix of standing, walking, bending and
squatting.

---

## Learning outcomes

### Part A (Week 4)

1. Inspect an annotated smartphone-sensor dataset and identify the posture labels.
2. Prepare features and labels for a supervised multi-class classification task.
3. Apply feature selection and explain why selected sensor features may help distinguish
   postures.
4. Build a multinomial Logistic Regression classifier inside a scaling pipeline.
5. Use a validation set for model selection and reserve a test set for final evaluation.
6. Evaluate a model using Accuracy, macro Precision, macro Recall, macro F1-score and a
   confusion matrix.
7. Explain why a simple baseline is measured before more flexible models are tried.

### Part B (Week 5)

1. Rebuild a fixed preprocessing and feature-selection pipeline so several models are
   compared on identical inputs.
2. Build KNN, SVM and Random Forest classifiers and state the key settings of each.
3. Explain which models need feature scaling and which do not, and why.
4. Compare four models using Accuracy, macro Precision, macro Recall, macro F1-score and
   confusion matrices.
5. Select a model using macro F1-score rather than Accuracy, and justify the choice
   against a baseline.
6. Propose a concrete improvement based on the per-class errors you observe.

---

## Files

| File | What it is |
|---|---|
| `A2_Assignment_Questions_Sep_29,_2026.docx` | **The question document.** Both parts, questions 1–11, 100 marks. Write your answers in here. |
| `Assignment_2_PartA_Week4_LogisticRegression_Sep_29,_2026.ipynb` | **Part A notebook.** Pipeline + Logistic Regression baseline. |
| `Assignment_2_PartB_Week5_Model_Comparison_Sep_29,_2026.ipynb` | **Part B notebook.** Same pipeline + KNN, SVM, Random Forest, comparison. |
| `Smartphone based method introduction Sep.28.pdf` | Lecture slides — background and method. |
| `An Ergonomic Risk Assessment Tool for Construction Workers with Smartphone in Pocket In-class Tutorial.pdf` | Tutorial walkthrough. |
| `preprocessed dataset 823.csv` | The dataset (also loaded automatically from GitHub — see below). |
| The `..._for_student_Sep_21,_2026_.ipynb` source notebook | Previous single-session version. Superseded; kept as the build source. |
| `build_week_notebooks.py` | Regenerates the two notebooks from the Sep 21 source. |
| `build_question_sheets.py` | Regenerates the question document. |
| `harvest_answer_facts.py`, `build_answer_key.py` | Instructor only — regenerate the answer key. |
| `run_notebook_check.py` | Runs a notebook's code cells outside Colab to check it still executes. |

Use the **latest dated version** of any file. Where a filename carries a date, the newer
date supersedes the older.

---

## The dataset

**46,499 rows × 14 columns** of raw sensor samples.

The notebook loads it **directly from GitHub** — you do not need to upload anything. The
local `preprocessed dataset 823.csv` is the same data, kept as a fallback if the GitHub
load fails.

**Sensor columns you will use:**

| Family | Columns |
|---|---|
| Accelerometer | `Accelerometer.xlsx_x`, `_y`, `_z` |
| Gravity | `Gravity_x`, `Gravity_y`, `Gravity_z` |
| Gyroscope | `Gyroscope_x`, `Gyroscope_y`, `Gyroscope_z` |

**Label column:** `Label_2`

**Columns that are not model inputs:** `Unnamed: 0`, `seconds_elapsed`, `time`,
`Real Time`. These are identifiers and timestamps. A timestamp can let a model recover
*when* a sample occurred and so guess the posture without learning anything about
movement — that is leakage, not learning.

**On the magnetometer.** Magnetometer channels are excluded because the steel
reinforcement on site strongly disturbs magnetic readings. They are already removed from
the provided CSV, so there is nothing for you to drop — but you should be able to say
*why* they are gone.

### Class distribution

| Posture | Samples | Share |
|---|---:|---:|
| Standing (1) | 5,404 | 11.6% |
| Walking (2) | 14,114 | 30.4% |
| Bending (5) | 2,840 | **6.1%** |
| Squatting (8) | 24,141 | **51.9%** |

**The data is imbalanced — about 8.5× more squatting than bending.** This one fact drives
several instructions below. A model that never predicts "bending" at all still scores
about 94% accuracy on the other three classes, which is why **accuracy is not an
acceptable basis for choosing your model**, and why the primary metric is macro
F1-score: it averages over the four classes equally, so failing on the rarest posture
cannot be hidden by succeeding on the commonest.

Note that bending is both the rarest class *and* one of the two postures that ergonomic
assessment exists to detect. All four models use `class_weight="balanced"` for this
reason — it weights each class inversely to its frequency, so a bending mistake costs
more than a squatting mistake.

---

## Requirements

Both parts:

- Use the prepared dataset provided for A2.
- Use the **stratified 60/20/20** train–validation–test split in the notebook.
- Fit models, the scaler **and feature selection** on the **training set only**.
- Use the **validation set** to review performance during development.
- Use the **test set only once**, for the final evaluation.
- Use **macro F1-score** as the primary metric.
- **Do not change any `random_state` value.** They are fixed so your numbers are
  reproducible and comparable with your classmates' — and, across the two parts, with
  your own.
- Export the completed notebook — code, outputs, figures and written answers all
  visible — as a PDF.

Part A additionally: train a multinomial Logistic Regression classifier inside a
`StandardScaler` pipeline, and record its test metrics for Part B.

Part B additionally: train KNN, SVM and Random Forest on the same features and split, and
compare all four models against the Part A baseline.

---

## How to run it

1. Open the part's `.ipynb` in **Google Colab**. The notebook imports
   `google.colab.files`, so it will not run unchanged on a local Jupyter.
2. Run the cells in order. The dataset loads from GitHub automatically.
3. Do not change the `random_state` values.

### What the notebook does for you

The pipeline is already written. Your job is to run it, read the output, and explain what
you see.

**Feature extraction.** Sensor data is a continuous time series, but these models need
one row per example. The notebook slides a window over the signal
(`window_size=5`, `step=10`) and computes summary features per window:

- acceleration and gyroscope **magnitude** (combines 3 axes into one scalar, so the
  feature does not depend on which way the phone points)
- **jerk** magnitude (rate of change of acceleration — captures sudden starts and stops)
- **statistics**: mean, standard deviation, min, max, skewness, kurtosis
- **frequency-domain**: energy and entropy
- **pitch and roll** derived from gravity (body orientation)
- **correlation between axes**

Each window's label is the **most common label inside it** (a majority vote), which
matters for windows that span a change of posture.

**Feature selection.** Recursive Feature Elimination (RFE) with a Random Forest
estimator, fitted on training data only, selects the **top 20** features.

### The models

| Part | Model | How it decides | Key settings | Scaled? |
|---|---|---|---|---|
| A | Logistic Regression | one linear boundary per class | `C=1.0`, `max_iter=2000`, `solver="lbfgs"`, `class_weight="balanced"` | **yes** |
| B | K-Nearest Neighbours | majority label among the 5 nearest training windows | `n_neighbors=5`, `weights="distance"`, Minkowski `p=2` | **yes** |
| B | Support Vector Machine | a curved boundary in a transformed space | RBF kernel, `C=10`, `gamma="scale"`, `class_weight="balanced"` | **yes** |
| B | Random Forest | a vote across 300 decision trees | 300 trees, unlimited depth, `class_weight="balanced"` | **no** |

Logistic Regression, KNN and SVM sit inside a `Pipeline` with `StandardScaler`, but for
two different reasons — worth understanding, because Part B asks about it:

- **KNN and SVM are distance-based.** Without scaling, a feature measured in hundreds
  (`fft_energy`) would dominate the distance calculation over a radian value under 3.2
  (`pitch_mean`), regardless of how informative it is. Scaling changes which points count
  as "near".
- **Logistic Regression penalises large coefficients** — that is what `C` controls.
  Unscaled, the penalty would fall almost entirely on the small-scale features.
- **Random Forest needs no scaling.** A tree splits one feature at a time on a threshold,
  and a threshold is unaffected by the units of any other feature.

Putting the scaler **inside** the pipeline is what keeps the split honest — it is refitted
on the training fold rather than on all the data.

### Why Logistic Regression is worth fitting even though it loses

Logistic Regression is the only model here that will tell you what it learned. It reports
one weight per feature per posture, and because the features were standardized those
weights are comparable to each other — a large positive weight means "a high value of
this feature pushes the prediction towards this posture".

Question 5 asks you to read that table. Nothing equivalent is available from KNN or from
an RBF-kernel SVM.

---

## What you submit

Answer every question in the question document, then export as PDF.

| Part | # | What is assessed | Marks |
|---|---|---|---:|
| A | 1 | Objectives and context — four classes, the objective, the problem type | 3 |
| | 2 | Dataset inspection — shape, dtypes, label column, class distribution | 8 |
| | 3 | Feature selection — top-20 list and explanations for **three** features from three families | 12 |
| | 4 | Data preparation — split sizes, plus notes on leakage | 8 |
| | 5 | Logistic Regression baseline — pipeline, validation metrics, confusion matrix, coefficient reading | 14 |
| | 6 | Baseline test score — the four test metrics and an interpretation | 10 |
| | | **Part A subtotal** | **55** |
| B | 7 | Pipeline reproduction — split sizes, baseline reproduces | 5 |
| | 8 | KNN — pipeline, validation metrics, confusion matrix, settings | 8 |
| | 9 | SVM and Random Forest — both models, validation results, settings, the scaling question | 12 |
| | 10 | Four-model comparison — table, plot, best model justified on macro F1, gain over baseline | 13 |
| | 11 | Improvement proposal — a named confusion and a mechanism | 7 |
| | | **Part B subtotal** | **45** |
| | | **Total** | **100** |

Part A carries more marks because it carries the whole pipeline — loading, feature
extraction, selection, the split, and the one model everything else is judged against.
Part B adds three models to a pipeline that already exists.

### The written answers, specifically

**Dataset inspection.** Report rows and columns, the label column name, the main sensor
variables, the class distribution, and whether the data is balanced. Say what the
imbalance *implies*, not just that it exists.

**Data preparation.** Report samples in each split, then explain in 2–4 sentences:
1. Why stratified splitting is used.
2. Why feature selection and scaling must be fitted on training data only.
3. Why the test set is reserved for final evaluation.

For (1), connect it to the class distribution above — with bending at 6% of the data, a
non-stratified split can leave a subset with very few bending samples, making the metric
for that class mostly noise.

**Feature interpretation.** Pick three selected features **from different feature
families** and explain each with this chain:

> **sensor feature → body movement or posture → value for classification**

Good answers name the postures being separated. "Jerk standard deviation is high" is not
an answer; "walking produces repeated heel strikes, so jerk variability is higher than in
standing, which separates the two moving classes from the two static ones" is.

**Model comparison (Q10).** Fill in the four-model table, insert the plot, name the
best model on **macro F1-score**, and justify it in 2–3 sentences using the test metrics
and the confusion matrix. State the **gain over the baseline**, and say whether that gain
justifies the more complex model — one that is harder to explain and slower to run has to
earn its cost.

**Do not justify your choice with accuracy alone.** See the class distribution above for
why.

**Improvement proposal (Q11).** Find the largest off-diagonal cell in your best
model's confusion matrix and target *that* error. Name the two postures and the count,
say what you would change, and say why that change addresses that specific error. "Use a
deep learning model" is not an answer.

---

## Submission

Export the notebook as PDF with all code, outputs, figures and written answers visible.

| When | What you upload | Filename | Graded? |
|---|---|---|---|
| End of Week 4 | Part A only | `A2_PartA_<YourName>.pdf` | **No** — progress record |
| End of Week 5 | The complete document, Parts A and B | `A2_<YourName>.pdf` | **Yes** — out of 100 |

Before you submit the final version, check that:

- [ ] Every cell has been run, in order, and its output is visible.
- [ ] **Part A answers are still present** in the final document.
- [ ] The class-distribution table or chart appears.
- [ ] The three split sizes are reported.
- [ ] The 20 selected features are listed.
- [ ] Three features are explained, from three different families.
- [ ] Validation metrics and confusion matrices appear for every model.
- [ ] The coefficient table and the Logistic Regression **test** metrics.
- [ ] The four-model comparison table and plot, with the baseline line visible.
- [ ] Your best-model choice is stated and justified on macro F1-score.

**Keep your Part A test metrics.** Question 7 asks you to reproduce them.

---

## Common mistakes

| Mistake | Why it costs marks |
|---|---|
| Treating the two tutorials as two assignments | There is one mark out of 100 and one graded submission. A Week 5 file containing only Part B loses the 55 Part A marks. |
| Assuming the Week 4 upload was the assignment | It was a progress record and carried no marks. The assignment is not submitted until the end of Week 5. |
| Picking the model with the highest accuracy | The imbalance makes accuracy misleading. Macro F1 is the stated criterion. |
| Reporting a Part B score without the baseline | A score with nothing to compare it against is not a result. |
| Changing a `random_state` between the two parts | Your Part B comparison no longer lines up with your Part A baseline, and neither lines up with anyone else's. |
| Fitting the scaler or RFE on all data before splitting | Test-set information leaks into training; your reported score is no longer an estimate of real performance. |
| Reporting test metrics during development | The test set is a one-time measurement. Using it to choose between models turns it into a validation set. |
| Wrapping Random Forest in a `StandardScaler` | Not wrong, but you should be able to say that it makes no difference — and why. |
| Explaining a feature without naming a posture | The question asks why it *distinguishes the four postures*, not what it measures. |
| Three features from the same family | The question requires different families. Three statistical features is one family. |
| An improvement proposal with no named error | The question asks you to target a specific confusion, not to improve performance in general. |
| Submitting a PDF with unrun cells | Outputs and figures carry marks; empty cells score zero. |

---

## For instructors

The build scripts regenerate the materials and are not for students:

```bash
python build_week_notebooks.py    # the two notebooks, from the Sep 21 source
python build_question_sheets.py   # the single question document
python harvest_answer_facts.py    # runs Part B, dumps every number to answer_key_facts.json
python build_answer_key.py        # the answer key and marking scheme, from that JSON
python run_notebook_check.py "Assignment_2_PartA_Week4_LogisticRegression_Sep_29,_2026.ipynb"
```

`run_notebook_check.py` executes a notebook's code cells in one namespace outside Colab —
it stubs `google.colab` and redirects the GitHub URL to the local CSV — so a broken cell
is caught before a tutorial rather than during one. Both notebooks pass.

**The answer key is generated, not written.** `harvest_answer_facts.py` executes the Part B
notebook and writes every metric, confusion matrix and coefficient to
`answer_key_facts.json`; `build_answer_key.py` renders the key from that file. So the model
answers cannot drift from what the notebook actually prints. Run the harvest first if you
change anything in the pipeline. The key (`A2_ANSWER_KEY_INSTRUCTOR_ONLY.docx`) is marked
instructor-only on its title page — do not post it with the student materials.

The mark split lives in `build_question_sheets.py` as `PART_A_MARKS` and `PART_B_MARKS`;
the question stems, the mark table and the total are all generated from those two lists,
so they cannot drift apart. If you change a weighting, change it there and rebuild — and
update the two flow tables in `build_week_notebooks.py` to match.

**Reference results** (test set, `random_state` as shipped). Students should land near
these; large deviations mean something in the pipeline was changed.

| Model | Test accuracy | Test macro F1 |
|---|---:|---:|
| Logistic Regression | 0.843 | 0.776 |
| KNN | 0.874 | 0.818 |
| SVM | 0.860 | 0.811 |
| Random Forest | **0.885** | **0.837** |

Random Forest wins by **+0.061 macro F1** over the baseline. That margin is the discussion
Q10 is built around: real, but modest for a model with 300 trees and no readable
coefficients.

**Two places the questions' wording runs ahead of the data** — both are written up in full
on the last page of the answer key, read it before marking:

1. Bending is the rarest class but **not** the weakest. Standing has the lowest per-class
   F1 in all four models (baseline 0.653 vs 0.709 for bending). `class_weight="balanced"`
   has lifted the rare class above the frequent-but-ambiguous one. Q5 and Q6 are worded
   around bending, so accept either class as "worst" when the confusion matrix is cited.
2. The dominant error is **Standing↔Walking**, not a bending confusion: the largest
   off-diagonal cells are 32 (walking predicted standing) and 26 (the reverse). Expect
   correct Q11 answers to be about window length or gait periodicity.

Note for marking: `sklearn` ≥ 1.7 removed the `multi_class` parameter from
`LogisticRegression`. The notebook omits it — `lbfgs` is multinomial by default — so it
runs on both older and current versions.

**On filenames.** These materials are shared between two courses, so nothing generated
here carries a course code — the question document, the answer key, the two notebooks and
the submission filenames are all named from `A2` alone. Add your own course prefix when
you post them to a specific course's page, and change it in one place if you do: the `OUT`
constant in each build script.

One inherited inconsistency is left alone: the Sep 21 source notebook's markdown still
mentions dropping magnetometer columns that are not in the CSV.
