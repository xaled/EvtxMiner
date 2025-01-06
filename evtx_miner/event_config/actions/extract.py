class Extract:
    __slots__ = 'xpath', 'cast'

    def __init__(self, extract_str_or_dict: str | dict):
        self.xpath = extract_str_or_dict if isinstance(extract_str_or_dict, str) else extract_str_or_dict['xpath']
        self.cast = None if isinstance(extract_str_or_dict, str) else extract_str_or_dict.get('cast', None)