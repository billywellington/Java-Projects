#!/usr/bin/env python3
"""
Cross-ecosystem dependency audit helper.

- Scans the repository for common package manager manifests.
- Prints a simple summary and can generate a Markdown report file similar to dependency-audit-<YYYY-MM-DD>.md
- Designed to be conservative: it never auto-upgrades. It only reports.

Usage:
  python tools/dependency_audit.py --output dependency-audit-YYYY-MM-DD.md

Note: Actual vulnerability scanning depends on ecosystem-specific tools being installed
(e.g., npm audit, pnpm audit, pip-audit, safety, poetry audit, mvn versions:display-dependency-updates,
Gradle versions plugin, osv-scanner, etc.). This helper focuses on discovery and report formatting.
"""

import argparse
import datetime
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Manifest patterns per ecosystem
MANIFESTS = {
    "java-maven": ["pom.xml"],
    "java-gradle": ["build.gradle", "build.gradle.kts", "gradle.properties"],
    "node": ["package.json", "yarn.lock", "pnpm-lock.yaml"],
    "python": ["requirements.txt", "Pipfile", "Pipfile.lock", "pyproject.toml", "poetry.lock"],
    ".net": ["packages.config", "Directory.Packages.props"],
    "dotnet-csproj": [".csproj"],
    "go": ["go.mod", "go.sum"],
    "rust": ["Cargo.toml", "Cargo.lock"],
    "php": ["composer.json", "composer.lock"],
    "ruby": ["Gemfile", "Gemfile.lock"],
}

SKIP_DIRS = {
    ".git", ".idea", "out", "build", "dist", "node_modules", ".venv", "venv", "__pycache__"
}


def find_manifests(root: Path) -> Dict[str, List[Path]]:
    found: Dict[str, List[Path]] = {eco: [] for eco in MANIFESTS}
    for dirpath, dirnames, filenames in os.walk(root):
        # prune unwanted directories
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            for eco, patterns in MANIFESTS.items():
                for pat in patterns:
                    if pat.startswith('.') and fname.endswith(pat):
                        # e.g., .csproj handled differently below
                        pass
                    if pat == ".csproj":
                        if fname.lower().endswith(".csproj"):
                            found[eco].append(Path(dirpath) / fname)
                    elif fname == pat:
                        found[eco].append(Path(dirpath) / fname)
    # cleanup empty ecosystems
    return {eco: paths for eco, paths in found.items() if paths}


def format_report(root: Path, manifests: Dict[str, List[Path]]) -> str:
    today = datetime.date.today().isoformat()
    lines: List[str] = []
    lines.append(f"# Dependency Audit Summary ({today})")
    lines.append("")
    lines.append("Scope: Audit all dependencies across all package managers in this repository. Report vulnerabilities (IDs, severity, fixed versions) and available updates. Skip/batch majors and note breaking changes.")
    lines.append("")
    lines.append(f"Repository root: {root}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 1) Package manager manifests discovered")
    lines.append("")
    if not manifests:
        lines.append("No known dependency manifests were found in this repository. Searched for common files including:")
        lines.extend([
            "- Java: pom.xml, build.gradle, build.gradle.kts, gradle.properties",
            "- JavaScript/TypeScript: package.json, yarn.lock, pnpm-lock.yaml",
            "- Python: requirements.txt, requirements-*.txt, Pipfile, Pipfile.lock, pyproject.toml, poetry.lock",
            "- .NET: *.csproj, packages.config, Directory.Packages.props",
            "- Go: go.mod, go.sum",
            "- Rust: Cargo.toml, Cargo.lock",
            "- PHP: composer.json, composer.lock",
            "- Ruby: Gemfile, Gemfile.lock",
        ])
        lines.append("")
        lines.append("Result: 0 manifests found. This repository currently contains plain source/projects without a build tool configuration.")
    else:
        total = sum(len(v) for v in manifests.values())
        lines.append(f"Found {total} manifest file(s) across ecosystems:")
        for eco, paths in manifests.items():
            lines.append(f"- {eco}: {len(paths)} file(s)")
            for p in paths:
                lines.append(f"  - {p.relative_to(root)}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 2) Vulnerability findings")
    lines.append("")
    if not manifests:
        lines.append("None. No manifests were found, so no third-party dependencies could be resolved or audited.")
        lines.append("")
        lines.append("If/when manifests are added, this section will list each vulnerable package per ecosystem with:")
        lines.extend([
            "- Advisory ID / CVE",
            "- Severity (CVSS/qualitative)",
            "- Affected range",
            "- Fixed versions",
        ])
    else:
        lines.append("This script does not execute ecosystem-specific scanners by default. Recommended tools:")
        lines.extend([
            "- Node: npm audit --production | yarn npm audit | pnpm audit | osv-scanner",
            "- Python: pip-audit | safety | poetry audit | osv-scanner",
            "- Java (Maven): mvn versions:display-dependency-updates; for CVEs use OWASP Dependency-Check or osv-scanner",
            "- Java (Gradle): Gradle Versions Plugin; for CVEs use OWASP Dependency-Check or osv-scanner",
            "- .NET: dotnet list package --vulnerable",
            "- Go: govulncheck | osv-scanner",
            "- Rust: cargo audit",
            "- PHP: symfony/security-checker or composer audit",
            "- Ruby: bundler-audit",
        ])
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 3) Available updates")
    lines.append("")
    if not manifests:
        lines.append("None. Without manifests/lockfiles, there are no dependency versions to check for updates.")
    else:
        lines.append("For updates, prefer ecosystem-native tools (examples):")
        lines.extend([
            "- Node: npm outdated | yarn outdated | pnpm outdated",
            "- Python: pip list --outdated | poetry update --dry-run",
            "- Maven: mvn versions:display-dependency-updates",
            "- Gradle: ./gradlew dependencyUpdates",
            "- .NET: dotnet list package --outdated",
        ])
        lines.append("")
        lines.append("Policy: apply patch/minor updates where tests pass; batch major upgrades and review breaking changes before merging.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 4) Notes on major versions and breaking changes")
    lines.append("")
    if not manifests:
        lines.append("N/A for this run. Once manifests exist, major updates will be grouped (batched) and annotated with breaking-change highlights and migration references.")
    else:
        lines.append("Major updates should be grouped by ecosystem/module with links to release notes and migration guides.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 5) Next steps")
    lines.append("")
    if not manifests:
        lines.extend([
            "- If you plan to adopt a build tool (recommended):",
            "  - For Java, add either Gradle (build.gradle) or Maven (pom.xml). Once present, re-run the audit to surface vulnerabilities and updates.",
            "  - If other ecosystems are added (JavaScript, Python, etc.), the audit script can include them automatically.",
        ])
    else:
        lines.extend([
            "- Run the suggested scanners above per ecosystem.",
            "- Apply patch/minor updates where test suites pass.",
            "- Batch majors and review breaking changes before merging.",
        ])
    lines.append("")
    lines.append(f"Generated automatically on {today}.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Cross-ecosystem dependency audit helper")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]), help="Repository root (defaults to project root)")
    parser.add_argument("--output", default="", help="Optional path to write Markdown report")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    manifests = find_manifests(root)
    report = format_report(root, manifests)

    if args.output:
        out_path = Path(args.output)
        if not out_path.is_absolute():
            out_path = root / out_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report, encoding="utf-8")
        print(f"Wrote audit report to: {out_path}")
    else:
        print(report)


if __name__ == "__main__":
    main()
