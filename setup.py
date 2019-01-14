from setuptools import setup, find_packages

setup(name="mqm", packages=find_packages('src'),
      setup_requires=["pytest-runner"],
      tests_require=["pytest"],
      package_dir={'': 'src'})
