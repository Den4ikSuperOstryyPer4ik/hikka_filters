from setuptools import setup
import hikka_filters

setup(
    name="hikka_filters",
    version=hikka_filters.__version__,
    description="Filters for updates-handlers for Telegram UserBot `Hikka` (https://github.com/hikariatama/Hikka)",
    author="Den4ikSuperOstryyPer4ik",
    url=hikka_filters.__github__,
    download_url=f"{hikka_filters.__github__}/releases/latest",
    packages=['hikka_filters'],
    license="GNU AGPLv3"
)