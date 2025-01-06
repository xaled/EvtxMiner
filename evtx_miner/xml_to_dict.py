# def normalize_xml_dict(xml_dict, is_root=False):
#     # children tails and text
#     if xml_dict['@children']:
#         new_list = list()
#         if xml_dict['@text']:
#             new_list.append(xml_dict['@text'])
#             xml_dict['@text'] = None
#
#         for itm in xml_dict['@children']:
#             new_list.append(itm)
#             if '@tail' in itm and itm['@tail']:
#                 new_list.append(itm['@tail'])
#                 del itm['@tail']
#
#         xml_dict['@children'] = new_list
#
#     # children list to dict
#     if len(xml_dict['@children']) == len(set(itm['@tag'] for itm in xml_dict['@children'] if isinstance(itm, dict))):
#         new_children = {}
#         for itm in xml_dict['@children']:
#             item_key = itm.pop('@tag')
#             new_children[item_key] = list(itm.values())[0] if len(itm) == 1 else (itm or None)
#
#         xml_dict['@children'] = new_children
#
#     # # @value
#     # if (not not xml_dict['@attrib']) + (not not xml_dict['@text']) + (not not xml_dict['@children']) == 1:
#     #     xml_dict['@value'] = xml_dict['@attrib'] or xml_dict['@text'] or xml_dict['@children']
#     # elif xml_dict['@text'] and not xml_dict['@children']:
#     #     xml_dict['@value'] = xml_dict['@text']
#     # elif xml_dict['@children'] and not xml_dict['@text']:
#     #     xml_dict['@children'] = xml_dict['@text']
#     #
#
#     # remove empty items
#     if not xml_dict['@text']:
#         del xml_dict['@text']
#     if not xml_dict['@attrib']:
#         del xml_dict['@attrib']
#     if not xml_dict['@children']:
#         del xml_dict['@children']
#     if not xml_dict['@tail']:
#         del xml_dict['@tail']
#
#     if is_root and len(xml_dict) <= 2:
#         tag = xml_dict.pop('@tag')
#         value = list(xml_dict.values())[0] if xml_dict else None
#         return {
#             tag: value
#         }
#
#     return xml_dict
#
#
# def xml_to_dict(element, is_root=True):
#     # Initialize the node dictionary with tag name
#     return normalize_xml_dict({
#         '@tag': element.tag,
#         '@attrib': dict(element.attrib),
#         '@tail': element.tail.strip() if element.tail is not None else None,
#         '@text': element.text.strip() if element.text is not None else None,
#         '@children': [xml_to_dict(el, is_root=False) for el in element]
#     }, is_root=is_root)

def normalize_xml_dict_ex1(xml_dict, is_root=False):
    # children tails and text
    if xml_dict['@children']:
        new_list = list()
        if xml_dict['@text']:
            new_list.append(xml_dict['@text'])
            xml_dict['@text'] = None

        for itm in xml_dict['@children']:
            new_list.append(itm)
            if '@tail' in itm and itm['@tail']:
                new_list.append(itm['@tail'])
                del itm['@tail']

        xml_dict['@children'] = new_list

    # children attributes
    children_attribs = dict()

    for ix, itm in enumerate(xml_dict['@children']):
        if isinstance(itm, dict):
            item_key = itm.get('@tag')
            item_attributes = itm.pop('@attrib', {})
            for k, v in item_attributes.items():
                attr_key = f"{item_key}_{k}"
                attr_key = attr_key + str(ix) if attr_key in children_attribs else attr_key
                children_attribs[attr_key] = v

    # children list to dict
    if len(xml_dict['@children']) == len(set(itm['@tag'] for itm in xml_dict['@children'] if isinstance(itm, dict))):
        new_children = {}
        for itm in xml_dict['@children']:
            item_key = itm.pop('@tag')
            new_children[item_key] = list(itm.values())[0] if len(itm) == 1 else (itm or None)

        xml_dict['@children'] = new_children
    else:
        new_children = {}
        for ix, itm in enumerate(xml_dict['@children']):
            item_key = itm.pop('@tag')
            if item_key in new_children:
                item_key += str(ix)

            new_children[item_key] = list(itm.values())[0] if len(itm) == 1 else (itm or None)
        # xml_dict['@children'] = {f'item{ix}': itm for ix, itm in enumerate(xml_dict['@children'])}
        xml_dict['@children'] = new_children

    xml_dict['@children'].update(children_attribs)

    # remove empty items
    if not xml_dict['@text']:
        del xml_dict['@text']
    if not xml_dict['@attrib']:
        del xml_dict['@attrib']
    if not xml_dict['@children']:
        del xml_dict['@children']
    if not xml_dict['@tail']:
        del xml_dict['@tail']

    if is_root:
        tag = xml_dict.pop('@tag')
        value = xml_dict.pop('@children')
        return {
            tag: value
        }

    return xml_dict


def xml_to_dict_ex1(element, is_root=True):
    # Initialize the node dictionary with tag name
    return normalize_xml_dict_ex1({
        '@tag': element.tag,
        '@attrib': dict(element.attrib),
        '@tail': element.tail.strip() if element.tail is not None else None,
        '@text': element.text.strip() if element.text is not None else None,
        '@children': [xml_to_dict_ex1(el, is_root=False) for el in element]
    }, is_root=is_root)
