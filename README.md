# DR-MulFea-26

Python 3 implementation of the DR-MulFea-26 motion-reproduction experiment.

## Repository Layout

| Path | Purpose |
| --- | --- |
| `RUN/` | Experiment scripts and supporting Python modules. |
| `BHV/` | Generated behavioural data. |
| `EEG/` | EEG data saved by the experimenter. |
| `EYE/` | Generated EyeLink recordings. |
| `LOG/` | Generated PsychoPy logs. |
| `LIB/` | Platform-specific EyeLink conversion and USB2LPT driver utilities. |

Generated data and the local `.venv` environment are excluded from Git. Changes to the source or configuration should be recorded in [CHANGES.md](CHANGES.md).

## Sessions

Run sessions in this order:

1. `run_DEMO.py` familiarises participants with the touchpad, central motion, peripheral distractors, and response deadline. It does not record EEG or eye movements.
2. `run_STAIR.py` estimates the central random-dot kinematogram coherence that produces 50% correct responses. It does not record EEG or eye movements.
3. `run_MAIN.py` runs the motion-reproduction task in the controlled testing session and can record EEG and eye movements.

## Prerequisites

Install Git and Miniforge before creating the experiment environment. Miniforge includes Conda and Mamba.

### macOS

Install Git using the Xcode Command Line Tools:

```sh
xcode-select --install
```

Install Miniforge using the installer for your Mac from [Miniforge releases](https://github.com/conda-forge/miniforge/releases/latest). Close and reopen Terminal, then verify:

```sh
git --version
mamba --version
```

### Windows

Install Git:

```powershell
winget install --id Git.Git -e
```

Install Miniforge using the Windows installer from [Miniforge releases](https://github.com/conda-forge/miniforge/releases/latest). Open a new Miniforge Prompt, then verify:

```powershell
git --version
mamba --version
```

### Linux

Install Git using your distribution package manager. On Ubuntu or Debian:

```sh
sudo apt update
sudo apt install git
```

Install Miniforge using the installer for your Linux architecture from [Miniforge releases](https://github.com/conda-forge/miniforge/releases/latest). Open a new shell and verify:

```sh
git --version
mamba --version
```

## Create the Environment

From the project root, create the project-local Python 3.11 environment and install the pinned runtime packages:

```sh
mamba create -p ./.venv -c conda-forge python=3.11 pip
conda activate ./.venv
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements-python3.txt
```

Use `conda` in place of `mamba` if Mamba is unavailable. The requirements file pins the direct dependencies validated with the experiment; do not upgrade individual packages in this environment.

Confirm the core runtime:

```sh
python -c "import psychopy, pylink, numpy, pandas, scipy; print('PsychoPy', psychopy.__version__)"
```

### Apple Silicon macOS

The validated macOS configuration uses Intel packages under Rosetta because the legacy Pyglet backend used by PsychoPy can fail on native Apple Silicon. Install Rosetta once, then create the environment with Intel packages:

```sh
softwareupdate --install-rosetta --agree-to-license
CONDA_SUBDIR=osx-64 mamba create -p ./.venv -c conda-forge python=3.11 pip
conda activate ./.venv
arch -x86_64 python -m pip install --upgrade pip setuptools wheel
arch -x86_64 python -m pip install -r requirements-python3.txt
```

Run sessions from this environment with `arch -x86_64 python`. Do not reuse a native ARM `.venv`; remove it first with `mamba env remove -p ./.venv`.

To remove any local environment, run `conda deactivate` followed by `mamba env remove -p ./.venv`.

## Run the Experiment

Activate the environment, change to `RUN/`, and launch the sessions in order:

```sh
conda activate ./.venv
cd RUN
python run_DEMO.py
python run_STAIR.py
python run_MAIN.py
```

On Apple Silicon using the Rosetta environment, prefix each launch command with `arch -x86_64`. Run the demo before connecting EEG or EyeLink hardware. Retain console error messages if a session fails.

## Configuration

The `RUN/` folder contains the configuration files used by the session scripts.

| File | Purpose |
| --- | --- |
| `exp_information.json` | Questions shown at session startup. |
| `exp_parameters.json` | Adjustable experiment parameters. Each parameter includes a description. |
| `exp_instructions.json` | Participant-facing instruction lines. Empty strings create blank lines. Keep the final `When you are ready, press SPACE key to start.` entry intact and last. |

When first using a monitor name, PsychoPy asks for display size, resolution, and viewing distance. This monitor profile is saved for later sessions. Set the monitor number only when independently driven displays are connected. Keep `simulate` unchanged outside development. Circular response motion is the default; use linear motion only when a participant cannot perform the circular movement.

Enable EEG and eye recording only for `run_MAIN.py`. When EEG recording is enabled, supply the parallel-port address as a hexadecimal value such as `0xD050`. Feedback is enabled by default; disable it for `run_MAIN.py` only when a participant cannot perform the task.

## Data and Timing

`BHV/`, `EYE/`, and `LOG/` are populated automatically. Save EEG data in `EEG/` using this filename pattern:

```text
sub-<three-digit-subject-number>_ses-MAIN_eeg
```

The central-motion signal duration should be adjusted in one-second increments and should not exceed two seconds. When it changes, adjust the response deadline accordingly.

## EyeLink

Follow the on-screen calibration procedure. In the camera view, use the left and right arrows to change views, and the up/down and page-up/page-down keys to adjust pupil and corneal-reflex thresholds.

At the start of each block, accept the drift-correction fixation with Enter or Space. Press Escape during drift correction to enter setup mode and recalibrate. After calibration or validation, press Escape until trials resume.

The `LIB/` folder provides `edf2asc` executables for macOS, Linux, and Windows for converting EyeLink EDF files.

## USB2LPT and Parallel-Port Triggers

Windows USB2LPT systems install the Python 3 `ftd2xx` package from `requirements-python3.txt`. If the presentation computer lacks a functioning parallel port and uses a USB2LPT adapter, run `LIB/InstallDriverUSB2LPTAdapter.exe`. To remove the adapter driver, run `LIB/RemoveDriverUSB2LPTAdapter.exe`.
