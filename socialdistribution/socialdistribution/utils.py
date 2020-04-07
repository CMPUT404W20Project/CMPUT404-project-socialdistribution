from socialdistribution.settings import HOSTNAME


def get_url_part(url, index):
    try:
        part = url.split("/")[int(index)]
        return part
    except IndexError:
        print("url %s index %s out of range" % (url, index))
        return None


def get_hostname():
    return HOSTNAME


def get_host(url):
    try:
        parsed_url = url.split("/")
        scheme = parsed_url[0]
        host = parsed_url[2]
        return ("%s//%s/" % (scheme, host))
    except IndexError:
        print("url %s does not contain scheme or host" % (url))
        return None


def validate_instance(instance, fields, type):
    if not isinstance(instance, dict):
        print("instance not a dictionary")
        return False
    for field in fields:
        if field not in instance:
            print("%s not in %s" % (field, type))
            return False
    return True
