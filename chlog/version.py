import re


class Version(object):
    """
    Represents a semantic version, without a v
    """
    def __init__(self, major: int, minor=0, patch=0):
        self.major = major
        self.minor = minor
        self.patch = patch
        for val in self.values:
            assert isinstance(val, int)

    @property
    def values(self):
        return (self.major, self.minor, self.patch)

    def to_string(self):
        return str(self)

    @classmethod
    def from_string(cls, version):
        assert cls.is_valid_version(version)
        vals = [int(x) for x in version.split('.')]
        return cls(*vals)

    @staticmethod
    def is_valid_version(version):
        return re.match('^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$', version)

    def __str__(self):
        return '.'.join([str(x) for x in self.values])

    def increment(self, minor=False):
        """
        Returns a new object
        """
        major = self.major
        if minor:
            minor = self.minor + 1
            patch = 0
        else:
            minor = self.minor
            patch = self.patch + 1
        return self.__class__(major, minor, patch)
