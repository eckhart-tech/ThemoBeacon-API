from setuptools import setup, find_packages
import subprocess

root='beacon'

def get_install_requires(pkg):
    r = subprocess.run(['pipreqs', '--print', pkg], capture_output=True, text=True)
    return [x for x in r.stdout.split('\n') if len(x) > 0]

setup_args = dict(
    name='Thermobeacon tools',
    version='1.0',
    packages=find_packages(include=[root, f'{root}.*']),
    include_package_data=True,
    install_requires=get_install_requires(root),
    url='https://https://github.com/eckhart-tech/ThermoBeacon-API',
    license='BSD3',
    author='julianporter',
    author_email='julian@porternet.net',
    description='ThermoBeacon scanner and API tool',
    entry_points={
        'console_scripts': [
            f'thermobeacon-tool = {root}:action'
        ]
    }
)

for k,v in setup_args.items():
    print(f' {k}={v}')

setup(**setup_args)
