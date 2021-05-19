import io

import pytest

from pre_commit_hooks.add_trailing_blank_line_fixer import fix_file
from pre_commit_hooks.add_trailing_blank_line_fixer import main


# Input, expected return value, expected output
TESTS = (
    (b'', 1, b'\n\n'),
    (b'foo\n\n', 0, b'foo\n\n'),
    (b'bar\n', 1, b'bar\n\n'),
    (b'baz\r\n', 0, b'baz\r\n'),
    (b'baz\r\n\n', 1, b'baz\r\n'),
    (b'qux\r\r', 1, b'qux\r\n'),
)


@pytest.mark.parametrize(('input_s', 'expected_retval', 'output'), TESTS)
def test_fix_file(input_s, expected_retval, output):
    file_obj = io.BytesIO(input_s)
    ret = fix_file(file_obj)
    assert file_obj.getvalue() == output
    assert ret == expected_retval


@pytest.mark.parametrize(('input_s', 'expected_retval', 'output'), TESTS)
def test_integration(input_s, expected_retval, output, tmpdir):
    path = tmpdir.join('file.txt')
    path.write_binary(input_s)

    ret = main([str(path)])
    file_output = path.read_binary()

    assert file_output == output
    assert ret == expected_retval

