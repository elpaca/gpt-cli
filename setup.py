from setuptools import setup, find_packages

setup(
    name='gpt_cli',
    version='0.1',
    packages=find_packages(),
    install_requires=['openai'],
    entry_points={
        'console_scripts': [
            'gpt = gpt_cli.__main__:main',
        ],
    },
)