"""Unsigned, offline actual-source/full-SDK sanitizer regression."""

import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(os.environ.get("OWNERSHIP_SOURCE_ROOT", ROOT)).resolve()
SDK = {
    "4DPluginAPI.c": "478081f0238f6bc5393222f574bc2656f010b67b",
    "4DPluginAPI.h": "9054b45ffc7ff6f5b8d57529a3788a55d977b314",
    "EntryPoints.h": "730f2f77ff2713fb2fe4b7d6562baeedf5f664cb",
    "Flags.h": "10a83185333dac06a62dda61b9f9428243d1e2ee",
    "PrivateTypes.h": "77053dc0c0a3718d2d3b6f158371a6af78c6ae66",
    "PublicTypes.h": "2bb392e73e9c556c274fe0a75b3a6b83e310b77c",
    "4DPluginAPI.def": "996ecc4ab11ad165de9192eba2e7478db141c757",
}


@unittest.skipUnless(sys.platform == "darwin", "macOS synthetic host")
class OwnershipTests(unittest.TestCase):
    leaf_runs = 0
    leaf_passes = 0

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="application-icon-ownership-")
        cls.addClassCleanup(cls.temp.cleanup)
        api = SOURCE / "4D Plugin API"
        for name, expected in SDK.items():
            contents = (api / name).read_bytes()
            blob = hashlib.sha1(f"blob {len(contents)}\0".encode() + contents).hexdigest()
            if blob != expected:
                raise AssertionError(f"Re-audit changed SDK: {name}: {blob}")
        common = [
            "clang++", "-std=c++14", "-x", "objective-c++",
            "-include", str(ROOT / ".github/tests/ownership_platform.h"),
            "-I", str(api), "-I", str(api / "Classes"),
            "-fsanitize=address,undefined", "-fno-sanitize=alignment",
            "-fno-omit-frame-pointer", "-g",
            "-Wno-deprecated-declarations", "-Wno-return-type-c-linkage",
            "-Wno-ignored-attributes", "-Wno-writable-strings",
        ]
        cls.binaries = {}
        for platform in ("mac", "windows"):
            dispatcher = Path(cls.temp.name) / f"{platform}.o"
            command = common + (["-DOWNERSHIP_WINDOWS_DISPATCH"] if platform == "windows" else [])
            cls.compile(command + ["-c", str(SOURCE / "4DPlugin.cpp"), "-o", str(dispatcher)])
            binary = Path(cls.temp.name) / platform
            cls.compile(common + [
                str(api / "4DPluginAPI.c"),
                *map(str, sorted((api / "Classes").glob("*.cpp"))),
                str(ROOT / ".github/tests/ownership_host.mm"),
                "-x", "none", str(dispatcher),
                "-framework", "Cocoa", "-framework", "Carbon", "-framework", "ImageIO",
                "-o", str(binary),
            ])
            cls.binaries[platform] = binary
            imports = subprocess.check_output(["nm", "-u", str(binary)], text=True)
            for symbol in (
                "_OBJC_CLASS_$_NSURL", "_OBJC_CLASS_$_NSImage",
                "_OBJC_CLASS_$_NSFileManager", "_OBJC_CLASS_$_NSWorkspace",
                "_CFURLCreateWithFileSystemPath", "_CFURLCopyFileSystemPath",
                "_LoadLibraryEx", "_FindResource", "_BeginUpdateResource",
                "_UpdateResource", "_EndUpdateResource",
                "_system", "_popen", "_execve", "_posix_spawn",
            ):
                if any(line.strip().endswith(symbol) for line in imports.splitlines()):
                    raise AssertionError(f"Real platform boundary linked: {symbol}")

    @classmethod
    def compile(cls, command):
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)

    @classmethod
    def tearDownClass(cls):
        print(f"LEAF runs={cls.leaf_runs} passed={cls.leaf_passes} "
              f"failed={cls.leaf_runs - cls.leaf_passes}", file=sys.stderr)

    def run_case(self, case, text="", empty="allocated", mode=0, platform="windows"):
        type(self).leaf_runs += 1
        result = subprocess.run(
            [str(self.binaries[platform]), case, text, empty, str(mode)],
            env={**os.environ, "ASAN_OPTIONS": "detect_leaks=0",
                 "UBSAN_OPTIONS": "halt_on_error=1"},
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            type(self).leaf_passes += 1
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("strings=0 pictures=0 handles=0 objects=n/a collections=n/a", result.stdout)

    def test_exact_paths_copy_scalar_and_empty_engines(self):
        for case in ("path", "copy", "scalar"):
            for text in ("ASCII", "\u65e5", "\U0001f600", ""):
                for empty in ("allocated", "null"):
                    with self.subTest(case=case, text=text, empty=empty):
                        self.run_case(case, text, empty)

    def test_picture_lifetimes(self):
        for case in ("bytes", "gray", "size", "thumbnail"):
            with self.subTest(case=case):
                self.run_case(case)

    def test_array_transfers_and_rejections(self):
        for empty in ("allocated", "null"):
            with self.subTest(empty=empty):
                self.run_case("arrays", empty=empty)

    def test_error_before_output_adoption(self):
        for case in ("path", "copy", "gray", "size", "thumbnail"):
            for failure in ("handle", "command"):
                with self.subTest(case=case, failure=failure):
                    self.run_case(f"{case}:{failure}")
        self.run_case("copy:conversion")

    def test_sdk_failure_predicates_not_oom_safety(self):
        self.run_case("sdk-failures")

    def test_independent_owned_command_returns(self):
        for kind in range(3):
            with self.subTest(kind=kind):
                self.run_case("command-returns", "ASCII", mode=kind)

    def test_pointer_lookup_success_and_poison_failure(self):
        for case in ("pointer", "pointer-failure"):
            with self.subTest(case=case):
                self.run_case(case, "ASCII")

    def test_actual_windows_dispatcher_all_command_failures_and_metadata_paths(self):
        for mode in range(13):
            for empty in ("allocated", "null"):
                with self.subTest(mode=mode, empty=empty):
                    self.run_case("dispatch", empty=empty, mode=mode)

    def test_mac_dispatcher_no_icon_work(self):
        self.run_case("dispatch-mac", platform="mac")

    def test_noncopyable_heap_owners_and_copyable_values(self):
        self.run_case("copy-traits")

    def test_each_implicit_copy_owner(self):
        for kind in range(10):
            with self.subTest(kind=kind):
                self.run_case("copy-owner", mode=kind)


if __name__ == "__main__":
    unittest.main()
