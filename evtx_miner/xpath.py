def xpath(tree, _xpath_query, cast=None):
    result = tree.xpath(_xpath_query)
    if not result:
        return None

    result = result[0]
    result = (getattr(result, 'text', None) or str(result)).strip()
    if result and cast:
        return cast(result)
    return result.strip() or None
