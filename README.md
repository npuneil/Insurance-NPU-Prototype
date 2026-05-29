# Insurance — On-Device AI Showcase 🛡️

A showcase application demonstrating on-device AI capabilities for insurance claims processing, running entirely on the NPU (Neural Processing Unit) via Microsoft Foundry Local. Optimized for Snapdragon X (QNN runtime). Works in airplane mode.

## On-Device AI Prototypes & Sample Code

### Overview

This repository contains prototypes, demos, and sample code that illustrate patterns for building on-device AI solutions. The content is provided for educational and demonstration purposes only to help developers explore ideas and implementation approaches.

This repository does not contain Microsoft products and is not a supported or production-ready offering.

### Prototype & Sample Code Disclosure

- All code and demos are experimental prototypes or samples.
- They may be incomplete, change without notice, or be removed at any time.
- The contents are provided "as-is," without warranties or guarantees of any kind.

### No Product, Performance, or Business Claims

- This repository makes no claims about performance, accuracy, productivity, efficiency, cost savings, reliability, or security.
- Any example outputs, screenshots, or logs are illustrative only and should not be interpreted as typical or expected results.

### AI Output Variability

- AI and machine-learning outputs may be non-deterministic, incomplete, or incorrect.
- Example outputs shown here are not guaranteed and may vary across runs, devices, or environments.

### Responsible AI Considerations

- These samples are intended to demonstrate technical patterns, not validated AI systems.
- Developers are responsible for evaluating fairness, reliability, privacy, accessibility, and safety before using similar approaches in real applications.
- Do not deploy AI solutions based on this code without appropriate testing, human oversight, and safeguards.

### Data & Fictitious Content

- Any names, data, or scenarios used in examples are fictitious and for illustration only.
- Do not use real personal, customer, or confidential data without proper authorization and protections.

### Third-Party Components

- The repository may reference third-party libraries or tools.
- Use of those components is subject to their respective licenses and terms.

### No Support

Microsoft does not provide support, SLAs, or warranties for the contents of this repository.

### Summary

By using this repository, you acknowledge that it contains illustrative prototypes and sample code only, not supported or production-ready software.

---

## Quick Start

```powershell
# First time:
Setup.bat          # or: .\Setup.ps1

# Every time:
StartApp.bat       # opens browser to http://localhost:5000
```

## Prerequisites

- **Windows 11 Copilot+ PC** with Snapdragon X NPU
- **Python 3.10+** (ARM64-native recommended for Snapdragon)
- **Foundry Local** installed (`winget install Microsoft.FoundryLocal`)

## Snapdragon X Optimization

This app is optimized for ARM64 Snapdragon X devices:
- **WMI-based silicon detection** — correctly identifies Snapdragon under x64 emulation
- **No warmup on Snapdragon** — QNN runtime loads on first real request
- **NPU-first model chain**: qwen2.5-1.5b → phi-3-mini-4k → phi-3.5-mini → qwen2.5-7b
- **CPU fallback** when no NPU model is available

## Downloadable Packages (Intel & Snapdragon)

Two pre-built, end-user-friendly zip packages are produced by
[`build-packages.ps1`](./build-packages.ps1):

| Package | Target hardware | NPU runtime | Default model chain |
|---------|-----------------|-------------|---------------------|
| `ZavaInsuranceAI-Intel-v<x.y.z>.zip`      | Intel Core Ultra (Lunar Lake / Meteor Lake) | OpenVINO | `phi-3.5-mini → phi-4-mini → qwen2.5-1.5b → phi-3-mini-4k` |
| `ZavaInsuranceAI-Snapdragon-v<x.y.z>.zip` | Snapdragon X                                | QNN      | `qwen2.5-1.5b → phi-3-mini-4k → phi-3.5-mini → phi-4-mini` |

Each zip is self-contained: end users run `Setup.bat` once, then `StartApp.bat`
thereafter. `StartApp.bat` sets `ZAVA_PLATFORM=intel` or `snapdragon`, and a
`platform.txt` marker is also baked into the package as a fallback. The Flask
app reads either signal to pick the right model chain and to label the NPU
runtime correctly on the dashboard (`NPU (OpenVINO)` vs `NPU (QNN)`).

Platform-specific overlays live in `packaging/intel/` and
`packaging/snapdragon/` (README, START_HERE, Setup.bat, StartApp.bat). Shared
source comes from the repo root (`app.py`, `templates/`, `static/`,
`requirements.txt`, `Setup.ps1`, `DEMO_SCRIPT.txt`).

### Build both packages

```powershell
# From the repo root
.\build-packages.ps1                       # → dist\ZavaInsuranceAI-{Intel,Snapdragon}-v1.0.0.zip
.\build-packages.ps1 -Version 1.1.0        # bump version
.\build-packages.ps1 -Version 1.1.0 -Clean # wipe dist\ first
```

## Features

| Tab | Description |
|-----|-------------|
| **Home** | Overview of on-device AI for insurance operations |
| **Claims AI** | Upload or describe property/vehicle damage → AI severity assessment, repair cost estimate, next steps |
| **Policy Assistant** | Chat about insurance policies, coverage, claims, and terminology |
| **Document Analyzer** | Paste policy docs or claim reports → summarize, extract data, or review for risks |
| **NPU Dashboard** | Live metrics, fleet-scale cost projections, carbon calculator, inference log |

## Sample Data

- 6 sample damage scenarios (flood, fire, hurricane, burst pipe, collapse, interior flood)
- Sample insurance policy document
- Voice dictation support for field adjusters

## Demo Experience

See `START_HERE.txt` for setup instructions and `DEMO_SCRIPT.txt` for a guided demo walkthrough.

**The key demo moment:** Run claims assessments → turn on airplane mode → run more assessments. They keep working. Show the NPU Dashboard — $0.00 in cloud costs. Project fleet savings: 10K adjusters × 50 inferences/day = 130M inferences/year, all on-device.
