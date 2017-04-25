from distutils.core import setup
from setuptools import find_packages

__version__ = "0.1.0"

install_requires = [
    "django"
]

tests_require = [
    "pytest",
    "pytest-cov",
    "pytest-django",
    "django_factory_boy",
    "codecov"
]

extras = {
    "test": tests_require
}


setup(
    name="django-und",
    packages=find_packages(),
    version=__version__,
    description=("Django Up and Down, django app"
                 "to add upvote and downvote to models"),
    author="luxcem",
    author_email="a@luxcem.fr",
    url="https://github.com/luxcem/django-und",
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require=extras,
    setup_requires=["pytest-runner"],
)
