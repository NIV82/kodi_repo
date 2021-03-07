class BTFailure(Exception):
    pass


def decode_int(x, f):
    f += 1
    newf = x.index(ord("e"), f)
    n = int(x[f:newf])

    if x[f] == ord("-"):
        if x[f + 1] == ord("0"):
            raise ValueError

    elif x[f] == ord("0") and newf != f + 1:
        raise ValueError

    return (n, newf + 1)


def decode_bytes(x, f):
    colon = x.index(ord(":"), f)
    n = int(x[f:colon])

    if x[f] == ord("0") and colon != f + 1:
        raise ValueError

    colon += 1

    return (bytes(x[colon:colon + n]), colon + n)


def decode_list(x, f):
    r, f = [], f + 1
    while x[f] != ord("e"):
        v, f = decode_func[x[f]](x, f)
        r.append(v)

    return (r, f + 1)


def decode_dict(x, f):
    r, f = {}, f + 1
    while x[f] != ord("e"):
        k, f = decode_bytes(x, f)
        r[k], f = decode_func[x[f]](x, f)

    return (r, f + 1)


decode_func = {
    ord("l"): decode_list,
    ord("d"): decode_dict,
    ord("i"): decode_int,
    **{
        ord(c): decode_bytes
        for c in "0123456789"
    }
}


def bytes_decode_recursive(x, decoder):
    if isinstance(x, dict):
        return {
            decoder("key", key): bytes_decode_recursive(value, decoder)
            for key, value in x.items()
        }
    elif isinstance(x, list):
        return [
            bytes_decode_recursive(item, decoder)
            for item in x
        ]
    elif isinstance(x, bytes):
        return decoder("value", x)
    else:
        return x


def bdecode(x, decoder=None):
    try:
        r, l = decode_func[x[0]](x, 0)
    except (IndexError, KeyError, ValueError):
        raise BTFailure("not a valid bencoded string")

    if l != len(x):
        raise BTFailure("invalid bencoded value (data after valid prefix)")

    return bytes_decode_recursive(r, decoder) if decoder else r


def encode_int(x):
    result = bytearray()

    result.append(ord("i"))

    result.extend(bytearray(str(x), "utf-8"))
    result.append(ord("e"))

    return result


def encode_bool(x):
    if x:
        return encode_int(1)
    else:
        return encode_int(0)


def encode_bytes(x):
    result = bytearray()

    result.extend(bytearray("{}:".format(len(x)), "utf-8"))
    result.extend(x)

    return result


def encode_string(x):
    return encode_bytes(bytearray(x, "utf-8"))


def encode_list(x):
    result = bytearray()

    result.append(ord("l"))

    for i in x:
        result.extend(encode_func[type(i)](i))

    result.append(ord("e"))

    return result


def encode_dict(x):
    result = bytearray()

    result.append(ord("d"))

    for k, v in sorted(x.items()):
        result.extend(encode_string(str(k)))
        result.extend(encode_func[type(v)](v))

    result.append(ord("e"))

    return result


encode_func = {
    int: encode_int,
    bool: encode_bool,
    bytes: encode_bytes,
    str: encode_string,
    list: encode_list,
    tuple: encode_list,
    dict: encode_dict
}


def bencode(x):
    return bytes(encode_func[type(x)](x))
