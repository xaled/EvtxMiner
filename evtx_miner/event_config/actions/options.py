def find_options_value(database, *keys):
    for key in keys:
        value = database.get(key)
        if value:
            return value
    return None
