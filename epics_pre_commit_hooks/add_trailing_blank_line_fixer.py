import argparse
import os
from typing import IO
from typing import Optional
from typing import Sequence


def fix_file(file_obj: IO[bytes]) -> int:
    # Test for newline at end of file
    # Empty files will throw IOError here
    try:
        file_obj.seek(-1, os.SEEK_END)
    except OSError:
        file_obj.write(b'\n\n')
        return 1
    last_character = file_obj.read(1)
    # last_character will be '' for an empty file
    if last_character == b'':
        file_obj.write(b'\n\n')
        return 1

    while last_character in {b'\n', b'\r'}:
        # Deal with the beginning of the file
        if file_obj.tell() == 1:
            # If we've reached the beginning of the file and it is all
            # linebreaks then we can make this file empty
            file_obj.seek(0)
            file_obj.truncate()
            file_obj.write(b'\n\n')
            return 1

        # Go back two bytes and read a character
        file_obj.seek(-2, os.SEEK_CUR)
        last_character = file_obj.read(1)

    # Our current position is at the end of the file just before any amount of
    # newlines.  If we find extraneous newlines, then backtrack and trim them.
    position = file_obj.tell()
    remaining = file_obj.read()
    for sequence in (b'\n\n', b'\r\n'):
        if remaining == sequence:
            return 0
        elif remaining.startswith(sequence):
            # Accept any \r|\n terminator and append one \n
            file_obj.seek(position + 1)
            file_obj.truncate()
            file_obj.write(b'\n')
            return 1

    file_obj.seek(-2, os.SEEK_CUR)
    second_to_last = file_obj.read(1)
    last = file_obj.read(1)
    if last == b'\n' and second_to_last not in {b'\n', b'\r'}:
        file_obj.write(b'\n')
        return 1
    elif last == second_to_last == b'\r':
        file_obj.seek(-1, os.SEEK_CUR)
        file_obj.truncate()
        file_obj.write(b'\n')
        return 1

    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', nargs='*', help='Filenames to fix')
    args = parser.parse_args(argv)

    retv = 0

    for filename in args.filenames:
        # Read as binary so we can read byte-by-byte
        with open(filename, 'rb+') as file_obj:
            ret_for_file = fix_file(file_obj)
            if ret_for_file:
                print(f'Fixing {filename}')
            retv |= ret_for_file

    return retv


if __name__ == '__main__':
    exit(main())

