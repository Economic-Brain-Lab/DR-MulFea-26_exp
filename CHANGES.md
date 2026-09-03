# Changelog

All notable changes after version 1.0 are documented here.

## 2026-09-03

- Migrated the `RUN` scripts to Python 3-compatible NumPy and public PsychoPy APIs.
- Added pinned Python 3 runtime dependencies and cross-platform Conda/Mamba setup instructions.
- Documented Apple Silicon macOS installation using Intel packages under Rosetta.
- Moved platform-specific EyeLink conversion and USB2LPT driver utilities to `LIB/`.
- Added GitHub documentation for Git, Miniforge/Mamba, and Python 3 setup on macOS, Windows, and Linux.

## Version 1.2

### 2019-10-22

- Added a date to EDF timestamps.
- Added a fallback coherence value in `run_MAIN.py` when the staircase has not finished.

### 2019-10-21

- Added timestamps to EDF file names.

### 2019-10-18

- Added `PIXEL_SIZE` information to EDF files.
- Added the Linux `edf2asc` converter.

### 2019-10-17

- Added extra columns to `tsv.gz` data files.

## Version 1.1

### 2019-10-16

- Added USB2LPT adapter support.