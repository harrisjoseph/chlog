import argparse
import re
import datetime

from logentry import LogEntry
from version import Version


def parse_args():
    parser = argparse.ArgumentParser(
        description='Adds entries to the Changelog')
    parser.add_argument(
        '--file',
        '-f',
        type=str,
        default='CHANGELOG.md',
        help='File to update, CHANGELOG.md by default')
    parser.add_argument(
        '--version',
        '-v',
        type=str,
        default=None,
        help='Current version. If not found, will use most recent version in file.')
    parser.add_argument(
        '--date',
        '-d',
        type=str,
        default=str(datetime.date.today()),
        help='Date of changelog entry in YY-MM-DD format')
    parser.add_argument(
        '--minor',
        '-m',
        action="store_true",
        default=False,
        help='Increment minor version. Otherwise increments patch')
    parser.add_argument(
        '--user',
        '-u',
        action="store_true",
        default=False,
        help='Prompt user for Added/Changed/Fixed input')
    parser.add_argument(
        '--added',
        nargs='+',
        default=[],
        help='Added items to include in changelog entry')
    parser.add_argument(
        '--changed',
        nargs='+',
        default=[],
        help='Changed items to include in changelog entry')
    parser.add_argument(
        '--fixed',
        nargs='+',
        default=[],
        help='Fixed items to include in changelog entry')
    return parser.parse_args()


def find_version_in_file(fn):
    with open(fn) as fp:
        versions = re.findall("^##\s+\[([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\]",
                              fp.read(), re.MULTILINE)
    if not versions:
        return None
    versions = [tuple(map(int, x.split('.'))) for x in versions]
    return Version(*max(versions))


def find_insertion_index(lines):
    for i, l in enumerate(lines):
        if i == 0:
            continue
        if re.match("^##\s+\[([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\]", l):
            return i
    raise ValueError('No records in changelog file')


def find_compare_group(lines):
    last_line = len(lines) - 1
    while not re.match("^\[([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\]",
                       lines[last_line]):
        last_line -= 1
        if last_line == 0:
            raise ValueError('No GitHub compare links found')
    first_line = last_line
    while re.match("^\[([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\]",
                   lines[first_line]):
        first_line -= 1
        if last_line == 0:
            raise ValueError('GitHub comparison lines go to start of file')
    return first_line + 1


def create_compare_group(original_line, current_version, next_version):
    head, tail = original_line.split('/compare/', 1)
    head = '[{}]:'.format(next_version) + head.split(':', 1)[1]
    tail = 'v{}...v{}\n'.format(current_version, next_version)
    return '/compare/'.join((head, tail))


# Not finished
def update_file(input_file,
                new_log,
                current_version,
                next_version,
                output_file=None):
    if not output_file:
        output_file = input_file + '_'

    with open(input_file) as fp:
        lines = fp.readlines()
    insertion_index = find_insertion_index(lines)
    compare_index = find_compare_group(lines)
    compare_line = create_compare_group(lines[compare_index], current_version,
                                        next_version)

    with open(output_file, 'w+') as fp:
        fp.writelines(lines[:insertion_index])
        print("\nAdded log entry:\n")
        print(new_log.render())
        fp.write(new_log.render())

        fp.writelines(lines[insertion_index:compare_index])
        print("Added new github Comparison:\n")
        print(compare_line)
        fp.write(compare_line)
        fp.writelines(lines[compare_index:])


def main():
    args = parse_args()
    filename = args.file
    outfile = filename + '_'

    # Get latest version number from file / cli
    if not args.version or not Version.is_valid_version(args.version):
        current_version = find_version_in_file(filename)
    else:
        current_version = Version.from_string(args.version)
    next_version = current_version.increment(minor=args.minor)

    if args.user:
        new_log = LogEntry.from_user_input(next_version.to_string())
    else:
        new_log = LogEntry(next_version, args.date, args.changed, args.added,
                           args.fixed)

    update_file(
        filename, new_log, current_version, next_version, output_file=outfile)


if __name__ == '__main__':
    main()
