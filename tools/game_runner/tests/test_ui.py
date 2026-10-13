"""Focused UI safety tests; native input and rendering need live proof."""
import hashlib
import struct
import tempfile
import time
import unittest
from pathlib import Path

try:
    from tools.game_runner.ui import WindowGeometry, UIError, validate_declaration, validate_reload, validate_frame, wait_for_saved_campaign
except ImportError:
    WindowGeometry = None


class GeometryTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(WindowGeometry, 'UI helper is absent')

    def test_125_percent_virtualized_client_is_converted_once(self):
        geometry = WindowGeometry(42, 100, 120, 2048, 1152, 2560, 1440, 100, 50)
        self.assertEqual(geometry.image_to_client(1280, 720), (1024, 576))
        self.assertEqual(geometry.image_to_screen(1280, 720), (1124, 626))

    def test_dpi_aware_client_does_not_receive_a_second_dpi_multiplier(self):
        geometry = WindowGeometry(42, 100, 120, 2560, 1440, 2560, 1440, -20, 40)
        self.assertEqual(geometry.image_to_client(1280, 720), (1280, 720))
        self.assertEqual(geometry.image_to_screen(1280, 720), (1260, 760))

    def test_100_percent_window_origin_and_edge_pixels(self):
        geometry = WindowGeometry(42, 100, 96, 1920, 1080, 1920, 1080, 10, 25)
        self.assertEqual(geometry.image_to_screen(1919, 1079), (1929, 1104))
        for point in [(-1, 0), (1920, 0), (0, 1080), (True, 20), (float('nan'), 20)]:
            with self.subTest(point=point), self.assertRaises(ValueError):
                geometry.image_to_client(*point)

    def test_mismatched_capture_and_nonuniform_or_unknown_scaling_fail(self):
        for values in [(2048, 1152, 2560, 1400, 120), (2048, 1152, 2560, 1440, 96), (0, 1152, 2560, 1440, 120), (2048, 1152, 2560, 1440, 0)]:
            width, height, pixels_w, pixels_h, dpi = values
            with self.subTest(values=values), self.assertRaises(ValueError):
                WindowGeometry(42, 100, dpi, width, height, pixels_w, pixels_h, 0, 0)

    def test_geometry_change_or_ownership_change_rejects_the_frame(self):
        original = WindowGeometry(42, 100, 120, 2048, 1152, 2560, 1440, 0, 0)
        for changed in [WindowGeometry(43, 100, 120, 2048, 1152, 2560, 1440, 0, 0), WindowGeometry(42, 101, 120, 2048, 1152, 2560, 1440, 0, 0), WindowGeometry(42, 100, 120, 2048, 1152, 2560, 1440, 10, 0)]:
            with self.subTest(changed=changed), self.assertRaises(UIError):
                original.require_unchanged(changed)


def measured():
    return dict(first_id=11, second_id=12, selected_id=12, ambitions=2,
                declared_count=1, first_identity=1, second_identity=1,
                first_declared=0, second_declared=1, deadline_days=1825,
                choice_second=1, eligible_count=1, origin_delta=0, review_delta=0, stress_delta=0, prestige_delta=0)


