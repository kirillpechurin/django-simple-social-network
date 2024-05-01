import json
import os.path
from unittest.mock import patch

from django.test import TestCase

from common.utils import JsonFile


class JsonFileWriteUnitTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.filename = "sample.json"

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def _call(self, opts: dict, data):
        JsonFile(**opts).write(data)

    def test_default_instance(self):
        file = JsonFile(filename=self.filename)
        self.assertEqual(file.filename, self.filename)
        self.assertEqual(file.ensure_ascii, False)
        self.assertEqual(file.sort_keys, False)
        self.assertEqual(file.indent, 2)

    def test_custom_instance(self):
        file = JsonFile(filename=self.filename,
                        ensure_ascii=True,
                        sort_keys=True,
                        indent=4)
        self.assertEqual(file.filename, self.filename)
        self.assertEqual(file.ensure_ascii, True)
        self.assertEqual(file.sort_keys, True)
        self.assertEqual(file.indent, 4)

    def test_check_custom_params(self):
        with patch("json.dump") as mock:
            self._call(opts=dict(
                filename=self.filename,
                ensure_ascii=True,
                sort_keys=True,
                indent=4
            ), data={"sample": "value"})

            mock.assert_called_once()
            self.assertEqual(mock.mock_calls[0].kwargs["ensure_ascii"], True)
            self.assertEqual(mock.mock_calls[0].kwargs["sort_keys"], True)
            self.assertEqual(mock.mock_calls[0].kwargs["indent"], 4)

    def test_rewrite_all(self):
        self._call(opts=dict(filename=self.filename), data={"sample": "value"})
        with open(self.filename, mode="r", encoding='utf-8') as file:
            data = json.load(file)
        self.assertEqual(data, {"sample": "value"})

        self._call(opts=dict(filename=self.filename), data={"new": "sample"})
        with open(self.filename, mode="r", encoding='utf-8') as file:
            data = json.load(file)
        self.assertEqual(data, {"new": "sample"})
