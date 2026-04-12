# Development Workflow

How we build, test, and release Voice Separation.

## Branching Strategy

We use a simplified Git flow:

```
main          ← Production-ready code
├── feature/*  ← Feature branches
└── fix/*      ← Bug fix branches
```

### Main Branch

* Protected — requires PR for merge
* Always deployable
* Tags for releases (v1.0.0, v1.0.1, etc.)

### Feature Branches

Create from `main` for new features:
```bash
git checkout main
git pull
git checkout -b feature/my-feature
```

### Fix Branches

Create from `main` for bug fixes:
```bash
git checkout main
git pull
git checkout -b fix/issue-123
```

## Development Cycle

### 1. Plan

* Create an issue or use existing one
* Discuss approach in comments
* Assign to yourself

### 2. Develop

```bash
# Create branch
git checkout -b feature/my-feature

# Make changes
# ... edit files ...

# Test locally
npm start

# Run tests (when implemented)
pytest tests/
```

### 3. Commit

Commit frequently with clear messages:
```bash
git add .
git commit -m "Add: feature to export multiple formats"
```

**Commit conventions:**
* `Add:` — New features
* `Fix:` — Bug fixes
* `Refactor:` — Code changes without behavior change
* `Docs:` — Documentation updates
* `Test:` — Test additions/changes
* `Chore:` — Maintenance tasks

### 4. Create Pull Request

```bash
git push origin feature/my-feature
```

Then open a PR on GitHub with:
* Description of changes
* Link to related issue
* Checklist from PR template

### 5. Review

* Maintainer reviews code
* Request changes or approve
* Discuss in comments

### 6. Merge

* Squash and merge to `main`
* Delete feature branch
* Update `CHANGELOG.md`

## Testing

### Unit Tests (Not Yet Implemented)

When tests are added:
```bash
pytest tests/                    # Run all tests
pytest tests/test_pipeline.py    # Run specific file
pytest --cov=src tests/          # With coverage
```

### Manual Testing Checklist

Before merging:
* [ ] App launches without errors
* [ ] File upload works
* [ ] Processing completes
* [ ] Output files are generated
* [ ] Audio player works
* [ ] Cancel button stops processing
* [ ] Reset button clears state

### Integration Tests

Test the full pipeline:
```bash
# Download sample audio
wget https://example.com/sample-podcast.mp3

# Run CLI
python src/voice_isolation.py sample-podcast.mp3

# Verify output
ls data/voice_separation_output/
```

## Release Process

### 1. Prepare Release

```bash
# Ensure main is up to date
git checkout main
git pull

# Update version
npm version minor  # or patch, major

# Update CHANGELOG.md
# Add release notes with date
```

### 2. Tag and Push

```bash
git add .
git commit -m "Release v1.1.0"
git tag v1.1.0
git push origin main --tags
```

### 3. Build

```bash
npm run build:linux
npm run build:mac
npm run build:windows
```

### 4. Publish

Create GitHub release:
* Select tag
* Paste release notes
* Attach binaries
* Publish

## Code Review

### Reviewer Checklist

* [ ] Code follows conventions
* [ ] No obvious bugs
* [ ] Tests added (when applicable)
* [ ] Documentation updated
* [ ] CHANGELOG.md updated
* [ ] No secrets committed

### Author Response

* Address all feedback
* Update PR as needed
* Request re-review when ready

## Continuous Integration

### GitHub Actions (Future)

When CI is configured:
* Run tests on every push
* Build on release tags
* Deploy to release channel

### Example Workflow

```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.8'
      - run: pip install -r requirements.txt
      - run: pytest tests/
```

## Version Bumping

Automated with npm:
```bash
npm version patch   # 1.0.0 → 1.0.1 (bug fixes)
npm version minor   # 1.0.0 → 1.1.0 (new features)
npm version major   # 1.0.0 → 2.0.0 (breaking changes)
```

This updates `package.json` and creates a git tag.

## Hotfixes

For critical bugs in production:

```bash
# Create hotfix branch from release tag
git checkout v1.0.0
git checkout -b hotfix/critical-bug

# Fix and test
# ...

# Merge to main and release tag
git checkout main
git merge hotfix/critical-bug
git tag v1.0.1

# Also merge back to any feature branches
```

## Housekeeping

### Regular Tasks

* Update dependencies: `pip install --upgrade -r requirements.txt`
* Update npm packages: `npm update`
* Archive old releases: Move to `archive/` folder
* Clean up branches: Delete merged branches

### Dependency Updates

Check for updates monthly:
```bash
pip list --outdated
npm outdated
```

Update with caution — test thoroughly after updating PyTorch, Electron, or Demucs.

## Communication

* **Issues:** Bug reports and feature requests
* **PRs:** Code changes and reviews
* **Releases:** Announcements in CHANGELOG.md
* **Discussions:** Future: General questions and ideas
