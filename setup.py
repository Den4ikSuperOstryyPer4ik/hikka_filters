from setuptools import setup
import re

try:
    import hikkatl
except ImportError:
    raise Exception("Please use hikka version >= 1.6.2. (If you have hikka version>=1.6.2: please install Hikka-TL-New)")

with open("hikka_filters/__init__.py", encoding="utf-8") as f:
    _text = f.read()
    version = re.findall(r"__version__ = \"(.+)\"", _text)[0]
    github = re.findall(r"__github__ = \"(.+)\"", _text)[0]

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="hikka_filters",
    version=version,
    description="Filters for updates-handlers for Telegram UserBot `Hikka` (https://github.com/hikariatama/Hikka)",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Den4ikSuperOstryyPer4ik",
    url=github,
    download_url=f"{github}/releases/latest",
    packages=['hikka_filters'],
    license="GNU AGPLv3"
)
