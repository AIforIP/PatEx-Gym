# PatEx-Gym

PatEx-Gym is a public Harbor release for USPTO-style patent Office Action agents.

## Release contents

- `bench/`: 100 Harbor tasks. Each task contains the application input, instruction,
  environment definition, and its Harbor `tests/` verifier payload.
- `base-image/patex-codex-harness-amd64.tar.zst`: the prebuilt Codex harness image.
- `src/`: the public Codex harness and gateway sources.

The released task snapshot exposes Main CPC rather than Main IPC. The 100 tasks are therefore
stratified by the first CPC section letter (A–H), with 12–13 tasks per section; the exact release
manifest is in `bench_selection.json`.

The visual frontend, training data, task-construction data and scripts, PI image, and source
corpora are not included. The public task release includes the per-task verifier files so that
the Harbor layout matches the original benchmark format.

## Timeline

- **2026-10-08** — Released a public subset of PatEx-Bench and the Codex Harness.
- **Current release** — Patent-1M and Paper-52K are not included.

## Quick start

```bash
git lfs install
git clone https://github.com/AIforIP/PatEx-Gym.git
cd PatEx-Gym
git lfs pull
zstd -dc base-image/patex-codex-harness-amd64.tar.zst | docker load
```

Use the tasks under `bench/` with Harbor and the loaded image tag
`patex-codex-harness:latest`. A search backend and model endpoint must be supplied by the user;
neither source corpora nor model credentials are distributed here.

## Evaluation submissions

For model evaluation or questions about the released verifier, contact
[wangqiyao25@mails.ucas.ac.cn](mailto:wangqiyao25@mails.ucas.ac.cn).

## Citation and contact

This release is maintained by AIforIP. For questions or evaluation requests, contact
[wangqiyao25@mails.ucas.ac.cn](mailto:wangqiyao25@mails.ucas.ac.cn).
