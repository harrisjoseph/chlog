import sys
import os
from typing import List
import re
import datetime


class LogEntry(object):
    header = """## [{version}] - {date}"""
    entry_text = "- {}"

    def __init__(self, version: str, date: str, changed: List[str],
                 added: List[str], fixed: List[str]):
        self.version = version
        self.date = date
        self.added = added
        self.changed = changed
        self.fixed = fixed

    def render(self):
        if self.added:
            added_text = '### Added\n' \
                + '\n'.join(self.entry_text.format(x) for x in self.added)
        else:
            added_text = ''
        if self.changed:
            change_text = '### Changed\n' \
                + '\n'.join(self.entry_text.format(x) for x in self.changed)
        else:
            change_text = ''
        if self.fixed:
            fix_text = '### Fixed\n' \
                + '\n'.join(self.entry_text.format(x) for x in self.fixed)
        else:
            fix_text = ''
        header = self.header.format(version=self.version, date=self.date)
        content = (header, added_text, change_text, fix_text)
        return '\n'.join([x for x in content if x]) + '\n\n'

    @staticmethod
    def is_valid_version(version):
        return re.match('^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$', version)

    @staticmethod
    def is_valid_date(date):
        try:
            _ = datetime.datetime.strptime(date, '%Y-%m-%d')
            return True
        except:
            return False

    @classmethod
    def from_user_input(cls, version=''):
        if not version:
            version = input('Version: ')
        while not cls.is_valid_version(version):
            print("'{}'' is not a valid version".format(version))
            version = input('Version: ')

        date = input('Date?: ')
        if not date:
            date = str(datetime.date.today())

        changed = []
        fixed = []
        added = []

        while not added or fixed or changed:
            while True:
                newadded = input('Added?: ')
                if newadded:
                    added.append(newadded)
                else:
                    break

            while True:
                newchange = input('Changed?: ')
                if newchange:
                    changed.append(newchange)
                else:
                    break

            while True:
                newfix = input('Fixed?: ')
                if newfix:
                    fixed.append(newfix)
                else:
                    break
            if fixed or changed:
                break
            else:
                print("You need to add some fixes or changes")

        return cls(version, date, added, changed, fixed)


def tuple_to_str(tup):
    return '.'.join(str(x) for x in tup)


def find_version_in_file(fn):
    with open(fn) as fp:
        versions = re.findall("^##\s+\[([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\]",
                              fp.read(), re.MULTILINE)
    if not versions:
        return None
    versions = [tuple(map(int, x.split('.'))) for x in versions]
    return max(versions)


def get_next_version(fn):
    last_version = find_version_in_file(fn)
    if not last_version:
        return '', ''
    next_version = tuple_to_str(last_version[:-1] + (last_version[-1] + 1, ))
    print('Last version in file is [{}], writing version [{}]'.format(
        tuple_to_str(last_version), next_version))
    return tuple_to_str(last_version), next_version


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


def main():
    filename = sys.argv[1]
    outfile = filename + '_'

    current_version, next_version = get_next_version(filename)
    new_log = LogEntry.from_user_input(next_version)

    with open(filename) as fp:
        lines = fp.readlines()
    insertion_index = find_insertion_index(lines)
    compare_index = find_compare_group(lines)
    compare_line = create_compare_group(lines[compare_index], current_version,
                                        next_version)

    with open(outfile, 'w+') as fp:
        fp.writelines(lines[:insertion_index])
        print("\nAdded log entry:\n")
        print(new_log.render())
        fp.write(new_log.render())

        fp.writelines(lines[insertion_index:compare_index])
        print("Added new github Comparison:\n")
        print(compare_line)
        fp.write(compare_line)
        fp.writelines(lines[compare_index:])


if __name__ == '__main__':
    main()
