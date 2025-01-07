def xpath(tree, _xpath_query, cast=None):
    result = tree.xpath(_xpath_query)
    if not result:
        return None

    result = result[0]
    # print(_xpath_query, type(result), hasattr(result, 'tag'), hasattr(result, 'text'), dir(result))
    if hasattr(result, 'text'):
        result = result.text.strip() if result.text else result.text
    else:
        result = str(result).strip()
    # result = (getattr(result, 'text', None) or str(result)).strip()

    if result and cast:
        return cast(result)
    return result
