from setuptools import setup, find_packages

setup(
    name='exdsdecode',
    version='1.0.0',
    author='SimonB',
    author_email='py.simonbolivar@gmail.com',
    description='The decode seed.seco file from Exodus crypto wallet via password and  extract mnemonic phrase (seed)',
    url='https://github.com/SimonBolivarPy/exdsdecode',
    packages=find_packages(),
    install_requires=[
        'pycryptodome',
        'mnemonic',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
