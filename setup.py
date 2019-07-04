from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='matchbox-orm',
    version='0.2',
    description='matchbox is orm package for google Cloud Firestore',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/gameboy86/matchbox',
    author='Maciej Gębarski',
    author_email='mgebarski@gmail.com',
    license='MIT',
    packages=find_packages(exclude=['tests']),
    zip_safe=False,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=['firebase-admin>=2.16.0', 'iso8601>=0.1.12'],
)
