import json

import requests


def manylinux_wheel(package):
    url = 'https://pypi.python.org/pypi/{}/json'.format(package)
    res = requests.get(url)
    data = res.json()
    version = data['info']['version']
    result = {'package': package, 'version': version, 'url': None}

    for f in data['releases'][version]:
        if f['filename'].endswith('cp36m-manylinux1_x86_64.whl'):
            result['url'] = f['url']
            return result

    return result


def any_wheel(package):
    url = 'https://pypi.python.org/pypi/{}/json'.format(package)
    res = requests.get(url)
    data = res.json()
    version = data['info']['version']
    result = {'package': package, 'version': version, 'url': None}

    for f in data['releases'][version]:
        if f['filename'].endswith('py3-none-any.whl'):
            result['url'] = f['url']
            return result

    return result


if __name__ == '__main__':
    wheels = {}

    manylinux_packages = ['numpy', 'pandas', 'numexpr', 'psycopg2']
    anyplatform_packages = ['pymysql', 'requests', 'urllib3', 'chardet', 'idna', 'certifi', 'pytz' ]

    for info in (manylinux_wheel(p) for p in manylinux_packages):
        if info.get('url'):
            wheels[f"{info['package']}={info['version']}"] = info['url']

    for info in (any_wheel(p) for p in anyplatform_packages):
        if info.get('url'):
            wheels[f"{info['package']}={info['version']}"] = info['url']

    # manually add sqlalchemy
    # TODO @anne build own
    wheels['sqlalchemy=1.1.11'] = 'https://sqlalchemy-wheels.s3.amazonaws.com/' \
                                  'SQLAlchemy-1.1.11-cp36-cp36m-manylinux1_x86_64.whl'

    with open('wheels.json', 'w') as f:
        txt = json.dumps(wheels, indent=0)
        f.write(f'{txt}\n')

    print(wheels)
