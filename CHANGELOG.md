# CHANGELOG

<!-- version list -->

## v1.34.0 (2025-11-29)

### Bug Fixes

- **ci**: Prevent workflow cancellation on main branch pushes
  ([`f3edccc`](https://github.com/sensiloles/telegram-bot-stack/commit/f3edcccd55309d21027635b5ca8de5c0ac30a45d))

### Continuous Integration

- Add concurrency control to auto-cancel outdated CI runs
  ([`a2affdf`](https://github.com/sensiloles/telegram-bot-stack/commit/a2affdfeda90dc573dbdc6fc693ffcd8e850ab7e))

### Documentation

- **status**: Mark #132 Makefile alternatives as DONE
  ([`276ff05`](https://github.com/sensiloles/telegram-bot-stack/commit/276ff05a759d716f150240bafd94d218d32cff0a))

### Features

- **dx**: Add cross-platform task runner as Makefile alternative for Windows
  ([`9e06c65`](https://github.com/sensiloles/telegram-bot-stack/commit/9e06c65536980a0ff01f5ca6f55de36aaf635cbd))


## v1.33.0 (2025-11-29)

### Bug Fixes

- **automation**: Add mandatory CI checks before PR merge
  ([`689b870`](https://github.com/sensiloles/telegram-bot-stack/commit/689b870c876da140b43fe7e6d73d1b8651acce3f))

### Features

- **deploy**: Add cross-platform SSH key generation using cryptography
  ([`f39bab4`](https://github.com/sensiloles/telegram-bot-stack/commit/f39bab4621dfa89c3d0e16bc075032ab0f6b858d))


## v1.32.0 (2025-11-29)

### Documentation

- **status**: Add Windows cross-platform support to roadmap (#130-#135)
  ([`4e1955b`](https://github.com/sensiloles/telegram-bot-stack/commit/4e1955b09ad2698155a80f394860011907bbc9a7))

### Features

- **deploy**: Implement SSH key generation and delivery to VPS
  ([`fbadcc9`](https://github.com/sensiloles/telegram-bot-stack/commit/fbadcc9c0b62261c1008a944283e45816d558587))


## v1.31.0 (2025-11-29)

### Features

- **deploy**: Add multi-bot deployment support
  ([#117](https://github.com/sensiloles/telegram-bot-stack/pull/117),
  [`9532409`](https://github.com/sensiloles/telegram-bot-stack/commit/95324096aef235aaad7b26eb043c7d1c4856962f))


## v1.30.0 (2025-11-29)

### Bug Fixes

- **tests**: Update mocks after VPSConnection refactoring
  ([`6b4b8b8`](https://github.com/sensiloles/telegram-bot-stack/commit/6b4b8b8f0c7bc33552d1e4789162902d37c519ba))

### Documentation

- **status**: Mark #118 SSH key authentication as DONE
  ([`ea41178`](https://github.com/sensiloles/telegram-bot-stack/commit/ea4117820f7c40ff8be1ee0bd30387c74da268d8))

### Features

- **deploy**: Support SSH key-based authentication alongside password
  ([`4a45701`](https://github.com/sensiloles/telegram-bot-stack/commit/4a4570175dc7419769444ce5efdd83247c6a6df7))


## v1.29.0 (2025-11-29)

### Features

- **cli**: Add doctor command for project health diagnostics
  ([`57966c1`](https://github.com/sensiloles/telegram-bot-stack/commit/57966c177f8f9514027ff986886cf8cc591ea6e3))


## v1.28.0 (2025-11-29)

### Documentation

- **roadmap**: Organize all 121 issues into milestones and update roadmap
  ([`7ff9afd`](https://github.com/sensiloles/telegram-bot-stack/commit/7ff9afd0d10d2a567b28ed21e0091594aaeb190b))

### Features

- **deploy**: Handle bot already running/deployed scenarios
  ([#119](https://github.com/sensiloles/telegram-bot-stack/pull/119),
  [`bb62e72`](https://github.com/sensiloles/telegram-bot-stack/commit/bb62e720398ffb08d8a35a50937a44f80e396b6d))


## v1.27.0 (2025-11-29)

### Documentation

- **roadmap**: Add 5 new issues for v2.0.0 preparation
  ([`110cc29`](https://github.com/sensiloles/telegram-bot-stack/commit/110cc29019bcbc0288fcfb027efcc9a3387c5528))

### Features

- **mcp**: Add milestone management tools to GitHub MCP server
  ([`5c6bc16`](https://github.com/sensiloles/telegram-bot-stack/commit/5c6bc1615557710b137c6460a7304090defc59cd))


## v1.26.1 (2025-11-29)

### Bug Fixes

- **deploy**: Fix 12 critical deployment bugs found in E2E testing
  ([`92b808b`](https://github.com/sensiloles/telegram-bot-stack/commit/92b808bf742e6d5f1841f91e5ad7fa2d9f553be6))


## v1.26.0 (2025-11-29)

### Features

- **ci**: Refactor CI/CD into modular workflows
  ([`82a449f`](https://github.com/sensiloles/telegram-bot-stack/commit/82a449fe350e091e94399b89c9e904e91ba08244))

### Testing

- **integration**: Add VPS deployment integration tests infrastructure
  ([`3d2c12c`](https://github.com/sensiloles/telegram-bot-stack/commit/3d2c12cd4bcf1abff650fe8f0bdc54dfd1da86d0))


## v1.25.3 (2025-11-27)

### Bug Fixes

- **ci**: Add id-token permission for PyPI Trusted Publishing
  ([`e202830`](https://github.com/sensiloles/telegram-bot-stack/commit/e202830d819b2a644d6972bd3eba1428a250d579))


## v1.25.2 (2025-11-27)

### Bug Fixes

- **tests**: Configure git identity locally in CI environments
  ([`7c27e75`](https://github.com/sensiloles/telegram-bot-stack/commit/7c27e7575fce0b186fdbbb65e6ddc1d064c718f0))


## v1.25.1 (2025-11-27)

### Bug Fixes

- **ci**: Add database dependencies to PyPI publish workflow
  ([`7587f26`](https://github.com/sensiloles/telegram-bot-stack/commit/7587f260707564d02997d9cb282af58a6d053add))

### Documentation

- **deploy**: Add comprehensive troubleshooting guide
  ([#84](https://github.com/sensiloles/telegram-bot-stack/pull/84),
  [`2b235be`](https://github.com/sensiloles/telegram-bot-stack/commit/2b235befcc4a22c33373c6ffb2aa356a63ae7c47))


## v1.25.0 (2025-11-27)

### Features

- **deploy**: Add health checks and automatic recovery
  ([#77](https://github.com/sensiloles/telegram-bot-stack/pull/77),
  [`f5241f1`](https://github.com/sensiloles/telegram-bot-stack/commit/f5241f170a844a440d0b4058f9b1199cd2f47cee))


## v1.24.0 (2025-11-27)

### Features

- **deploy**: Add rollback mechanism for failed deployments
  ([`2e107c0`](https://github.com/sensiloles/telegram-bot-stack/commit/2e107c0eac65534e0acd03641b308adc21fe833f))

### Refactoring

- **deploy**: Split deploy.py into smaller modules
  ([`7c98d16`](https://github.com/sensiloles/telegram-bot-stack/commit/7c98d165c9e1b4d23dd2aaf5a4d4e3805497f702))


## v1.23.0 (2025-11-27)

### Features

- **deploy**: Add backup and restore commands for bot data
  ([`0bcfd84`](https://github.com/sensiloles/telegram-bot-stack/commit/0bcfd8464f69efa564c9b6ee8cf69a0aceb5893d))


## v1.22.1 (2025-11-27)

### Bug Fixes

- **ide**: Configure mypy extension for real-time type checking
  ([`da660e0`](https://github.com/sensiloles/telegram-bot-stack/commit/da660e04e2e4330030ab11290f6fff65a6d17825))


## v1.22.0 (2025-11-27)

### Continuous Integration

- Trigger workflows after making repository public
  ([`0ff4c2c`](https://github.com/sensiloles/telegram-bot-stack/commit/0ff4c2c3d87547d2027c8d96dd4b2a38d2bf9170))

### Features

- **deploy**: Add secrets management for secure token storage
  ([`d7a95e2`](https://github.com/sensiloles/telegram-bot-stack/commit/d7a95e2d68d11e4492528bd95f394110adbd82e0))


## v1.21.1 (2025-11-26)

### Bug Fixes

- **ci**: Add mypy type checking to pre-commit hooks
  ([`847152c`](https://github.com/sensiloles/telegram-bot-stack/commit/847152cd922f25d1b2c1921f3481706f874db570))

### Documentation

- **readme**: Simplify and focus on framework users
  ([`eb90eac`](https://github.com/sensiloles/telegram-bot-stack/commit/eb90eac75915132a2e5ad1d5cdbc99a8b2ad2509))

- **status**: Update PROJECT_STATUS with deployment hardening roadmap
  ([`0951c24`](https://github.com/sensiloles/telegram-bot-stack/commit/0951c24d2addffead73a61cd079c745ff9156f1f))

### Refactoring

- Consolidate code and optimize project graphs
  ([`919e4fa`](https://github.com/sensiloles/telegram-bot-stack/commit/919e4fa7c427406abaccba6fea6cf5d1bf39f10c))


## v1.21.0 (2025-11-26)

### Documentation

- **deployment**: Expand deployment documentation with provider guides and advanced scenarios
  ([`3e1bc1a`](https://github.com/sensiloles/telegram-bot-stack/commit/3e1bc1a49b797abcfa35562c82cd7eea29f993d6))

### Features

- **cli**: Use pyproject.toml only, add Makefile and improve dev env
  ([`8129f72`](https://github.com/sensiloles/telegram-bot-stack/commit/8129f7273f761a82e14fcb905af989c2d130a63b))


## v1.20.0 (2025-11-26)

### Features

- **config**: Set Python 3.12 as primary development version
  ([`8662afb`](https://github.com/sensiloles/telegram-bot-stack/commit/8662afbfe0de8723fee7b30469c6acd6edc04021))


## v1.19.0 (2025-11-25)

### Features

- **deploy**: Add VPS deployment CLI with one-command deployment
  ([`c8c8f9b`](https://github.com/sensiloles/telegram-bot-stack/commit/c8c8f9bf63adf1d41a1f12cb784c2d5c8f75d8e4))


## v1.18.1 (2025-11-25)

### Bug Fixes

- **agent**: Add post-merge local cleanup requirement for MCP
  ([`89f2bd0`](https://github.com/sensiloles/telegram-bot-stack/commit/89f2bd0f0ba7331056efa1f69e37820add8af668))


## v1.18.0 (2025-11-25)

### Features

- **agent**: Implement Phase 2 agent optimizations - cache, metrics, and analytics
  ([`bdfb889`](https://github.com/sensiloles/telegram-bot-stack/commit/bdfb889b68458b6be6352bf074f902c2c27d2f8c))


## v1.17.0 (2025-11-25)

### Features

- **cli**: Implement full CLI tool for bot project management (Issue #40)
  ([`1adeb75`](https://github.com/sensiloles/telegram-bot-stack/commit/1adeb75bd1e99e7b65dc37f73ed695afc8893b7e))


## v1.16.0 (2025-11-25)

### Features

- **agent**: Optimize AI agent workflow - Quick Wins (67% token reduction)
  ([`ba15e7a`](https://github.com/sensiloles/telegram-bot-stack/commit/ba15e7a066334da735f476cf546f0b9af3b2e9f9))


## v1.15.0 (2025-11-24)

### Bug Fixes

- **mcp**: Read credentials from .env file for better security
  ([`daf7fc4`](https://github.com/sensiloles/telegram-bot-stack/commit/daf7fc44cadcd96da291a6e735938821a53e10e2))

### Features

- **mcp**: Add MCP servers automation and monitoring tools
  ([`691ddb2`](https://github.com/sensiloles/telegram-bot-stack/commit/691ddb2e856242a3060c94d04c193d1be2ec115e))


## v1.14.0 (2025-11-24)

### Features

- **mcp**: Fix project-graph server and auto-generate graphs
  ([`6bc51c1`](https://github.com/sensiloles/telegram-bot-stack/commit/6bc51c1162896e9d228aae6c96cdaf9d1d6b9d1c))


## v1.13.0 (2025-11-24)

### Features

- **mcp**: Enhance server with PR management and batch operations
  ([`d5f7e8d`](https://github.com/sensiloles/telegram-bot-stack/commit/d5f7e8d434e78fe31c8783be94cf7a8429a32156))


## Unreleased

### Features

- **cli**: Implement CLI tool with full dev environment setup (#40)

  - Add `telegram-bot-stack init` command - Initialize new bot project with complete dev environment
  - Add `telegram-bot-stack new` command - Create bot from template
  - Add `telegram-bot-stack dev` command - Run bot in development mode with auto-reload
  - Add `telegram-bot-stack validate` command - Validate bot configuration
  - Add virtual environment management utilities
  - Add dependency management (pip, poetry, pdm support)
  - Add linting setup (ruff, mypy, pre-commit hooks)
  - Add testing setup (pytest with fixtures)
  - Add IDE configuration (VS Code, PyCharm)
  - Add Git initialization with .gitignore
  - Add basic bot template
  - Add CLI entry point to pyproject.toml
  - Add comprehensive CLI tests (29 tests, 283 total)

- **mcp**: Enhanced MCP server with PR management and batch operations
  - Add Pull Request management (create, merge, list, check CI)
  - Add batch operations for updating multiple issues at once
  - Add advanced filtering (milestone, assignee, sort, direction, since)
  - Add repository caching for better performance
  - Add actionable error messages with hints
  - Version 2.0.0 of MCP server

### Changed

- Add CLI dependencies: `click>=8.1.0`, `jinja2>=3.1.0`, `watchdog>=3.0.0`

## v1.12.0 (2025-11-24)

### Documentation

- **archive**: Add business analysis document
  ([`1c0e6f1`](https://github.com/sensiloles/telegram-bot-stack/commit/1c0e6f120c658c36690bf00a9154b003c1461e9b))

- **roadmap**: Consolidate roadmap into PROJECT_STATUS.md
  ([`5b692c0`](https://github.com/sensiloles/telegram-bot-stack/commit/5b692c019eab4a41c16a1a8d816b0de6a2242910))

- **roadmap**: Update PROJECT_STATUS with 12 new issues and scaling roadmap
  ([`e2633d2`](https://github.com/sensiloles/telegram-bot-stack/commit/e2633d28fb7d8b753ab7faec37eaf106342789df))

### Features

- **mcp**: Add custom MCP server for GitHub issues integration
  ([`5eda78e`](https://github.com/sensiloles/telegram-bot-stack/commit/5eda78e32f1635ee7bee8005076b8992cd313623))

## v1.11.0 (2025-11-18)

### Bug Fixes

- **ci**: Resolve Python 3.9 compatibility and formatting issues
  ([`f7c38aa`](https://github.com/sensiloles/telegram-bot-stack/commit/f7c38aa1b37518f88c93761e3b522eea6f2e2ee8))

### Features

- **examples**: Add tests, graceful shutdown, and Makefile commands
  ([`14700bc`](https://github.com/sensiloles/telegram-bot-stack/commit/14700bc94945f51a3d27dc7167653947d710a643))

## v1.10.0 (2025-11-18)

### Chores

- **config**: Simplify .env.example to GitHub token only
  ([`7691ae6`](https://github.com/sensiloles/telegram-bot-stack/commit/7691ae611628628063d1b0526cc7df1337d24059))

- **makefile**: Add GitHub flow commands and remove outdated docs
  ([`eeee909`](https://github.com/sensiloles/telegram-bot-stack/commit/eeee9096dfa557543664153e206395f73b4ee439))

- **makefile**: Add GitHub flow commands and remove outdated docs
  ([`2958469`](https://github.com/sensiloles/telegram-bot-stack/commit/29584694105b5987236bed24dd93e9f3bb62b12e))

### Documentation

- **graphs**: Add complete project coverage with 3 new domains
  ([`6769dcc`](https://github.com/sensiloles/telegram-bot-stack/commit/6769dcc8020184fad4ca28fa56ad6d06ea79ac27))

### Features

- **scripts**: Add pr-ready command to mark draft PRs as ready
  ([`9dec8f1`](https://github.com/sensiloles/telegram-bot-stack/commit/9dec8f1d8854e9781b59be4b441c25be0cc71e84))

### Refactoring

- **docs**: Restructure documentation and remove dev CLI wrapper
  ([`eeee909`](https://github.com/sensiloles/telegram-bot-stack/commit/eeee9096dfa557543664153e206395f73b4ee439))

## v1.9.0 (2025-11-18)

### Features

- **scripts**: Add issue management scripts for labels and dependencies
  ([`9a350de`](https://github.com/sensiloles/telegram-bot-stack/commit/9a350de0e9e4abf616b3d41ad0d6ecfd3c62970c))

## v1.8.1 (2025-11-18)

### Bug Fixes

- **vscode**: Remove comments from settings.recommended.json
  ([`e7b706a`](https://github.com/sensiloles/telegram-bot-stack/commit/e7b706acabdf562985b4ba710c9568646b3d53f2))

### Documentation

- **examples**: Add reminder_bot and menu_bot examples
  ([`61f00f2`](https://github.com/sensiloles/telegram-bot-stack/commit/61f00f23d5b9872f2a600175c38f22b1edf89373))

- **github**: Optimize and consolidate .github folder
  ([`be5bd23`](https://github.com/sensiloles/telegram-bot-stack/commit/be5bd23555b8e4e26bb710ca51597324316deac2))

- **status**: Add VPS deployment issues #27, #28, #29
  ([`bb9e086`](https://github.com/sensiloles/telegram-bot-stack/commit/bb9e0860216eb1f7e74c670ee7a5161e86d40db4))

- **vscode**: Add recommended settings with type checking
  ([`14e4eea`](https://github.com/sensiloles/telegram-bot-stack/commit/14e4eea2f82e51952745bc332f55f66c4dfd70fd))

## v1.8.0 (2025-11-18)

### Features

- **graphs**: Hierarchical multi-graph system v3.0
  ([`e894dd9`](https://github.com/sensiloles/telegram-bot-stack/commit/e894dd95e8a19d5e3257836057b66e15edf374ba))

- **graphs**: Implement hierarchical multi-graph system v3.0
  ([`e894dd9`](https://github.com/sensiloles/telegram-bot-stack/commit/e894dd95e8a19d5e3257836057b66e15edf374ba))

## v1.7.1 (2025-11-18)

### Bug Fixes

- **docs**: Remove .github/README.md to fix main page display
  ([`2a27a48`](https://github.com/sensiloles/telegram-bot-stack/commit/2a27a484f8369aa8f6456585cef267d0fde466ca))

## v1.7.0 (2025-11-18)

### Features

- **decorators**: Add rate limiting decorator
  ([`917a9a5`](https://github.com/sensiloles/telegram-bot-stack/commit/917a9a5607922c7eab62ae547d3c4edb0d35c47d))

- **decorators**: Add rate limiting decorator for spam protection
  ([`917a9a5`](https://github.com/sensiloles/telegram-bot-stack/commit/917a9a5607922c7eab62ae547d3c4edb0d35c47d))

## v1.6.0 (2025-11-18)

### Documentation

- **status**: Update PROJECT_STATUS with Phase 2+ roadmap
  ([`16cab76`](https://github.com/sensiloles/telegram-bot-stack/commit/16cab768cae1696d57b1f0b77698b8091f38e51a))

### Features

- **storage**: Implement SQL storage backend
  ([`4ef47ad`](https://github.com/sensiloles/telegram-bot-stack/commit/4ef47ade8dfe688f15c6942ef342b5827eba198a))

## v1.5.0 (2025-11-17)

### Features

- **graphs**: Implement multi-graph dependency system
  ([`3b61520`](https://github.com/sensiloles/telegram-bot-stack/commit/3b61520482184a3bea2100bab90415ef7665d2a8))

## v1.4.0 (2025-11-17)

### Features

- **scripts**: Auto-delete remote branch on merge with --cleanup
  ([`0c0fd7e`](https://github.com/sensiloles/telegram-bot-stack/commit/0c0fd7efc7254bad71252e75787f6d6feca12a6e))

## v1.3.0 (2025-11-17)

### Features

- **tooling**: Add comprehensive dependency graph for AI agent navigation
  ([`4a194c8`](https://github.com/sensiloles/telegram-bot-stack/commit/4a194c8c74586e19ac0b87520f56ed416675daf0))

## v1.2.1 (2025-11-17)

### Bug Fixes

- **ci**: Ensure release only runs after tests pass
  ([`038d5ac`](https://github.com/sensiloles/telegram-bot-stack/commit/038d5accaae3266e727ad5a40e57493998eee77f))

## v1.2.0 (2025-11-17)

### Features

- **ci**: Add PyPI publication workflow and documentation
  ([`6c82a7f`](https://github.com/sensiloles/telegram-bot-stack/commit/6c82a7f6ba5ce3aa74f30895c2a19456a3d2050a))

- **pypi**: Prepare package for PyPI publication
  ([`6c82a7f`](https://github.com/sensiloles/telegram-bot-stack/commit/6c82a7f6ba5ce3aa74f30895c2a19456a3d2050a))

## v1.1.2 (2025-11-17)

### Bug Fixes

- **scripts**: Handle empty issue list in read_issues.py
  ([`0912858`](https://github.com/sensiloles/telegram-bot-stack/commit/091285850f2837e433e9e5370e9cc3a9e70283a6))

### Documentation

- Remove hardcoded coverage metrics from .github/README.md
  ([`4867611`](https://github.com/sensiloles/telegram-bot-stack/commit/48676115bcb54e005d1e6b2af4f14d8587d6823f))

- Remove last hardcoded coverage metric from development-archive
  ([`2fb668e`](https://github.com/sensiloles/telegram-bot-stack/commit/2fb668e15829768d9a22531d7ec7f2c7a35a7340))

## v1.1.1 (2025-11-17)

### Bug Fixes

- **scripts**: Correct PR auto-assignment to use proper GitHub client
  ([`1e9de4a`](https://github.com/sensiloles/telegram-bot-stack/commit/1e9de4aadfc4bbec2b9f66a6e9e29a002675a97e))

## v1.1.0 (2025-11-17)

### Features

- **workflow**: Simplify PR merge process with one-command automation
  ([`b8ea2db`](https://github.com/sensiloles/telegram-bot-stack/commit/b8ea2db8df61f4c01f05fa24f4857dd3f537fe1d))

### Testing

- **storage**: Enable all skipped tests and increase coverage to 83.91%
  ([`3acecfb`](https://github.com/sensiloles/telegram-bot-stack/commit/3acecfbaaf7a8ba361d67b0cab1890a6d34c0805))

## v1.0.0 (2025-11-17)

### Bug Fixes

- **ci**: Remove output dependencies in release workflow
  ([`298c968`](https://github.com/sensiloles/telegram-bot-stack/commit/298c9684d5618ad4953df6f6f54dc94a3d8e6e2e))

- **ci**: Use correct semantic-release command
  ([`63f87ae`](https://github.com/sensiloles/telegram-bot-stack/commit/63f87aedcb764fc5000b2bc906502ba283810ab0))

- **ci**: Use direct semantic-release CLI instead of Docker action
  ([`4d05ea0`](https://github.com/sensiloles/telegram-bot-stack/commit/4d05ea0e2f3b8fc7503b8f865c9ee710ec27df50))

- **release**: Add python-semantic-release configuration
  ([`6642dc8`](https://github.com/sensiloles/telegram-bot-stack/commit/6642dc85f7b44a84824173f1fb1aadaac3ace7cc))

- **workflow**: Improve PR creation error handling and add token guide
  ([`29dad27`](https://github.com/sensiloles/telegram-bot-stack/commit/29dad2733ed5413dcda5483346aed5ad921b9437))

### Documentation

- Add comprehensive installation guide
  ([`0db38e9`](https://github.com/sensiloles/telegram-bot-stack/commit/0db38e9775bb1cc26d06a6cba545ab21243a0506))

- Add workflow configuration quick guide
  ([`7f7245b`](https://github.com/sensiloles/telegram-bot-stack/commit/7f7245b0260141a1e08c4875e0fd4e0afee4009d))

- **workflow**: Add Git Flow rules and PR automation
  ([`29dad27`](https://github.com/sensiloles/telegram-bot-stack/commit/29dad2733ed5413dcda5483346aed5ad921b9437))

### Features

- **workflow**: Implement GitHub Flow with automatic releases
  ([`613e615`](https://github.com/sensiloles/telegram-bot-stack/commit/613e6158dd84e9faa9b875c0edadc5dba89b6761))

### Breaking Changes

- **workflow**: Direct pushes to main will be blocked after branch protection is enabled

## v0.1.0 (2025-11-17)

- Initial Release
