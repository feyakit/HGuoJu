import base64
from dataclasses import dataclass


@dataclass(frozen=True)
class BuildVariant:
    """只维护全站源版：任何构造方式都固定为真果剧，保留字段是为了兼容旧调用。"""

    all_sources: bool = True

    def __post_init__(self):
        object.__setattr__(self, 'all_sources', True)

    @property
    def name(self):
        return '真果剧'

    @property
    def slug(self):
        return 'zhenguoju'

    @property
    def arguments(self):
        return ['--all-sources']

    @property
    def flutter_arguments(self):
        return ['--dart-define=ALL_SOURCES=' + str(self.all_sources).lower()]

    @property
    def linker_flags(self):
        return '-s -w -X hguoju/native/core.buildAllSources=' + str(self.all_sources).lower()

    @classmethod
    def from_dart_defines(cls, encoded):
        values = {}
        for item in encoded.split(','):
            if not item:
                continue
            key, separator, value = base64.b64decode(item, validate=True).decode('utf-8').partition('=')
            if separator:
                values[key] = value
        return cls(True)


def add_variant_argument(parser):
    parser.add_argument('--all-sources', action='store_true',
                        help='兼容参数：当前只产出全站源版（真果剧）')
