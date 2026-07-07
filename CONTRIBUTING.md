# Contributing to Claude Local Stack

Thank you for your interest in contributing! This guide will help you get started.

## 🚀 Getting Started

1. **Fork** the repository
2. **Clone** your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/local-llm-stack.git
   cd local-llm-stack
   ```
3. **Create a feature branch:**
   ```bash
   git checkout -b feat/your-feature-name
   ```

## 📋 Development Workflow

### Prerequisites

- Docker & Docker Compose
- Python 3.8+
- Git with pre-commit hooks configured:
  ```bash
  pip install pre-commit commitizen
  pre-commit install
  pre-commit install --hook-type pre-push
  ```

### Making Changes

1. **Branch naming convention:**
   - Features: `feat/description`
   - Docs: `docs/description`
   - Fixes: `fix/description`
   - Tests: `test/description`

2. **Commit messages** follow [Conventional Commits](https://www.conventionalcommits.org/):
   ```
   feat: add new feature
   fix: resolve bug in component
   docs: update architecture guide
   test: add unit tests for X
   ```

3. **Code quality:**
   - Pre-commit hooks validate automatically
   - Run manually: `pre-commit run --all-files`
    - Editors should respect the repository formatting rules in [`.editorconfig`](.editorconfig)

### Testing Your Changes

Before submitting a PR:

```bash
# Verify Docker Compose config
docker compose -f docker\docker-compose.yml --env-file docker\.env config

# Run smoke tests
powershell -ExecutionPolicy Bypass -File scripts\smoke-test.ps1

# Check logs for issues
docker compose -f docker\docker-compose.yml --env-file docker\.env logs -f
```

## 📝 Submitting Changes

1. **Push your branch:**
   ```bash
   git push origin feat/your-feature-name
   ```

2. **Open a Pull Request** on GitHub with:
   - Clear title (following Conventional Commits)
   - Description of changes
   - Link to related issues (if any)
   - Screenshots/logs for UI/behavior changes

3. **Address review feedback:**
   - Keep commits atomic (one logical change per commit)
   - Respond constructively to suggestions

## 🏗️ Project Structure

```
claude-local-stack/
├── docker/              # Docker configs and Dockerfile
├── docs/                # Documentation
├── scripts/             # Utility scripts (smoke tests, etc.)
├── claude/              # Claude Code settings
├── .github/             # GitHub templates and workflows
├── env.example          # Template environment variables
└── README.md            # Main documentation
```

## 🐛 Reporting Bugs

1. **Search existing issues** first
2. **Use the bug report template** (auto-filled on GitHub)
3. **Include:**
   - Docker version
   - OS and hardware (CPU/GPU)
   - Steps to reproduce
   - Expected vs. actual behavior
   - Relevant logs

For general usage questions and support routing, see [SUPPORT.md](SUPPORT.md).

## ✨ Suggesting Enhancements

1. **Describe** the problem you're trying to solve
2. **Explain** your proposed solution
3. **Show** examples of similar implementations
4. **Link** related issues/discussions

Security-related reports must follow [SECURITY.md](SECURITY.md) and should not be filed as public issues.

## 📚 Documentation

- **User docs:** `docs/` folder (Markdown)
- **Code comments:** Inline explanations for complex logic
- **Docstrings:** Python/Shell scripts should have headers

When adding features, **update docs simultaneously**.

## 🔄 Release Process

Maintainers will:
1. Review and merge PRs
2. Tag releases with semantic versioning (`v1.2.3`)
3. Update CHANGELOG (auto-generated from commits)

## 📞 Questions?

- **GitHub Issues:** For bug reports and feature requests
- **Discussions:** For questions and brainstorming
- **README:** For quick start and architecture overview
- **Support guide:** [SUPPORT.md](SUPPORT.md)
- **Maintainers:** [MAINTAINERS.md](MAINTAINERS.md)

---

**Thank you for contributing to Claude Local Stack!** 🎉
