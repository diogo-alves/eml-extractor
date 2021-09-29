import unittest
from argparse import ArgumentTypeError
from io import StringIO
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from unittest import mock

from eml_extractor import (
    check_file, check_path,
    extract_attachments,
    get_argument_parser,
    get_eml_files_from,
    sanitize_foldername,
    save_attachment
)

DATA_DIR = Path(__file__).parent / 'data'


class TestEmlExtractor(unittest.TestCase):

    @mock.patch.object(Path, 'glob')
    def test_get_eml_files_from_path(self, mock_glob):
        mock_glob.return_value = [
            Path('path/to/files/file1.eml'),
            Path('path/to/files/file2.eml')
        ]
        source = Path('path/to/files/')
        files = get_eml_files_from(source)
        mock_glob.assert_called_once_with('*.eml')
        self.assertListEqual(files, mock_glob.return_value)

    @mock.patch.object(Path, 'rglob')
    def test_get_eml_files_from_path_recursively(self, mock_rglob):
        mock_rglob.return_value = [
            Path('path/to/files/file1.eml'),
            Path('path/to/files/folder1/file2.eml'),
        ]
        source = Path('path/to/files/')
        files = get_eml_files_from(source, recursively=True)
        mock_rglob.assert_called_once_with('*.eml')
        self.assertListEqual(files, mock_rglob.return_value)

    @mock.patch('eml_extractor.save_attachment')
    def test_extract_attachments_when_eml_file_have_attachments(self, mock_save_attachment):
        with TemporaryDirectory() as temp_dir:
            source = DATA_DIR / 'file with attachments.eml'
            destination = Path(temp_dir)
            extract_attachments(source, destination)
            self.assertEqual(mock_save_attachment.call_count, 2)
            email_subject = 'Email with attachments'
            mock_save_attachment.assert_any_call(
                destination / email_subject / 'attachment1.txt',
                b'content of attachment 1'
            )
            mock_save_attachment.assert_any_call(
                destination / email_subject / 'attachment2.txt',
                b'content of attachment 2'
            )

    @mock.patch('eml_extractor.save_attachment')
    def test_extract_attachments_when_eml_file_does_not_have_attachments(self, mock_save_attachment):
        with TemporaryDirectory() as temp_dir:
            source = DATA_DIR / 'file without attachments.eml'
            destination = Path(temp_dir)
            extract_attachments(source, destination)
            self.assertFalse(mock_save_attachment.called)

    def test_sanitize_foldername_should_replace_all_invalid_chars(self):
        invalid_chars = '/\|[]{}:<>+=;,?!*"~#$%&@\''
        expected_name = "_" * len(invalid_chars)
        self.assertEqual(sanitize_foldername(invalid_chars), expected_name)

    @mock.patch.object(Path, 'open', new_callable=mock.mock_open)
    def test_save_attachment(self, mock_open):
        attachment = Path('attachment.txt')
        payload = b'data'
        save_attachment(attachment, payload)
        mock_open.assert_called_once_with('wb')
        mock_open.return_value.write.assert_called_once_with(payload)


class TestArgumentsCheckers(unittest.TestCase):

    def test_check_path_should_return_a_valid_path(self):
        with TemporaryDirectory() as temp_dir:
            path = check_path(temp_dir)
            self.assertIsInstance(path, Path)
            self.assertTrue(path.is_dir())

    def test_check_path_should_raise_an_error_when_the_path_is_not_a_valid_dir(self):
        with self.assertRaises(ArgumentTypeError):
            check_path('./non/existent/dir/')

    def test_check_file_should_return_a_valid_eml_file(self):
        with NamedTemporaryFile(suffix='.eml') as temp_file:
            file = check_file(temp_file.name)
            self.assertIsInstance(file, Path)
            self.assertTrue(file.is_file())
            self.assertEqual(file.suffix, '.eml')

    def test_check_file_should_raise_an_error_when_file_does_not_exist(self):
        with self.assertRaises(ArgumentTypeError):
            check_file('non_existent_file.eml')

    def test_check_file_should_raise_an_error_when_the_file_extension_is_invalid(self):
        with self.assertRaises(ArgumentTypeError), NamedTemporaryFile(suffix='.emlx') as temp_file:
            check_file(temp_file.name)


class TestArguments(unittest.TestCase):

    def setUp(self):
        self.parser = get_argument_parser()

    def test_default_values(self):
        args = self.parser.parse_args([])
        self.assertEqual(args.source, Path.cwd())
        self.assertFalse(args.recursive)
        self.assertIsNone(args.files)
        self.assertEqual(args.destination, Path.cwd())

    def test_source(self):
        with TemporaryDirectory() as temp_dir:
            args = self.parser.parse_args(['--source', temp_dir])
            self.assertEqual(args.source, Path(temp_dir))

    def test_recursive(self):
        args = self.parser.parse_args(['--recursive'])
        self.assertTrue(args.recursive)

    def test_files(self):
        with NamedTemporaryFile(suffix='.eml') as temp_file:
            args = self.parser.parse_args(['--files', temp_file.name])
            self.assertListEqual(args.files, [Path(temp_file.name)])

    def test_destination(self):
        with TemporaryDirectory() as temp_dir:
            args = self.parser.parse_args(['--destination', temp_dir])
            self.assertEqual(args.destination, Path(temp_dir))

    @mock.patch('sys.stderr', new_callable=StringIO)
    def test_mutual_exclusion_between_source_and_files(self, mock_stderr):
        with self.assertRaises(SystemExit), NamedTemporaryFile(suffix='.eml') as temp_file:
            self.parser.parse_args(['--source', '.', '--files', temp_file.name])
        expected_error_msg = 'argument -f/--files: not allowed with argument -s/--source'
        self.assertRegexpMatches(mock_stderr.getvalue(), expected_error_msg)


if __name__ == '__main__':
    unittest.main()
