from setuptools import setup, find_packages

tests_require = [
    'mysql-python',
    'redis',
]

install_requires = [
    'pytest',
]

setup(
    name='pytest-call-tracer',
    version='0.1.0',
    packages=find_packages(exclude=['tests']),
    zip_safe=False,
    install_requires=install_requires,
    # tests_require=tests_require,
    # test_suite='runtests.runtests',
    license='Apache License 2.0',
    include_package_data=True,
    entry_points={
        'pytest11': [
            'call_tracer = pytest_call_tracer.plugin',
        ]
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
