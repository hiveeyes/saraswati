import imp

try:
    import hashlib

    md = hashlib.md5
except ImportError:
    import md5

    md = md5.new


def load_module_from_file(path):
    """
    http://code.davidjanes.com/blog/2008/11/27/how-to-dynamically-load-python-code/

    :param path:
    :return:
    """
    try:
        fp = open(path, "rb")
        digest = md(path.encode("utf-8")).hexdigest()
        return imp.load_source(digest, path, fp)
    finally:
        try:
            fp.close()
        except:
            pass
