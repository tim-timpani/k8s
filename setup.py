from setuptools import setup, find_packages

setup(
    name='k8s',
    version='1.0.0',
    packages=find_packages(include=[
        'k8s', 'k8s.*'
    ]),
    python_requires='>=3',
    url='',
    license='',
    author='Tim Martin',
    author_email='timothy.martin@netapp.com',
    description='Kubernetes Utility Script',
    install_requires=[
        'invoke',
        'tabulate'
    ],
    entry_points={
        'console_scripts': [
            'k8s=k8s.k8s:main'
        ]
    }
)
