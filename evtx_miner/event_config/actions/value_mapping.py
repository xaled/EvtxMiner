class Mapping:
    __slots__ = 'default', 'map'

    def __init__(self, mapping_dict: str | dict, default=None):
        self.map = mapping_dict
        self.default = default or mapping_dict.pop('_default') or None

    def get_mapping(self, value):
        if value is None:
            return None
        if value in self.map:
            return self.map[value]

        # if self.default:
        #     return self.default

        return f"Unknown value: {value}, default={self.default}"


LEVEL_MAPPING = {
    0: "win:LogAlways",
    1: "WINEVENT_LEVEL_CRITICAL",
    2: "WINEVENT_LEVEL_ERROR",
    3: "WINEVENT_LEVEL_WARNING",
    4: "WINEVENT_LEVEL_INFO",
    5: "WINEVENT_LEVEL_VERBOSE",
}  # https://github.com/libyal/libevtx/blob/main/documentation/Windows%20XML%20Event%20Log%20(EVTX).asciidoc#52-level

level_mapping = Mapping(LEVEL_MAPPING)
