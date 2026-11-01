# Biomechanical Simulation and Exoskeleton Assistance with OpenSim

This teaching notebook introduces the OpenSim Python API through a comparison of a musculoskeletal model with and without a passive assistive spring. It uses the `gait2392` model and a prescribed crouch motion, adds a point-to-point spring between the torso and pelvis centers of mass, and compares joint moments and muscle forces between the two conditions.

The main notebook is [colab/4210_code.ipynb](colab/4210_code.ipynb). Google Colab is the intended execution environment.

## What the notebook demonstrates

- Loading, modifying, and saving an OpenSim model.
- Connecting a `PointToPointSpring` to model bodies using attachment points in their local frames.
- Running inverse dynamics to calculate the generalized forces and moments required by prescribed kinematics.
- Running static optimization to estimate individual muscle forces at each time point.
- Reading OpenSim storage files and comparing baseline and assisted results with Matplotlib.

The example plots `lumbar_extension_moment` and the left erector spinae muscle force (`ercspn_l`). The joint-moment plotting function accepts another moment-column label, and the muscle-force plotting function accepts another muscle name.

## Required notebook and input data

All files needed for the example are supplied in `colab/`:

| File | Purpose |
| --- | --- |
| `4210_code.ipynb` | Notebook containing the model modification, analyses, and plots. |
| `gait2392_simbody.osim` | OpenSim musculoskeletal model, including bodies, joints, and muscles. |
| `crouch4.mot` | Prescribed coordinate trajectories for the crouch-motion example. |

The `.mot` file supplies the kinematics directly; the notebook does not perform inverse kinematics from marker measurements. It contains a time column and coordinate columns, with rotational values identified as degrees in its header.

### Optional data for external loads

The supplied example passes `None` for external loads. The following files at the project root are additional walking-trial data and are **not required** to run the crouch example:

| File | Purpose |
| --- | --- |
| `subject01_walk1_grf.xml` | Defines the bodies, reference frames, and data-column identifiers used to apply ground reaction forces. |
| `subject01_walk1_grf.mot` | Ground reaction force, application-point, and torque data referenced by the XML file. |
| `subject01_walk1.trc` | Marker trajectories for the walking trial; not read by this notebook. |

For an analysis with external loads, provide the XML path to the analysis functions and make its referenced data files accessible. Use kinematics and loads from the same trial with compatible timing and reference frames; the walking loads should not simply be substituted into the crouch example.

## Run in Google Colab

1. Open Google Colab and upload `colab/4210_code.ipynb` using **File > Upload notebook**.
2. In Colab's **Files** panel, upload `gait2392_simbody.osim` and `crouch4.mot` from `colab/`. Place both in the runtime's current working directory, normally `/content`.
3. Run the first code cell to install OpenSim:

   ```python
   !pip install opensim
   ```

4. Run the remaining cells in order. They define the analysis functions, run inverse dynamics for both models, run static optimization for both models, and display the comparison plots.
5. Download any outputs you want to retain from the Files panel before the runtime ends. Files uploaded to or generated in the runtime are temporary.

The notebook imports `opensim`, `numpy`, and `matplotlib`. If a runtime reports a missing plotting dependency, install it in a code cell:

```python
!pip install numpy matplotlib
```

For local execution, use a Python environment with those dependencies and set the working directory to `colab/`. Skip the Colab installation cell if OpenSim is already installed.

## Example settings and workflow

The baseline analysis uses the original model. The assisted analysis uses a saved copy containing one torso–pelvis spring with stiffness **5000 N/m** and rest length **0.5 m**. Both analyses use the same motion and omit external loads.

Inverse dynamics uses a **4 Hz** coordinate filter by default. Static optimization explicitly filters the kinematics at **2 Hz** before constructing the states supplied to `AnalyzeTool`. Its setup also retains a 4 Hz cutoff setting; the explicit Storage filtering prepares the supplied state trajectories.

Static optimization takes the model and motion as inputs and computes the required dynamics internally; it does not read the inverse-dynamics `.sto` files produced earlier in the notebook.

## Generated outputs

Paths below are relative to the runtime working directory:

| Output | Contents |
| --- | --- |
| `model_with_spring.osim` | Model containing the torso–pelvis spring. |
| `id_results.sto` | Baseline inverse-dynamics generalized forces and moments. |
| `id_results_exo.sto` | Inverse-dynamics results with the spring. |
| `baseline_so_results/` | Static-optimization outputs for the original model. |
| `spring_so_results/` | Static-optimization outputs for the assisted model. |

The muscle-force plot reads `static_optimization_static_optimization_force.sto` from each static-optimization directory. Static optimization also writes activation results. Joint moments are plotted in N·m and muscle forces in N, against time in seconds. Rerunning the notebook can overwrite results at these paths.

## Interpreting the results

The motion is prescribed in both conditions. The comparison therefore shows how a spring changes the forces and moments required for that same motion, rather than predicting how a person would change their movement when wearing an exoskeleton.

The example omits external loads and is intended to illustrate the API and the model comparison. A quantitative analysis of measured movement requires appropriate external loads and model preparation. Check OpenSim's optimization messages: a completed tool run or an output file alone does not establish that every frame converged successfully. Reported constraint violations or actuator saturation should be resolved before interpreting muscle-force estimates.
