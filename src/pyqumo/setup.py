from setuptools import setup, Extension
from Cython.Build import cythonize
import os

os.environ['CC'] = 'g++'
os.environ['CXX'] = 'g++'

extensions = [
    Extension(
        "pyqumo.cqumo.sim", [
            "pyqumo/cqumo/sim.pyx",
            "cqumo/Base.cpp",
            "cqumo/Functions.cpp",
            "cqumo/tandem/Components.cpp",
            "cqumo/tandem/Journals.cpp",
            "cqumo/tandem/Simulation.cpp",
            "cqumo/tandem/Statistics.cpp",
            "cqumo/tandem/System.cpp",
            "cqumo/tandem/Marshal.cpp",
        ],
        include_dirs=['cqumo', 'cqumo/tandem'],
        language="c++",
        extra_compile_args=["-std=c++14", "-Wno-deprecated", "-O3"],
        extra_link_args=["-std=c++14"]
    ),
    Extension(
        "pyqumo.cqumo.randoms", [
            "pyqumo/cqumo/randoms.pyx",
            "cqumo/Functions.cpp",
            "cqumo/Randoms.cpp",
        ],
        include_dirs=['cqumo'],
        language="c++",
        extra_compile_args=["-std=c++14", "-Wno-deprecated", "-O3"],
        extra_link_args=["-std=c++14"]
    )
]

compiler_directives = {
    "language_level": 3,
    "embedsignature": True,
}


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='pyqumo',
    version='1.0',
    description='Queueing Models in Python',
    long_description=readme(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Intended Audience :: Science/Research',
    ],
    keywords='queueing systems, markov chains',
    url='https://github.com/larioandr/thesis-models/tree/pyqumo-refactor/src/pyqumo',
    author='Andrey Larionov',
    author_email='larioandr@gmail.com',
    license='MIT',
    packages=['pyqumo'],
    py_modules=['pyqumo'],
    scripts=[],
    python_requires=">=3.8",
    install_requires=[
        'numpy',
        'scipy',
        'tabulate',
        'Cython',
    ],
    include_package_data=True,
    zip_safe=False,
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    ext_modules=cythonize(
        extensions,
        compiler_directives=compiler_directives,
        annotate=True
    ),
    extras_require={
        "docs": ["sphinx", "sphinx-rtd-theme"]
    }
)
