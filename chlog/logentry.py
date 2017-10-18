import datetime
from typing import List


class LogEntry(object):
    header = """## [{version}] - {date}"""
    entry_text = "- {}"

    def __init__(self, version: str, date: str, changed: List[str],
                 added: List[str], fixed: List[str]):
        self.version = str(version)
        self.date = date
        self.added = added
        self.changed = changed
        self.fixed = fixed
        if not any((added, changed, fixed)):
            raise ValueError("You didn't provide any log entries")

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
    def is_valid_date(date):
        try:
            datetime.datetime.strptime(date, '%Y-%m-%d')
            return True
        except:
            return False

    @classmethod
    def from_user_input(cls, version=''):
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
                print("You need to enter some additions, fixes or changes")

        return cls(version, date, added, changed, fixed)
