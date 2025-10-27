# GitHub Repository Setup

## Quick Setup

After unzipping this repository locally:

```bash
# 1. Navigate to the directory
cd inventory-system

# 2. Initialize remote (replace with your GitHub repo URL)
git remote add origin https://github.com/YOUR_USERNAME/homelab-inventory.git

# 3. Verify remote
git remote -v

# 4. Push to GitHub
git push -u origin master

# Or if you want to use 'main' as the branch name:
git branch -M main
git push -u origin main
```

## Creating the GitHub Repository

1. Go to https://github.com/new
2. Repository name: `homelab-inventory` (or your preferred name)
3. Description: "AI-powered inventory management system for homelab/makerspace with voice interface support"
4. **Choose Public or Private**
5. **Do NOT initialize with README** (we already have one)
6. Click "Create repository"

## Repository Settings (Recommended)

### Topics/Tags
Add these topics to help others find your project:
- `inventory-management`
- `homelab`
- `makerspace`
- `flask`
- `postgresql`
- `docker`
- `ai`
- `voice-interface`
- `semantic-search`
- `python`

### About Section
```
AI-powered inventory management system for homelab and makerspace environments. 
Features semantic search, duplicate detection, CLI interface, and voice control 
with natural language processing.
```

### GitHub Features to Enable
- ✅ Issues (for bug reports and feature requests)
- ✅ Discussions (for Q&A and community)
- ✅ Projects (for roadmap tracking)
- ✅ Wiki (for extended documentation)

### Branch Protection (Optional)
For `main/master` branch:
- Require pull request reviews
- Require status checks to pass
- Include administrators

### Labels (Suggested)
Create these labels for better issue organization:
- `phase-1-ui` - Enhanced UI features
- `phase-2-locations` - Smart location management  
- `phase-3-duplicates` - Duplicate detection
- `phase-4-ai` - AI/ML features
- `phase-5-cli` - CLI interface
- `phase-6-voice` - Voice interface
- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Documentation improvements
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed

## Project Structure on GitHub

```
homelab-inventory/
├── .github/
│   ├── workflows/          # CI/CD pipelines (future)
│   ├── ISSUE_TEMPLATE/     # Issue templates (future)
│   └── PULL_REQUEST_TEMPLATE.md
├── backend/
├── frontend/
├── docs/                   # Extended docs (future)
├── tests/                  # Test suite (future)
└── ... (all other files)
```

## Cloning for Contributors

Others can clone your repository:
```bash
git clone https://github.com/YOUR_USERNAME/homelab-inventory.git
cd homelab-inventory
./setup.sh
```

## Keeping Up to Date

After pushing to GitHub, contributors can:
```bash
# Get latest changes
git pull origin main

# Update their deployment
docker compose pull
docker compose up -d --build
```

## Release Process

When ready to create a release:

```bash
# Tag the current version
git tag -a v1.1.0 -m "Version 1.1.0 - Enhanced UI Release"
git push origin v1.1.0

# Create release on GitHub
# Go to: Releases → Draft a new release
# Select the tag, add release notes from CHANGELOG.md
```

## Continuous Integration (Future)

Consider adding `.github/workflows/ci.yml`:
```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build images
        run: docker compose build
      - name: Run tests
        run: docker compose run backend pytest
```

## Security

### Dependabot (Automatic Dependency Updates)
Enable in Settings → Security → Dependabot

### Security Advisories
Enable in Settings → Security → Enable vulnerability alerts

### Secrets
Never commit to the repository:
- ❌ `.env` file
- ❌ Database credentials
- ❌ API keys
- ❌ SSL certificates

Use `.gitignore` (already configured) and GitHub Secrets for CI/CD.

## Community

### Issue Templates
Create `.github/ISSUE_TEMPLATE/bug_report.md` and `feature_request.md`

### Pull Request Template  
Create `.github/PULL_REQUEST_TEMPLATE.md`

### Code of Conduct
Consider adding `CODE_OF_CONDUCT.md`

## Promotion

Share your project on:
- Reddit: r/homelab, r/selfhosted
- Hacker News
- Product Hunt
- DEV Community
- Twitter/X with hashtags: #homelab #makerspace #opensource

---

**Need help?** Check out the [GitHub Docs](https://docs.github.com/)
