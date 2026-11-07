"""Platform package snapshot: coverage, counts and filename/command mapping."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from collect_platform_packages import (  # noqa: E402
    PLATFORM_ORDER, SOFTWARE_KINDS, asset_platform, command_platform,
)


class AssetMappingTests(unittest.TestCase):
    def platform(self, name, url="https://example.org/download", topics=None):
        return asset_platform(name, url, topics or [])

    def test_windows_packages(self):
        for name in ("tool-setup.exe", "tool-x64.msi", "tool.msix", "tool-win64.zip"):
            self.assertEqual(self.platform(name), "windows", name)

    def test_macos_packages(self):
        for name in ("tool-universal.dmg", "tool.pkg", "tool-macos-arm64.zip", "tool-osx.tar.gz"):
            self.assertEqual(self.platform(name), "macos", name)

    def test_linux_packages_and_pkg_tar(self):
        for name in ("tool.AppImage", "tool_amd64.deb", "tool.x86_64.rpm", "tool.flatpak",
                     "tool.snap", "tool.pkg.tar.zst", "tool-linux-x64.tar.gz"):
            self.assertEqual(self.platform(name), "linux", name)

    def test_android_and_alpine_apk(self):
        self.assertEqual(self.platform("app-release.apk"), "android")
        self.assertEqual(self.platform("app.aab"), "android")
        self.assertEqual(self.platform("tool-alpine.apk"), "linux")
        self.assertEqual(self.platform("tool.apk", topics=["alpine"]), "linux")

    def test_ios_packages(self):
        for name in ("tool.ipa", "tool-ios-arm64.zip"):
            self.assertEqual(self.platform(name), "ios", name)

    def test_web_and_source_packages(self):
        for name in ("tool.wasm", "tool-web.zip", "cadcraft-web-0.17.1.zip"):
            self.assertEqual(self.platform(name), "web", name)
        for name in ("tool-2.0-source.zip", "tool.whl", "tool.jar", "tool.nupkg"):
            self.assertEqual(self.platform(name), "source", name)

    def test_generic_archive_is_other(self):
        self.assertEqual(self.platform("tool.zip"), "other")
        self.assertEqual(self.platform("tool.tar.gz"), "other")

    def test_package_manager_commands(self):
        self.assertEqual(command_platform("brew install foo"), "macos")
        self.assertEqual(command_platform("winget install foo"), "windows")
        self.assertEqual(command_platform("choco install foo"), "windows")
        self.assertEqual(command_platform("apt install foo"), "linux")
        self.assertEqual(command_platform("apk add foo"), "linux")
        self.assertEqual(command_platform("pip install foo"), "source")
        self.assertEqual(command_platform("cargo install foo"), "source")
        self.assertEqual(command_platform("docker run foo"), "other")


class PlatformDataTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads((ROOT / "data" / "platform-packages.json").read_text(encoding="utf-8"))
        self.records = []
        for filename in ("rea-resources.json", "tool-resources.json"):
            self.records.extend(json.loads((ROOT / "data" / filename).read_text(encoding="utf-8")))

    def test_covers_every_curated_software_entry(self):
        expected = {record["id"] for record in self.records if record.get("kind") in SOFTWARE_KINDS}
        actual = {entry["id"] for entry in self.document["entries"]}
        self.assertEqual(actual, expected)
        self.assertEqual(self.document["meta"]["entry_count"], len(expected))
        self.assertEqual(self.document["meta"]["software_entry_count"], len(expected))

    def test_counts_agree(self):
        meta = self.document["meta"]
        entry_counts = {key: 0 for key in PLATFORM_ORDER}
        package_counts = {key: 0 for key in PLATFORM_ORDER}
        for entry in self.document["entries"]:
            self.assertEqual(entry["platform_keys"], [key for key in PLATFORM_ORDER if entry["platforms"].get(key)],
                             entry["id"])
            for key, items in entry["platforms"].items():
                self.assertIn(key, PLATFORM_ORDER, entry["id"])
                self.assertTrue(items, entry["id"])
                entry_counts[key] += 1
                package_counts[key] += len(items)
                for item in items:
                    self.assertTrue(item["name"], entry["id"])
                    if item["url"]:
                        self.assertTrue(item["url"].startswith("https://"), entry["id"])
        self.assertEqual(entry_counts, meta["platform_entry_counts"])
        self.assertEqual(package_counts, meta["platform_package_counts"])

    def test_every_class_zero_entry_has_a_package_or_source_signal(self):
        classes = json.loads((ROOT / "data" / "evidence-classes.json").read_text(encoding="utf-8"))
        c0 = {entry["id"] for entry in classes["entries"] if entry["evidence_class"] == 0}
        packages = {entry["id"]: entry for entry in self.document["entries"]}
        for identifier in c0:
            self.assertTrue(packages[identifier]["platform_keys"], identifier)

    def test_non_github_and_missing_evidence_are_explicit(self):
        for entry in self.document["entries"]:
            if entry["source"] == "not-collected":
                self.assertEqual(entry["platform_keys"], [], entry["id"])
                self.assertIn("non-GitHub", entry["reason"])


if __name__ == "__main__":
    unittest.main()
