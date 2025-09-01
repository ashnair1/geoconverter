#!/usr/bin/env python3
"""
GDAL Release Monitor for geoconverter

This script monitors GDAL releases and alerts when new versions are available
that may require compatibility testing.
"""

import sys
from datetime import datetime
from typing import List

import requests
from packaging import version


def get_latest_gdal_releases() -> List[dict]:
    """Fetch latest GDAL releases from GitHub API."""
    url = "https://api.github.com/repos/OSGeo/gdal/releases"

    try:
        response = requests.get(url)
        response.raise_for_status()
        releases = response.json()

        # Filter and parse releases
        parsed_releases = []
        for release in releases[:10]:  # Get last 10 releases
            tag_name = release["tag_name"]
            # Skip non-version tags
            if not tag_name.startswith("v"):
                continue

            version_str = tag_name[1:]  # Remove 'v' prefix
            try:
                parsed_version = version.parse(version_str)
                parsed_releases.append(
                    {
                        "version": version_str,
                        "parsed_version": parsed_version,
                        "published_at": release["published_at"],
                        "prerelease": release["prerelease"],
                        "html_url": release["html_url"],
                        "body": release.get("body", "")[
                            :500
                        ],  # First 500 chars of release notes
                    }
                )
            except version.InvalidVersion:
                continue

        return sorted(parsed_releases, key=lambda x: x["parsed_version"], reverse=True)

    except requests.RequestException as e:
        print(f"Error fetching releases: {e}")
        return []


def check_compatibility_status(gdal_version_str: str) -> str:
    """Check if a GDAL version is in our tested compatibility matrix."""
    # These are the versions we currently test
    tested_versions = ["3.8", "3.9", "3.10", "3.11"]

    try:
        gdal_ver = version.parse(gdal_version_str)

        for tested in tested_versions:
            tested_ver = version.parse(tested)
            # Check if it's the same major.minor version
            if (
                gdal_ver.major == tested_ver.major
                and gdal_ver.minor == tested_ver.minor
            ):
                return "tested"

        # Check if it's newer than our latest tested version
        latest_tested = version.parse(max(tested_versions))
        if gdal_ver > latest_tested:
            return "newer"
        else:
            return "older"

    except version.InvalidVersion:
        return "unknown"


def check_breaking_changes(release_body: str) -> List[str]:
    """Check release notes for potential breaking changes."""
    breaking_indicators = [
        "breaking change",
        "api change",
        "incompatible",
        "deprecated",
        "removed",
        "rfc",
        "abi break",
        "backwards",
        "migration",
    ]

    body_lower = release_body.lower()
    found_indicators = [
        indicator for indicator in breaking_indicators if indicator in body_lower
    ]

    return found_indicators


def generate_report() -> int:
    """Generate a compatibility status report."""
    print("=== GDAL Release Compatibility Monitor ===")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    releases = get_latest_gdal_releases()
    if not releases:
        print("❌ Could not fetch GDAL releases")
        return 1

    print("Latest GDAL Releases:")
    print("-" * 80)

    needs_attention = []

    for release in releases:
        version_str = release["version"]
        status = check_compatibility_status(version_str)
        breaking_changes = check_breaking_changes(release["body"])

        # Status indicators
        if status == "tested":
            status_icon = "✅"
        elif status == "newer":
            status_icon = "⚠️ "
            needs_attention.append((version_str, "newer version"))
        elif status == "older":
            status_icon = "ℹ️ "
        else:
            status_icon = "❓"

        # Breaking change indicator
        breaking_icon = "🚨" if breaking_changes else "  "

        print(
            f"{status_icon} {breaking_icon} GDAL {version_str:8} | {status:6} | {release['published_at'][:10]}"
        )

        if breaking_changes:
            print(f"    Breaking change indicators: {', '.join(breaking_changes)}")
            needs_attention.append(
                (
                    version_str,
                    f"potential breaking changes: {', '.join(breaking_changes)}",
                )
            )

        if release["prerelease"]:
            print("    (Prerelease)")

    print("-" * 80)

    # Summary and recommendations
    if needs_attention:
        print("\n⚠️  ATTENTION REQUIRED:")
        for version_str, reason in needs_attention:
            print(f"   • GDAL {version_str}: {reason}")

        print("\nRECOMMENDED ACTIONS:")
        print("1. Review release notes for breaking changes")
        print("2. Update GitHub Actions matrix to include new versions")
        print("3. Run compatibility tests: ./scripts/test_gdal_compatibility.sh")
        print("4. Update GDAL compatibility documentation")

        return 1
    else:
        print("\n✅ All recent GDAL releases are covered by compatibility testing")
        return 0


def update_github_actions() -> None:
    """Suggest updates to GitHub Actions workflow based on new releases."""
    releases = get_latest_gdal_releases()
    if not releases:
        return

    # Find versions that are stable and newer than what we test
    newer_stable = []
    for release in releases:
        if not release["prerelease"]:
            status = check_compatibility_status(release["version"])
            if status == "newer":
                # Only suggest minor versions (not patch versions)
                ver = version.parse(release["version"])
                version_key = f"{ver.major}.{ver.minor}"
                if version_key not in newer_stable:
                    newer_stable.append(version_key)

    if newer_stable:
        print("\n📝 SUGGESTED GITHUB ACTIONS UPDATES:")
        print("Add these versions to .github/workflows/gdal-compatibility.yml:")
        current_matrix = "gdal-version: ['3.8', '3.9', '3.10', '3.11']"
        new_versions = ["3.8", "3.9", "3.10", "3.11"] + newer_stable
        new_matrix = f"gdal-version: {new_versions}"
        print(f"  Current: {current_matrix}")
        print(f"  Updated: {new_matrix}")


if __name__ == "__main__":
    exit_code = generate_report()
    update_github_actions()
    sys.exit(exit_code)
