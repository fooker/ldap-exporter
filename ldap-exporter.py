from bottle import route, run, response
from json import dumps

import ldap3
import ldap3.utils.dn


# See https://www.netiq.com/documentation/edirectory-9/edir_admin/data/b1gkoio0.html

HOST = ''
USERNAME = ''
PASSWORD = ''


def connect():
    server = ldap3.Server(host=HOST,
                          port=636,
                          use_ssl=True,
                          get_info='ALL')
    con = ldap3.Connection(server=server,
                           user=USERNAME,
                           password=PASSWORD)
    con.bind()

    return con


def sat(result, path, k, v):
    if len(path) == 0:
        result[k] = v
        return

    if path[0] not in result:
        result[path[0]] = {}

    sat(result[path[0]], path[1:], k, v)


def try_int(val):
    try:
        return [int(v) for v in val]
    except ValueError:
        return val


@route('/')
def export():
    result = {}

    with connect() as con:
        con.search(search_base='cn=monitor',
                   search_filter='(objectClass=*)',
                   search_scope=ldap3.SUBTREE,
                   attributes=['*', '+'])

        for x in con.response:
            path = [e[1] for e in ldap3.utils.dn.parse_dn(x['dn'])]
            path.reverse()

            for (key, val) in x['attributes'].items():
                if key == 'objectclass':
                    continue

                val = try_int(val)

                sat(result, path, key, val)

    response.content_type = 'application/json'

    return dumps(result)


if __name__ == '__main__':
    run(host='localhost', port=8080)
