<!--
Sync Impact Report (2025-09-28):
- Version change: 1.0.0 → 1.0.1 (Remove monitoring requirements)
- Modified sections:
  - Compliance Monitoring → Compliance Enforcement (simplified)
  - Removed dashboard and monitoring requirements
- Templates requiring updates: ✅ None
- Follow-up TODOs: None
-->

# TradingView Strategy Repository Constitution

## Core Principles

### I. Code Quality First
**All code MUST meet professional standards**. Every piece of code written must be maintainable, readable, and follow established patterns. Code reviews SHALL enforce consistent style, proper abstractions, and clear naming conventions. Technical debt is unacceptable - refactor immediately when identified.

**Rationale**: Poor code quality compounds exponentially. A single compromise in standards leads to cascading maintenance issues that cost 10x more to fix later than to implement correctly initially.

### II. Test Coverage Excellence
**Maintain 95% test coverage minimum across all Python modules**. Every function, method, and code path MUST have comprehensive tests including edge cases, error conditions, and integration scenarios. Pine Script strategies MUST pass all validation tests before deployment. Test failures block all merges without exception.

**Rationale**: Tests are the only guarantee of correctness. Without 95% coverage, we cannot confidently refactor, optimize, or extend functionality. Untested code is broken code waiting to be discovered.

### III. Architecture Integrity
**Enforce strict separation of concerns and modular design**. Each module SHALL have a single, well-defined responsibility. Dependencies MUST flow in one direction only (no circular dependencies). All Pine Script strategies MUST follow the established boilerplate template structure. Utility libraries SHALL be reusable and self-contained.

**Rationale**: Clean architecture enables parallel development, simplifies debugging, and allows independent module updates. Mixed responsibilities create coupling that makes changes risky and expensive.

### IV. Linting Compliance
**Zero tolerance for linting violations**. All code MUST pass Ruff, Black, isort, and mypy checks before commit. Pre-commit hooks SHALL NOT be bypassed under any circumstances. Pine Script MUST pass custom validator checks for v6 syntax compliance, risk management implementation, and structural requirements.

**Rationale**: Automated quality checks catch issues before human review. Bypassing linters introduces inconsistencies that degrade codebase quality and developer productivity over time.

### V. No Unnecessary Code
**Write only essential code - YAGNI strictly enforced**. Every line of code MUST serve a current, validated requirement. Speculative features, unused functions, and commented-out code SHALL be rejected. Dead code MUST be deleted immediately upon discovery. Complexity requires written justification.

**Rationale**: Unnecessary code increases maintenance burden, confuses developers, and hides bugs. Every line written is a line that must be tested, documented, and maintained forever unless actively removed.

## Development Standards

### Code Review Requirements
- ALL pull requests require approval from at least one reviewer
- Reviews MUST verify: test coverage ≥95%, all lints pass, no dead code
- Breaking changes require migration plan and deprecation notices
- Performance regressions require justification or optimization

### Documentation Standards
- Every public function requires docstring with parameters, returns, and examples
- Pine Script strategies MUST include trading logic explanation
- Complex algorithms require inline comments explaining approach
- README updates required for new features or changed workflows

### Testing Requirements
- Unit tests for all functions with multiple test cases per function
- Integration tests for module interactions
- End-to-end tests for complete workflows
- Performance benchmarks for critical paths
- Pine Script validation tests for all strategies

## Quality Gates

### Pre-Commit Checks (Automated)
1. **Python formatting**: Black (line-length=100)
2. **Import sorting**: isort (profile=black)
3. **Linting**: Ruff (E, W, F, I, B, C4, UP rules)
4. **Type checking**: mypy (warn_return_any=true)
5. **Pine Script validation**: Custom validator.py

### CI/CD Pipeline (Required)
1. **Matrix testing**: Python 3.9, 3.10, 3.11
2. **Coverage enforcement**: Minimum 95% with failure on decrease
3. **Security scanning**: Trivy vulnerability detection
4. **Pine Script verification**: All strategies validated
5. **Performance tests**: No regression >10% without approval

### Merge Criteria
- ✅ All CI checks green
- ✅ Test coverage ≥95%
- ✅ Zero linting violations
- ✅ Approved by reviewer
- ✅ No merge conflicts
- ✅ Documentation updated

## Governance

### Amendment Process
1. **Proposal**: Document proposed change with rationale
2. **Review**: Team discussion with impact analysis
3. **Approval**: Consensus or majority vote if disputed
4. **Migration**: Update all affected code and documentation
5. **Verification**: Audit compliance within 30 days

### Compliance Enforcement
- **Continuous**: Pre-commit and CI enforcement only
- **No dashboards or monitoring tools required**
- **Coverage verified at commit time via CI pipeline**

### Violation Response
1. **First violation**: Immediate fix required
2. **Repeated violations**: Code review privileges suspended
3. **Systematic violations**: Architecture refactoring mandated

### Version Policy
Constitution versioning follows semantic versioning:
- **MAJOR**: Principle removal or fundamental change
- **MINOR**: New principle or section addition
- **PATCH**: Clarifications and minor updates

**Version**: 1.0.1 | **Ratified**: 2025-09-28 | **Last Amended**: 2025-09-28
