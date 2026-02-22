# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LeRobot is a PyTorch-based machine learning library for real-world robotics by Hugging Face. It provides a hardware-agnostic robot control interface, standardized dataset format (LeRobotDataset), and implementations of state-of-the-art policies (ACT, Diffusion, TDMPC, VQ-BeT, SmolVLA, etc.). Source code lives in `src/lerobot/`.

## Development Environment

This project uses a **conda environment named `lerobot`**. All commands must be run inside it:
```bash
conda activate lerobot
# or prefix commands with: conda run -n lerobot <cmd>
```

After pulling upstream changes, re-sync dependencies:
```bash
pip install -e ".[dev,test]"             # dev + test deps
pip install -e ".[dev,test,aloha,pusht]" # include sim envs
```

## Common Commands

### Test
```bash
pytest tests -vv --maxfail=10            # full suite
pytest tests/test_available.py           # single file
pytest tests/test_available.py::test_available_policies  # single test
make test-end-to-end                     # end-to-end train+eval for ACT, Diffusion, TDMPC, SmolVLA
```

Test artifacts are tracked with git-lfs. Run `git lfs pull` if `tests/artifacts/` is missing data.

### Lint and Format
```bash
pre-commit install                       # one-time setup
pre-commit run --all-files               # run all checks (ruff, typos, mypy, bandit, etc.)
ruff check <files>                       # lint specific files
ruff format --check <files>              # check formatting
```

### Train and Evaluate
```bash
lerobot-train --policy.type=act --env.type=aloha --dataset.repo_id=lerobot/aloha_sim_transfer_cube_human ...
lerobot-eval --policy.path=<checkpoint> --env.type=aloha ...
```

All CLI scripts are registered as entry points: `lerobot-train`, `lerobot-eval`, `lerobot-record`, `lerobot-teleoperate`, `lerobot-calibrate`, `lerobot-replay`, `lerobot-dataset-viz`, `lerobot-edit-dataset`, `lerobot-find-cameras`, `lerobot-find-port`, `lerobot-info`, `lerobot-setup-motors`, `lerobot-find-joint-limits`, `lerobot-imgtransform-viz`.

## Code Style

- **Formatter/Linter**: ruff (line length 110, target Python 3.10, double quotes, space indentation)
- **Enabled rules**: E, W, F, I, B, C4, T20, N, UP, SIM
- **Imports**: isort via ruff with `combine-as-imports`, `lerobot` as known first-party
- **Docstrings**: Google convention
- **Additional checks**: typos (spell check), pyupgrade, bandit (security), mypy (type checking, excludes tests/examples/benchmarks)

## Architecture

### Configuration System
Uses **draccus** (not Hydra/YAML). Configs are Python dataclasses with CLI parsing via `--namespace.field=value` syntax. Key configs: `TrainPipelineConfig`, `EvalPipelineConfig`, `PreTrainedConfig` (base for all policies).

### Policy System (`policies/`)
Each policy has a directory with `configuration_*.py` (config dataclass) and `modeling_*.py` (nn.Module). All policies inherit from `PreTrainedPolicy` which extends `nn.Module` + `HubMixin` for HF Hub integration (`from_pretrained`/`push_to_hub`). The factory in `policies/factory.py` dynamically loads policy classes by name.

### Dataset System (`datasets/`)
`LeRobotDataset` loads Parquet (state/action) + MP4 (vision) data from HF Hub. Format version is v3.0. Key classes: `LeRobotDatasetMetadata`, `MultiLeRobotDataset`, `OnlineBuffer`.

### Data Processing Pipeline (`processor/`)
Generic sequential transformation framework. `ProcessorStep` (ABC) -> `DataProcessorPipeline` chains steps with save/load support. Processors handle normalization, delta actions, tokenization, device placement.

### Robot/Hardware Abstraction (`robots/`, `cameras/`, `motors/`, `teleoperators/`)
`Robot` ABC defines the interface: `connect()`, `disconnect()`, `get_observation()`, `send_action()`. Configs use draccus `ChoiceRegistry` for extensible subclass selection.

### Environment System (`envs/`)
Gymnasium-compatible. `make_env()` factory creates VectorEnv instances. Supports ALOHA, PushT, LIBERO, MetaWorld. Environments can be loaded from HF Hub repos.

### Training Pipeline (`scripts/lerobot_train.py`)
Uses HF `Accelerate` for distributed training + mixed precision. Key flow: config parsing -> dataset creation -> policy instantiation -> optimizer setup -> training loop with eval/checkpoint/WandB logging.

### Module Registry (`__init__.py`)
Lightweight init with `available_policies`, `available_robots`, `available_datasets`, etc. Avoids heavy imports. When adding new policies/robots/envs, update the registries here and in `tests/test_available.py`.

### Key Patterns
- **Factory pattern** everywhere: `make_policy()`, `make_dataset()`, `make_env()`, `make_optimizer_and_scheduler()`
- **HubMixin integration**: policies, datasets, and processor pipelines all serialize to/from HF Hub
- **ChoiceRegistry**: draccus pattern for extensible config subclass selection (robots, envs, policies)
