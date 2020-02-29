from unittest import TestCase
from unittest.mock import patch
import parse_media


class TestParseMedia(TestCase):
    @patch.object(parse_media, 'load_config')
    @patch.object(parse_media, 'os')
    def test_scan_media_no_media_found(self, py_os, cfg):
        py_os.listdir.return_value = ['file1.mkv', 'file2.mkv']
        cfg.return_value = {
            "MEDIA_FILE_NAME_FORMAT": "{series} - S{season}E{episode} - {quality}",
            "MEDIA_EXTS": [".mkv", ".avi", ".mp4"],
        }
        self.assertEqual(parse_media.scan_media(), {})

    @patch.object(parse_media, 'load_config')
    @patch.object(parse_media, 'os')
    def test_scan_media_found(self, py_os, cfg):
        py_os.listdir.return_value = [
            'show a - S02E03 - dvdrip.mkv',
            'show b - S05E02 - hdrip.mp4',
            'show.c.S01E01.1080p.avi']
        cfg.return_value = {
            "MEDIA_FILE_NAME_FORMAT": "{series} - S{season}E{episode} - {quality}",
            "MEDIA_EXTS": [".mkv", ".avi", ".mp4"],
        }
        self.assertEqual(parse_media.scan_media(),
                         {
                             'show a - S02E03 - dvdrip.mkv': {'series': 'show a',
                                                              'season': 2,
                                                              'episode': 3},
                             'show b - S05E02 - hdrip.mp4': {'series': 'show b',
                                                             'season': 5,
                                                             'episode': 2}
                         })
