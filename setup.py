from setuptools import setup
install_requires = [
        'pandas', 
        'yaml',
        'urllib3',
        'google-auth',
        'google-auth-httplib2',
        'google-api-pythonm-client'

        ]
setup(
    name='gatools',
    version='0.0.1',
    description='report google analytics and search console data',
    author_email='kimiyuki@gmail.com',
    url='https://github.com/kimiyuki/gatools',
    install_requires= install_requires,
    licence=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
