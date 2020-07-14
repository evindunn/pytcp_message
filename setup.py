from setuptools import setup

test_dependencies = list()
with open("requirements_test.txt") as f:
    for line in [l.strip() for l in f.readlines()]:
        if not line.startswith("#"):
            test_dependencies.append(line)

with open("README.md") as f:
    long_desc = f.read()

setup(
    name='pytcp_message',
    version='0.1.9',
    packages=['pytcp_message', "pytcp_message.message"],
    description='Client and server for TCP message passing',
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url='https://github.com/evindunn/pytcp_message',
    author='Evin Dunn',
    author_email='evin@scan-bugs.org',
    license='MIT',
    zip_safe=False,
    tests_require=test_dependencies,
    test_suite="pytest",
    python_requires=">=3.6"
)
