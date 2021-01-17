try:
    from setuptools import setup
except ImportError:
    from distutils.code import setup

setup(
    name='iqair2mqtt',
    version='0.1',
    entry_points={
        'console_scripts': [
            'iqair2mqtt = iqair2mqtt.main:main'
        ]
    },
)
