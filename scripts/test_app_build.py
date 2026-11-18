import base64
import os
from pathlib import Path
import plistlib
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from app_build import BuildVariant
from configure_ios_branding import configure


def dart_defines(*values):
    return ','.join(base64.b64encode(value.encode()).decode() for value in values)


class AppBuildTests(unittest.TestCase):
    def test_every_construction_resolves_to_full_edition(self):
        for encoded in ['', dart_defines('ALL_SOURCES=false'), dart_defines('OTHER=true')]:
            variant = BuildVariant.from_dart_defines(encoded)
            self.assertTrue(variant.all_sources)
            self.assertEqual(variant.name, '真果剧')
            self.assertEqual(variant.slug, 'zhenguoju')
        for explicit in [BuildVariant(), BuildVariant(False), BuildVariant(True)]:
            self.assertEqual(explicit.name, '真果剧')
            self.assertEqual(explicit.slug, 'zhenguoju')
            self.assertEqual(explicit.arguments, ['--all-sources'])
            self.assertEqual(explicit.flutter_arguments, ['--dart-define=ALL_SOURCES=true'])
            self.assertIn('core.buildAllSources=true', explicit.linker_flags)

    def test_ios_branding_keeps_bundle_identity_and_fixes_full_edition(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'Info.plist'
            original = {'CFBundleIdentifier': 'com.hguoju.app', 'CFBundleVersion': '9'}
            path.write_bytes(plistlib.dumps(original))
            for encoded in [dart_defines('ALL_SOURCES=true'), dart_defines('ALL_SOURCES=false')]:
                configure(path, encoded)
                actual = plistlib.loads(path.read_bytes())
                self.assertEqual(actual['CFBundleDisplayName'], '真果剧')
                self.assertEqual(actual['CFBundleName'], 'zhenguoju')
                for key, value in original.items():
                    self.assertEqual(actual[key], value)

    @unittest.skipUnless(shutil.which('cmake'), 'CMake is unavailable')
    def test_windows_branding_fixes_full_edition(self):
        branding = Path(__file__).resolve().parents[1] / 'windows/runner/app_branding.cmake'
        for flags in [[], ['ALL_SOURCES=false'], ['ALL_SOURCES=true'], ['OTHER=true']]:
            with self.subTest(flags=flags), tempfile.TemporaryDirectory() as temporary:
                script = Path(temporary) / 'check.cmake'
                result = Path(temporary) / 'name.txt'
                script.write_text(
                    'list(APPEND FLUTTER_TOOL_ENVIRONMENT "OTHER=1" "DART_DEFINES=' + dart_defines(*flags) + '")\n'
                    'include("' + branding.as_posix() + '")\n'
                    'file(WRITE "' + result.as_posix() + '" "${APP_DISPLAY_NAME}")\n',
                    encoding='utf-8',
                )
                subprocess.run(['cmake', '-P', str(script)], check=True, capture_output=True)
                self.assertEqual(result.read_text(encoding='utf-8'), '真果剧')

    def test_android_and_windows_propagate_full_edition_to_core_flutter_and_package(self):
        root = Path(__file__).resolve().parent
        for target in ['android', 'windows']:
            with self.subTest(target=target):
                script = root / f'build_{target}.py'
                with mock.patch.object(sys, 'argv', [str(script)]), \
                        mock.patch.dict(os.environ, {'PATH': '/tools'}, clear=True), \
                        mock.patch('shutil.which', return_value='/tools/flutter'), \
                        mock.patch('subprocess.run') as run:
                    runpy.run_path(str(script), run_name='__main__')
                calls = [call.args[0] for call in run.call_args_list]
                native = next(call for call in calls if any(str(arg).endswith('build_native.py') for arg in call))
                flutter = next(call for call in calls if 'build' in call)
                package = next(call for call in calls if any(str(arg).endswith('package_release.py') for arg in call))
                self.assertIn('--all-sources', native)
                self.assertIn('--all-sources', package)
                self.assertIn('--dart-define=ALL_SOURCES=true', flutter)


if __name__ == '__main__':
    unittest.main()
