# Novel or Not? PatEx-Gym: Agentic Prior-Art Search for Novelty Assessment in Patent Examination

Qiyao Wang, Xinyi Chen, Hongbo Wang, Jiayuan Lu, Minghuan Tan, Yuan Lin†, Min Yang†

SIAT, Chinese Academy of Sciences · UCAS · Dalian University of Technology · SUAT  
† Corresponding authors

[GitHub](https://github.com/AIforIP/PatEx-Gym) | [Contact](mailto:wangqiyao25@mails.ucas.ac.cn)

## 🔔 News

- **2026-10-27** — Released 100 PatEx-Bench tasks, per-task verifiers, and the Codex Harness.

## 📅 Timeline

- [x] Partial PatEx-Bench release (100 tasks)
- [x] Codex Harness and Docker image
- [x] Evaluation code
- [ ] Patent-1M
- [ ] Paper-52K

## 📝 Introduction

PatEx-Gym is a framework for developing and evaluating patent examination agents. Agents
iteratively search prior art, inspect technical evidence, and generate USPTO-style Office
Actions. The framework evaluates both examination quality and prior-art discovery, making
patent examination a testbed for agentic search and deep research.

The paper presents PatEx-Bench (1,000 tasks), Patent-1M and Paper-52K retrieval corpora,
PASS for search trajectory synthesis, and the 4B PatEx-Agent. This repository currently
provides a 100-task subset and the Codex runtime.

## 📦 Public release

- `bench/`: 100 Harbor tasks, each with application text, instructions, environment, and `tests/`.
- `src/`: Codex Harness and gateway source code.
- `base-image/`: one prebuilt Linux/amd64 Codex image, stored with Git LFS.

The subset covers A–H with 12–13 tasks per section, using the available Main CPC field.
See [bench_selection.json](bench_selection.json) for the task list. The frontend, training
data, and task-construction pipeline are outside this release.

## 🚀 Quick start

```bash
git lfs install
git clone https://github.com/AIforIP/PatEx-Gym.git
cd PatEx-Gym
git lfs pull
zstd -dc base-image/patex-codex-harness-amd64.tar.zst | docker load
```

Use `bench/` with Harbor and the image `patex-codex-harness:latest`. Configure your model
endpoint and search backend before running tasks.

## Contact

For questions or model evaluation submissions, contact
[wangqiyao25@mails.ucas.ac.cn](mailto:wangqiyao25@mails.ucas.ac.cn).
