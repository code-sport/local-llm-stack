# Security Policy

## Reporting a Vulnerability

**Please DO NOT create a public GitHub issue for security vulnerabilities.**

If you discover a security issue, please report it privately to the maintainers.

### Reporting Process

1. **Email:** Include "SECURITY" in the subject
2. **Details to include:**
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Your contact information
   - Whether you'd like credit in the security advisory

Maintainers will:
- Acknowledge receipt within 48 hours
- Investigate and assess the severity
- Work on a fix
- Coordinate disclosure timeline

## Security Best Practices

When using Claude Local Stack:

### 🔒 Network Security
- Run behind a firewall if exposed to external networks
- Use authentication (Open WebUI has built-in user management)
- Do not expose ports directly to the internet without a reverse proxy

### 🗝️ API Keys & Secrets
- Never commit `.env` files with real values
- Use `.env.example` template for sharing
- Rotate API keys regularly
- Use Docker secrets for production deployments

### 🐳 Container Security
- Keep Docker images updated
- Run containers with minimal privileges
- Use read-only filesystems where possible
- Scan images for vulnerabilities: `docker scan ollama/ollama`

### 📦 Dependency Updates
- Dependencies are monitored by Dependabot
- Review security updates in PRs
- Test updates before deploying to production

## Supported Versions

| Version | Supported | Note |
|---------|-----------|------|
| Latest | ✅ Yes | Actively maintained |
| Previous | ⚠️ Limited | Bug fixes only |
| Older | ❌ No | Use at own risk |

## Known Security Considerations

1. **Local Models:** Open WebUI stores conversations locally by default
2. **Network:** Services communicate via internal Docker network (secure)
3. **GPU:** NVIDIA GPU access requires host permissions
4. **Logs:** Ensure logs don't contain sensitive information

## Security Updates

- **Frequency:** Checked on each commit (Dependabot)
- **Policy:** Security fixes have priority
- **Notification:** GitHub security advisories and PRs

## Questions?

- 📖 [Security Best Practices](docs/configuration.md#security)
- 🐛 [Report Vulnerability](#reporting-a-vulnerability)
- 📞 GitHub Issues (non-security only)
