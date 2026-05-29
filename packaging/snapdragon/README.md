# Zava Insurance — On-Device AI Showcase 🛡️  (Snapdragon Edition)

A showcase application demonstrating on-device AI capabilities for insurance
claims processing, running entirely on the NPU via Microsoft Foundry Local.

**This package is optimized for Snapdragon X NPUs using the QNN execution
provider. Works in airplane mode.**

> Looking for the Intel Core Ultra (OpenVINO) build? Download
> `ZavaInsuranceAI-Intel-vX.Y.Z.zip` instead.

## Quick Start

```powershell
# First time:
Setup.bat          # or: .\Setup.ps1

# Every time:
StartApp.bat       # opens browser to http://localhost:5000
```

`StartApp.bat` sets `ZAVA_PLATFORM=snapdragon`, which tunes the Foundry Local
model chain for QNN NPU resolution.

## Prerequisites

- **Windows 11 Copilot+ PC** with Snapdragon X NPU
- **Python 3.10+** (ARM64-native recommended)
- **Foundry Local** (`winget install Microsoft.FoundryLocal`)

## Snapdragon-Optimized Model Chain

The Snapdragon edition prefers models that have QNN NPU variants first:

```
qwen2.5-1.5b → phi-3-mini-4k → phi-3.5-mini → phi-4-mini
```

Foundry Local will automatically resolve each alias to the best QNN INT4
variant available on the device, falling back to CPU when no NPU build exists.

Override the chain at any time:

```powershell
$env:FOUNDRY_MODELS = "phi-3.5-mini,qwen2.5-1.5b"
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
