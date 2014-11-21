from setuptools import setup, find_packages

setup(
    name = 'paqroles',
    description = 'Permission management library',
    version = '1.0.0',
    license = 'MIT',
    packages = find_packages(),
    include_package_data = True,
    test_suite = "tests"
)
