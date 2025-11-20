# Contributing to Authelia Walled Garden

Thank you for your interest in contributing to this project! This reference architecture helps the community deploy secure, authenticated service gateways using Authelia and Caddy.

## What This Project Is

This is a **reference architecture and documentation project**, not a software product with ongoing development. Contributions focus on improving documentation, adding service integration examples, and sharing best practices.

## Types of Contributions Welcome

### 📝 Documentation Improvements
- Fix typos, clarify confusing sections
- Improve existing guides and tutorials
- Add troubleshooting tips from your experience
- Update screenshots with better examples

### 🔧 Example Service Integrations
- Add guides for popular self-hosted services
- Share working configurations for specific applications
- Document edge cases and gotchas you've encountered

### 💡 Configuration Examples
- Alternative setups (LDAP backend, Redis sessions, PostgreSQL)
- Different authentication policies
- Multi-domain configurations

### 🐛 Bug Fixes
- Corrections to example configurations
- Fix broken links in documentation
- Update deprecated configuration syntax

### 🎨 Visual Improvements
- Better screenshots demonstrating features
- Updated architecture diagrams
- Dashboard UI improvements

## What We Don't Accept

- **New Features**: This is a reference, not active development
- **Breaking Changes**: Stability is priority for those using this guide
- **Proprietary Integrations**: Keep examples for open-source/self-hosted services
- **Production Secrets**: Never submit real secrets or identifying information

## How to Contribute

### 1. Fork the Repository

Click the "Fork" button at the top of this repository.

### 2. Clone Your Fork

```bash
git clone https://github.com/your-username/authelia-walled-garden.git
cd authelia-walled-garden
```

### 3. Create a Feature Branch

```bash
git checkout -b feature/your-improvement
```

Use descriptive branch names:
- `docs/clarify-authelia-setup`
- `example/add-jellyfin-integration`
- `fix/broken-link-in-readme`

### 4. Make Your Changes

**For Documentation**:
- Use clear, concise language
- Add code blocks with proper syntax highlighting
- Include before/after examples when fixing issues
- Test all commands and configurations

**For Examples**:
- Ensure all secrets are placeholders (REPLACE_WITH_YOUR_SECRET)
- Replace any real domains with example.com
- Add helpful comments explaining configuration
- Test the configuration works as described

**For Configurations**:
- Validate with tools (e.g., `scripts/check-config.sh` for Authelia)
- Document any prerequisites or dependencies
- Include troubleshooting tips

### 5. Test Your Changes

Before submitting:

#### Documentation Changes
- [ ] Read through your changes for clarity
- [ ] Check all links work (internal and external)
- [ ] Verify Markdown renders correctly
- [ ] Run spell check

#### Configuration Changes
- [ ] Test configuration in a clean environment
- [ ] Verify no production secrets included
- [ ] Run security validation checks
- [ ] Document any prerequisites

#### Security Validation (Critical)
```bash
# Check for production domains
grep -r "nycapphouse" . | grep -v ".md:"

# Check for real email addresses
grep -r "@" . | grep -v -E "\.md:|example\.com|CONTRIBUTING"

# Check for secrets (base64 strings >40 chars)
grep -rE "[A-Za-z0-9+/]{64,}" . | grep -v -E "REPLACE_WITH|\.md:"

# All commands should return no results
```

### 6. Commit Your Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "docs: clarify Authelia session.domain configuration

- Add explanation of parent domain for SSO
- Include common misconfiguration example
- Add troubleshooting tip for authentication loops"
```

**Commit Message Format**:
- `docs:` for documentation changes
- `example:` for new service examples
- `fix:` for bug fixes
- `style:` for formatting/cosmetic changes

### 7. Push to Your Fork

```bash
git push origin feature/your-improvement
```

### 8. Open a Pull Request

1. Go to the original repository on GitHub
2. Click "New Pull Request"
3. Select your fork and branch
4. Fill out the PR template with:
   - **Description**: What changes you made and why
   - **Testing**: How you tested the changes
   - **Screenshots**: If visual changes (before/after)

## Documentation Style Guide

### Markdown Formatting

**Code Blocks**: Always specify the language
````markdown
```yaml
key: value
```
````

**Internal Links**: Use relative paths
```markdown
See [Architecture Documentation](docs/ARCHITECTURE.md)
```

**External Links**: Use full URLs
```markdown
[Authelia Documentation](https://www.authelia.com/docs/)
```

**Security Warnings**: Use bold and capitalization
```markdown
**IMPORTANT**: Never commit production secrets to version control!
```

### Configuration Examples

Always include:
1. **Comments** explaining each section
2. **Placeholders** for secrets (never real values)
3. **Generation instructions** for secrets
4. **Example domains** (example.com, never real domains)

**Good Example**:
```yaml
# Generate with: openssl rand -base64 64
jwt_secret: REPLACE_WITH_YOUR_GENERATED_SECRET
```

**Bad Example**:
```yaml
jwt_secret: real-secret-value-here
```

### Service Integration Guides

When adding a new service integration, include:

1. **Service Overview**: Brief description and use case
2. **Prerequisites**: Required dependencies or configuration
3. **Docker Compose Configuration**: Complete service definition
4. **Caddyfile Route**: Reverse proxy configuration
5. **Authelia Access Control**: Authentication policy
6. **Dashboard Card**: HTML for dashboard integration
7. **Testing**: How to verify it works
8. **Troubleshooting**: Common issues and solutions

## Pull Request Review Process

1. **Automated Checks**: CI runs security validation
2. **Maintainer Review**: Checks for:
   - No production secrets or identifying information
   - Documentation clarity and accuracy
   - Proper Markdown formatting
   - Working links
   - Tested configurations
3. **Feedback**: May request changes or clarifications
4. **Merge**: Once approved, PR is merged to main

## Code of Conduct

### Our Standards

- **Be Respectful**: Treat all contributors with respect
- **Be Constructive**: Provide helpful feedback, not criticism
- **Be Patient**: Remember everyone is learning
- **Be Inclusive**: Welcome contributions from all skill levels

### Unacceptable Behavior

- Harassment, insults, or discriminatory comments
- Publishing others' private information
- Trolling, inflammatory comments, or personal attacks
- Any conduct inappropriate in a professional setting

### Reporting

Report unacceptable behavior by opening an issue or contacting maintainers directly.

## Questions?

- **General Questions**: Open a [GitHub Discussion](../../discussions)
- **Bug Reports**: Open an [Issue](../../issues)
- **Feature Requests**: Open a Discussion (not Issues)

## Recognition

Contributors are recognized in:
- Git commit history
- Pull request credits
- Future acknowledgments section (if added)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to make this reference architecture better for the community! 🙏
