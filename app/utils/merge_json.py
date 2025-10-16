def merge(target: dict, path: dict):
    target = target.copy()
    if len(path) > 0 and target is None:
        target = dict()
    for name, value in path.items():
        if value is None:
            del target[name]
        elif isinstance(value, dict):
            target[name] = merge(target[name], value)
        else:
            target[name] = value
    return target