class NativeAssertionTests(unittest.TestCase):
    def test_declaration_proves_exact_story_and_other_instance_preservation(self):
        self.assertEqual(validate_declaration(11, 12, measured()), measured())

    def test_wrong_story_stale_selection_or_clicked_cancel_cannot_pass(self):
        for changes in [dict(selected_id=11), dict(first_declared=1), dict(second_declared=0), dict(first_identity=0), dict(second_identity=0), dict(declared_count=0), dict(deadline_days=0), dict(origin_delta=1), dict(stress_delta=10)]:
            values = measured() | changes
            with self.subTest(changes=changes), self.assertRaises(UIError):
                validate_declaration(11, 12, values)

    def test_missing_unknown_boolean_or_conflicting_identity_is_rejected(self):
        missing = measured()
        del missing['review_delta']
        for values in [missing, measured() | dict(extra=1), measured() | dict(first_identity=True), measured() | dict(second_id=11)]:
            with self.subTest(values=values), self.assertRaises(UIError):
                validate_declaration(11, 12, values)

    def test_reload_compares_actual_declaration_state_without_recreation(self):
        before = measured()
        self.assertEqual(validate_reload(before, measured()), measured())
        for changes in [dict(second_id=22), dict(deadline_days=1824), dict(review_delta=1), dict(ambitions=1)]:
            with self.subTest(changes=changes), self.assertRaises(UIError):
                validate_reload(before, measured() | changes)


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        self.geometry = WindowGeometry(42, 100, 96, 1920, 1080, 1920, 1080, 0, 0)

    def png(self, name='stage.png', width=1920, height=1080):
        # A real generated PNG; image decoding must reject a header-only file.
        import zlib
        path = self.root / name
        def chunk(kind, payload):
            return struct.pack('>I', len(payload)) + kind + payload + struct.pack('>I', zlib.crc32(kind + payload))
        header = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
        rows = b''.join(b'\0' + bytes([20 + row % 180, 70, 90]) * width for row in range(height))
        path.write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', header) + chunk(b'IDAT', zlib.compress(rows)) + chunk(b'IEND', b''))
        return path

    def test_frame_requires_fresh_decodable_pixels_and_matching_geometry(self):
        started = time.time() - 1
        path = self.png()
        frame = validate_frame(path, self.root, self.geometry, started, 'selected-story')
        self.assertEqual(frame['width'], 1920)
        self.assertEqual(frame['height'], 1080)
        self.assertEqual(frame['sha256'], hashlib.sha256(path.read_bytes()).hexdigest())
        self.assertEqual(frame['operation'], 'selected-story')

    def test_missing_stale_outside_truncated_or_mismatched_frame_is_not_evidence(self):
        path = self.png()
        bad = self.root / 'truncated.png'
        bad.write_bytes(path.read_bytes()[:32])
        wrong = self.png('wrong.png', 20, 10)
        for candidate, started, root in [(self.root / 'absent.png', 0, self.root), (path, time.time() + 1, self.root), (path, 0, self.root / 'child'), (bad, 0, self.root), (wrong, 0, self.root)]:
            with self.subTest(candidate=candidate, started=started), self.assertRaises(UIError):
                validate_frame(candidate, root, self.geometry, started, 'selected-story')

    def test_save_wait_requires_stable_nonbaseline_campaign_and_bounded_timeout(self):
        save = self.root / 'owned.ck3'
        save.write_bytes(b'actual native saved state')
        now = [0]
        result = wait_for_saved_campaign(save, '0' * 64, 1, clock=lambda: now[0], sleep=lambda delay: now.__setitem__(0, now[0] + delay))
        self.assertEqual(result['sha256'], hashlib.sha256(b'actual native saved state').hexdigest())
        self.assertGreaterEqual(now[0], 0.2)
        now[0] = 0
        with self.assertRaises(TimeoutError):
            wait_for_saved_campaign(self.root / 'absent.ck3', '0' * 64, 0.3, clock=lambda: now[0], sleep=lambda delay: now.__setitem__(0, now[0] + delay))
        self.assertLessEqual(now[0], 0.4)

    def test_save_wait_rejects_baseline_copy_and_unbounded_deadline(self):
        save = self.root / 'owned.ck3'
        save.write_bytes(b'baseline')
        with self.assertRaises(UIError):
            wait_for_saved_campaign(save, hashlib.sha256(b'baseline').hexdigest(), 1)
        for deadline in [0, 181, True]:
            with self.subTest(deadline=deadline), self.assertRaises(ValueError):
                wait_for_saved_campaign(save, '0' * 64, deadline)


if __name__ == '__main__':
    unittest.main()
