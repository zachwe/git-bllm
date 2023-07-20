from setuptools import setup, find_packages

setup(
    name='git-bllm',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'git-bllm= git_bllm.main:main',
        ],
    },
)

