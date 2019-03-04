import os

##https://wiki.python.org/moin/Distutils/Cookbook/AutoPackageDiscovery
def is_package(path):
    return (
        os.path.isdir(path) and
        os.path.isfile(os.path.join(path, '__init__.py'))
        )

def find_packages(path, base="" ):
    """ Find all packages in path """
    packages = {}
    for item in os.listdir(path):
        dir = os.path.join(path, item)
        if is_package( dir ):
            if base:
                module_name = "%(base)s.%(item)s" % vars()
            else:
                module_name = item
            packages[module_name] = dir
            packages.update(find_packages(dir, module_name))
    return packages
##############################################

from setuptools import setup
install_requires = [
        'pandas', 
        'urllib3',
        'google-auth',
        'google-auth-httplib2',
        'google-api-python-client'

        ]
setup(
    name='gatools',
    version='0.0.1',
    description='report google analytics and search console data',
    author_email='kimiyuki@gmail.com',
    url='https://github.com/kimiyuki/gatools',
    install_requires= install_requires,
    licence=license,
    #packages=find_packages(exclude=('tests', 'docs'))
    packages=find_packages(".")
)
