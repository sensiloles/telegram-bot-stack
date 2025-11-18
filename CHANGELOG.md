# CHANGELOG

<!-- version list -->

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
