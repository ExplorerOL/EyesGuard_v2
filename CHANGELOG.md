# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- PyInstaller packaging: EyesGuard.spec (onefile, bundled res/, tray icon) and pyinstaller dev dependency; README build instructions
- AI-agent infrastructure: AGENTS.md and .agents/ knowledge base (architecture, state machine, settings, known issues), knowledge graph, retro journal, task directories
- CI workflow (GitHub Actions): ruff + pytest on push/PR
- Git hooks via prek: ruff check/format on commit (changed files) and push (whole project), plus repo hygiene hooks
- Project tooling: .python-version (3.11), .editorconfig, [tool.pytest.ini_options]
- Skill `add-user-setting` (end-to-end adding of a user setting) and skills registry in .agents/skills/README.md

### Fixed
- Settings window icon loaded via ResImages: fixed FileNotFoundError for res/img when running the frozen build

### Changed
- playsound installed from vendored wheel (wheels/): its PyPI sdist does not build under PEP 517 (setup.py resolves its path via inspect.getsource); replaces the dependency-metadata workaround
- Runtime paths resolved for frozen builds: resources via sys._MEIPASS, settings and logs next to the exe (src/support/paths.py); settings directory auto-created on save
- Linter config adopted from the reference project as-is: full rule set (naming, bugbear, builtins, complexity, pycodestyle, pyflakes, bandit, pydocstyle, isort, print, unicode names, encoding), line-length 120
- Codebase cleaned to zero ruff findings under the full rule set (docstrings, prints, long lines, file encoding)
- Project migrated to uv: pyproject.toml + uv.lock; pillow added to dependencies; playsound restricted to the win32 marker
- Ruff config moved from pyproject.toml to linter_ruff.toml; ruff pinned to 0.16.4 (synced with pre-commit hook rev)
- Codebase reformatted to single quotes (ruff format, quote-style = "single")
- Legacy files reformatted by ruff format (baseline for format hooks)
- Lint baseline cleaned: `ruff check .` passes with no errors

### Removed
- requirements.txt: pyproject.toml + uv.lock is now the single source of dependencies

## [2.0.0] - 2024-04-02

### Added
- First release of EyesGuard for Windows written in Python

[Unreleased]: https://github.com/ExplorerOL/EyesGuard_v2/compare/EyesGuard-v2.0.0..HEAD
[2.0.0]: https://github.com/ExplorerOL/EyesGuard_v2/releases/tag/EyesGuard-v2.0.0
