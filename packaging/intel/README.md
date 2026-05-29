# Zava Insurance — On-Device AI Showcase 🛡️  (Intel Edition)

A showcase application demonstrating on-device AI capabilities for insurance
claims processing, running entirely on the NPU via Microsoft Foundry Local.

**This package is optimized for Intel Core Ultra (Lunar Lake / Meteor Lake)
NPUs using the OpenVINO execution provider. Works in airplane mode.**

> Looking for the Snapdragon X (QNN) build? Download
> `ZavaInsuranceAI-Snapdragon-vX.Y.Z.zip` instead.

## Quick Start

```powershell
# First time:
Setup.bat          # or: .\Setup.ps1

# Every time:
StartApp.bat       # opens browser to http://localhost:5000
```

`StartApp.bat` sets `ZAVA_PLATFORM=intel`, which tunes the Foundry Local model
chain for Intel NPU resolution.

## Prerequisites

- **Windows 11 Copilot+ PC** with an Intel Core Ultra NPU (Series 1 or 2)
- **Python 3.10+ (x64)**
- **Foundry Local** (`winget install Microsoft.FoundryLocal`)

## Intel-Optimized Model Chain

The Intel edition prefers models that have OpenVINO NPU variants first:

```
phi-3.5-mini → phi-4-mini → qwen2.5-1.5b → phi-3-mini-4k
```

Foundry Local will automatically resolve each alias to the best OpenVINO INT4
variant available on the device, falling back to CPU when no NPU build exists.

Override the chain at any time:

```powershell
$env:FOUNDRY_MODELS = "phi-4-mini,phi-3.5-mini"
.\StartApp.bat
```

## Features

| Tab | Description |
|-----|-------------|
| **Home** | Overview of on-device AI for insurance operations |
| **Claims AI** | Damage description → AI severity assessment, repair cost estimate |
| **Policy Assistant** | Chat about insurance policies, coverage, claims |
| **Document Analyzer** | Summarize, extract data, or review policy/claim docs |
| **NPU Dashboard** | Live metrics, fleet-scale cost projections, inference log |

## The Demo Moment

Run several claims assessments → turn on airplane mode → run more. They keep
working. Show the NPU Dashboard — $0.00 in cloud costs. Project fleet savings:
10K adjusters × 50 inferences/day = 130M inferences/year, all on-device.

See `DEMO_SCRIPT.txt` for a guided 60-second executive walkthrough.

---

## Prototype Disclosure

This is sample / prototype code for educational purposes. It is provided
"as-is" with no warranties, no SLA, and no production support. AI outputs are
non-deterministic and should not be used for real claims decisions without
human review. See the upstream repository for full disclosures.
