# Human–Robot Handover with Reinforcement Learning

In this project, a robot arm hands a hammer to a person in simulation. You read observations, write a reward function, train a reinforcement learning policy, and evaluate it. Everything runs in one Jupyter notebook on your own laptop.

> **After downloading, rename this project folder to `CourseProj`.** The folder name on GitHub has spaces and a non-English dash "–". On Windows, MuJoCo cannot open files whose path has non-English characters, and spaces in the path make the `cd` command fail unless it is quoted. The rest of this guide calls the folder `CourseProj`.

**Contents**

- [What is in this folder](#what-is-in-this-folder)
- [Setup](#setup)
  1. [Install Miniconda](#1-install-miniconda)
  2. [Open a new terminal](#2-open-a-new-terminal)
  3. [Go to this folder](#3-go-to-this-folder)
  4. [Create the environment](#4-create-the-environment)
  5. [Install the packages](#5-install-the-packages)
  6. [Open the notebook](#6-open-the-notebook)
- [Troubleshooting](#troubleshooting)
- [Grading](#grading-100-points)

---

## What is in this folder

| File | What it is |
|---|---|
| `hri_handover_tutorial.ipynb` | The notebook you work in and submit |
| `requirements.txt` | Packages for Apple Silicon Mac, Windows, and Linux |
| `requirements-intel-mac.txt` | Packages for Intel Mac only |
| `mujoco/` | The local robosuite with the handover task. Do not change it |
| `CourseProject.pdf` | Tutorial slides |

You need one Python 3.11 environment named `courseproj`. Do not install these packages into the system Python.

---

## Setup

### 1. Install Miniconda

Download the **Miniconda** installer (not the full Anaconda Distribution) from:

https://docs.conda.io/en/latest/miniconda.html

Pick the installer that matches your computer:

| Your computer | Installer to download |
|---|---|
| Mac with an Apple chip (M1, M2, M3, ...) | macOS Apple Silicon (arm64) |
| Mac with an Intel chip | macOS Intel (x86_64) |
| Windows, Intel or AMD (most laptops) | Windows 64-bit (x86_64) graphical installer |
| Windows ARM (Qualcomm) | Windows 64-bit (arm64) graphical installer |
| Linux | Linux x86_64 |

To see which chip a Mac has, open the Apple menu and choose **About This Mac**.

**Windows:** double-click the downloaded `.exe`, then:

1. Review the license terms and click **I Agree**.
2. Choose **Just Me**. Keep the default install path.
3. Leave the advanced options at their defaults. Do **not** check "Add Miniconda to PATH".
4. Click **Install**. When it finishes, click **Finish**.

**Mac and Linux:** run the installer and say yes when it asks to run `conda init`.

When the installer finishes, quit it. Do not type the later commands into the installer window.

### 2. Open a new terminal

The terminal is a text window where you type commands. Open a **new** one after Miniconda is installed. Do not reuse a terminal that was already open.

| System | How to open it |
|---|---|
| Mac | Press <kbd>Command</kbd> + <kbd>Space</kbd>, type `Terminal`, press <kbd>Return</kbd> |
| Windows | Press the Windows key, type `Anaconda Prompt`, and open **Anaconda Prompt**, not Command Prompt and not PowerShell |
| Linux | Press <kbd>Ctrl</kbd> + <kbd>Alt</kbd> + <kbd>T</kbd>. If nothing opens, search the app menu for Terminal |

Check that conda works:

```bash
conda --version
```

It should print a version, such as `conda 24.11.0`. If it says the command is not found, close this window and open the terminal again the same way. If you already had Miniconda or Miniforge and this command works, continue.

### 3. Go to this folder

If you downloaded the whole repository, the project folder is inside `Projects`, and it is the only folder you need. Make sure you have renamed it to `CourseProj` (see the note at the top).

You can keep the `CourseProj` folder anywhere. Copy its path, then type `cd` followed by that path:

```bash
cd pathname
```

On Windows, type `cd /d` instead of `cd` so that it also works when the folder is on another drive.

Mac example:

```bash
cd /Users/tong/Desktop/CourseProj
```

Windows example:

```bat
cd /d C:\Users\tong\Desktop\CourseProj
```

> **Windows:** the whole path must have only English letters and numbers. MuJoCo cannot open files whose path has Chinese or other non-English characters.

Check that you are in the right folder. You should see `hri_handover_tutorial.ipynb`, `requirements.txt`, and `mujoco`:

```bash
ls
```

On Windows, use `dir` instead of `ls`.

### 4. Create the environment

These two commands are the same on Mac, Windows, and Linux:

```bash
conda create -n courseproj python=3.11
conda activate courseproj
```

While `conda create` runs:

- It may ask you to accept the Terms of Service more than once (often three times). Each time, type `a` and press <kbd>Enter</kbd>.
- When it asks `Proceed ([y]/n)?`, type `y` and press <kbd>Enter</kbd>.

The prompt should now start with `(courseproj)`.

> Every time you open a new terminal later, run `conda activate courseproj` again before you open the notebook.

### 5. Install the packages

Run this from the `CourseProj` folder, with `(courseproj)` shown in the prompt. It also installs the robosuite in `mujoco/robosuite`, and can take several minutes.

**Apple Silicon Mac, Windows, and Linux:**

```bash
pip install -r requirements.txt
```

**Intel Mac** (About This Mac says Intel). PyTorch 2.11 has no Intel Mac build, so use the other file:

```bash
pip install -r requirements-intel-mac.txt
```

If downloads are very slow (common in mainland China with the official PyPI), press <kbd>Ctrl</kbd> + <kbd>C</kbd> and run the same command with the Tsinghua mirror:

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

Intel Mac with the mirror:

```bash
pip install -r requirements-intel-mac.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

> If you later move or rename this folder, activate `courseproj` and run the same `pip install` line again from the new location.

### 6. Open the notebook

Register the environment as a notebook kernel, then open the notebook:

```bash
python -m ipykernel install --user --name courseproj --display-name courseproj
jupyter notebook hri_handover_tutorial.ipynb
```

Choose the `courseproj` kernel:

- **Jupyter:** Kernel → Change kernel → `courseproj`.
- **VS Code / Cursor:** pick the `courseproj` kernel at the top right. It must be `courseproj`, not "Python 3" or base.

Check that everything works:

1. Run the first code cell in Part 0. It should print the robosuite and numpy versions.
2. Run Part 1. It should print `Environment created successfully!` and a list of cameras.

Warnings about a private macro file, `robosuite_models`, or `mink` are harmless.

> **Training takes a while.** The notebook trains for `TOTAL_TIMESTEPS = 120000`. On the Mac we tested, this took about 75 minutes. Keep the computer plugged in and awake until `model.learn` finishes.

---

## Troubleshooting

**Windows: unzipping the download fails with "path too long" or "file not found"**
Windows limits a full path to 260 characters, and the download was unzipped into a folder that is too deep. Unzip it into a folder with a shorter path, then follow [step 3](#3-go-to-this-folder).

**`conda` is not found**
You are using an old window, or on Windows you opened Command Prompt. Close it and follow [step 2](#2-open-a-new-terminal) again.

**`pip` fails on an Intel Mac**
Use `requirements-intel-mac.txt` instead of `requirements.txt` (see [step 5](#5-install-the-packages)).

**`pip` fails on `opencv-python` on a Mac**
Your macOS is too old. Update macOS (Apple chip: 13 or newer; Intel: 12 or newer), then run `pip` again.

**Windows: the first code cell fails with `WinError 126` or `c10.dll`**
Install the Microsoft Visual C++ Redistributable (x64) from https://aka.ms/vs/17/release/vc_redist.x64.exe, restart the computer, then open the notebook again.

**Windows: Part 1 fails with an OpenGL or `gladLoadGL` error**
Run the notebook on the computer itself, not through Remote Desktop, and update the graphics driver.

**The notebook cannot import robosuite**
The kernel is not `courseproj`, or `pip install` was not run from this folder.

**Linux: Part 1 fails with an OpenGL or EGL error**
Install the OpenGL libraries, then restart the kernel:

```bash
sudo apt install libegl1 libgl1
```

On a machine with no GPU, install OSMesa instead:

```bash
sudo apt install libosmesa6
```

Then, in the first code cell, add this line right after `import os`:

```python
os.environ["MUJOCO_GL"] = "osmesa"
```

Restart the kernel and run again from the first cell.

---

## Grading (100 points)

- Write only in the designated answer areas in the notebook. Changing anything outside those areas gives 0 for the affected question.
- Submit only the `.ipynb`, saved with outputs after Part 6 finishes. Missing required outputs gives 0 for the corresponding question.

| Question | Points | What is graded |
|---|---|---|
| Q1 Robot observations | 6 | `robot0_joint_vel`, `robot0_eef_quat`, `robot0_gripper_qpos`, 2 each |
| Q1 Object observations | 8 | `head_pos`, `palm_pos`, `hammer_quat`, `hammer_vel`, 2 each |
| Q2 Camera images | 12 | `birdview`, `robot0_eye_in_hand`, `extra_side_plusx`, `extra_palm_close`, 3 each. Use `[::-1]` to flip the images; an upside-down image loses 1 of its 3 points |
| Q3 Info keys | 8 | `hammer_speed`, `hold_steps`, `body_contact`, `hand_contact`, 2 each |
| Q4 Random episode | 8 | Print all eight requested info keys (3), and explain each in one sentence (5) |
| Q5.1 Score shapes | 2 | Plot `-d`, `-d**2`, `-d**3` and the red distance line on one figure |
| Q5.2 Your score | 6 | The one-line score (4), and one sentence on how the two plotted lines change relative to each other (2) |
| Q6 `custom_reward` | 50 | The final stage reached in evaluation (see below) |

The eight keys in Q4 are `success`, `failure`, `body_contact`, `hand_contact`, `handle_pos`, `ellipsoid_pos`, `hammer_speed`, and `hold_steps`.

### Question 6: `custom_reward`

Only edit the reward answer area. Do not use `obs`, and keep each reward term zero or positive. There is no required formula to copy: the stage your trained policy reaches in evaluation decides the score.

Each evaluation episode is graded on its **last step only**. Entering a target region earlier and then leaving it does not count. `distance` is measured from the handle center to the palm-sphere center.

| Stage | Last-step check | Points | Total |
|---|---|---|---|
| 0 | None of the below, or `info["failure"]` on the last step | 0 | 0 / 50 |
| 1 | `distance <= 0.05` m | +20 | 20 / 50 |
| 2 | `distance <= 0.02` m. Position only, not speed | +15 | 35 / 50 |
| 3 | `hold_steps >= 60`: about 3 consecutive seconds within 2 cm, at a handle speed of at most 5 mm/s | +15 | 50 / 50 |

For Stage 3, leaving the 2 cm region or going faster than 5 mm/s resets the hold counter to 0. Touching the person, including the hand, ends the episode as a failure, and that episode is stage 0.

**How the score is read:**

- Part 6.2 evaluates 10 episodes, using reset seeds 0 through 9 and deterministic actions.
- The printed `Best final stage` is the highest final stage among those 10 episodes, and it decides your Q6 score. A failed episode does not cancel a higher stage from another episode.
- Evaluation loads `saved_models/handover_best_sac/best_model.zip` when it exists; otherwise it loads `saved_models/sac_handover_notebook.zip`.
- The separate video episode in Part 6.3 is not the grading result. Use `Best final stage` from Part 6.2.
