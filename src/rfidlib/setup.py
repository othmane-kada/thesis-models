from setuptools import setup


setup(
    name='rfidlib',
    version='1.0',
    author="Andrey Larionov",
    author_email="larioandr@gmail.com",
    license="MIT",
    py_modules=['rfidlib'],
    install_requires=[
        'numpy>=1.19.2',
    ],
    tests_requires=[
        'pytest',
    ],
)
