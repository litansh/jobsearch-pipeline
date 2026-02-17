# Changelog

All notable changes to the Job Search Pipeline will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Resume analysis and automatic tailoring
- Multi-user support with separate profiles
- Job application tracking CRM
- Interview preparation with AI
- Salary negotiation insights

## [0.3.0] - 2026-02-17

### Added
- CI workflow for lint and test (.github/workflows/ci.yml)
- Demo Mode documentation: test pipeline without API keys
- Local Run vs Scheduled Run sections in README
- Integration tests that don't require API access
- CODE_OF_CONDUCT.md for community guidelines
- CHANGELOG.md for version tracking

### Changed
- README restructured with 3 clear quickstart paths
- Clarified which features require API keys
- Improved documentation for GitHub Actions automation

### Security
- All credentials removed from repository
- Comprehensive .gitignore for secrets
- Security policy documented

## [0.2.0] - 2026-02-01

### Added
- Complete README refactor with value proposition
- Architecture documentation (docs/design.md)
- 12 architectural decisions documented
- MIT License

### Changed
- README reduced to focus on core value
- Impact metrics: "40+ hours/month saved"
- Clear scoring algorithm explanation
- Enhanced configuration documentation

### Security
- **CRITICAL:** Removed exposed Telegram bot token from set_railway_vars.sh
- Added instructions for manual credential setup
- Security best practices documented

## [0.1.0] - 2025-12-01

### Added
- 5 parallel job crawlers:
  - Greenhouse/Lever API integration
  - Israeli job boards (Drushim, AllJobs, LinkedIn Israel)
  - LinkedIn Jobs workaround
  - Direct company career pages
  - Known DevOps companies list
- OpenAI embeddings for semantic job scoring
- Telegram bot for daily digests
- Interactive buttons (Apply, Snooze, Skip, Cover Letter)
- Job deduplication and filtering
- Age tracking (1-14 days)
- Leadership-only role filtering
- Makefile for CLI automation
- GitHub Actions for scheduled runs
- Cover letter generation with GPT-4

### Infrastructure
- Railway deployment configuration
- GitHub Actions workflows (daily, on-demand, telegram deploy)
- Comprehensive test suite
- Configuration management

[Unreleased]: https://github.com/litansh/jobsearch-pipeline/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/litansh/jobsearch-pipeline/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/litansh/jobsearch-pipeline/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/litansh/jobsearch-pipeline/releases/tag/v0.1.0
