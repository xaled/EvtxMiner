import re

DEFAULT_FLAGS = 0


class Refine:
    __slots__ = 'regex', 'format'

    def __init__(self, refine_str_or_dict: str | dict):
        pattern = refine_str_or_dict if isinstance(refine_str_or_dict, str) else refine_str_or_dict['match']
        flags = refine_str_or_dict if isinstance(refine_str_or_dict, str) else refine_str_or_dict.get('flags', 0)
        self.format: str = None if isinstance(refine_str_or_dict, str) else refine_str_or_dict.get('format', None)
        self.regex = re.compile(pattern, flags=flags)

    def refine(self, text):
        if text is None:
            return text
        match = self.regex.search(text)
        if match:
            return match.group(0).strip()
        return text.strip()
