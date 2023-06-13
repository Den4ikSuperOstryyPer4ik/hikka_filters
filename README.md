<style type="text/css">
@font-face {
    font-family: 'Movement';
    src: url('https://static.hikari.gay/Movement.ttf') format('truetype');
}

.hikka_label {
    display: inline-block;
    background: white;
    padding: 10px 15px;
    border-radius: 30px;
    font-family: "Movement";
    color: black;
    font-size: 30px;
    line-height: 30px;
    position: relative;
    left: 50%;
    transform: translateX(-50%);
}

.label_inner {
    display: flex;
}

.moon {
    height: 30px;
}
</style>

<div class="hikka_label">
    <div class="label_inner">
        <img src="https://github.com/hikariatama/assets/raw/master/waning-crescent-moon_1f318.png" class="moon">
        &nbsp;Hikka
    </div>
</div>

# Hikka Filters

>## Filters for updates-handlers for Telegram UserBot [Hikka](https://github.com/hikariatama/Hikka)
#
# <img width="30" height="30" src="https://img.icons8.com/external-sbts2018-outline-color-sbts2018/58/external-install-basic-ui-elements-2.3-sbts2018-outline-color-sbts2018.png" alt="external-install-basic-ui-elements-2.3-sbts2018-outline-color-sbts2018"/> Install

## Install via GitHub:
``` bash
pip3 install https://github.com/Den4ikSuperOstryyPer4ik/hikka_filters/archive/main.zip --upgrade
```

## Stable version from PyPi:
``` bash
pip3 install hikka-filters
```
>### For Windows: <s>pip3</s> > <b>pip</b>
#
# Usage
``` python
# requires: hikka-filters>=0.2.0

from .. import loader, utils
from hikka_filters import check_filters, user, chat, text, media, content_types, args

@loader.tds
class TestModule(loader.Module):
    """Test module for `hikka-filters` library"""

    @loader.watcher()
    @check_filters(media)
    async def media_watcher(self, message):
        """Watcher for messages with media"""
        ...
    
    @loader.watcher()
    @check_filters(content_types("forwarded") & text(startswith="!", endswith="cmd", lower=True))
    async def forwarded_cmd_watcher(self, message):
        """Watcher for forwarded messages with text starstwith "!" and endswith "cmd" """
        ...
    
    @loader.command()
    @check_filters(args)
    async def command(self, message):
        """Command with args: `(args = message.args = utils.get_args_raw(message))`"""
        args = message.args
        ...
    
    @loader.watcher()
    @check_filters(chat([ID1, ID2, ID3]))
    async def watcher_in_chats_with_ids(self, message):
        """Watcher for messages in chats with IDs"""
        ...
    
    @loader.watcher()
    @check_filters(user([ID1, ID2, ID3]))
    async def watcher_for_sended_users_with_ids(self, message):
        """Watcher for users, sended message, by IDs"""
        ...
```
>## File hikka_test_module.py
#
# Thanks [@hikariatama](https://github.com/hikariatama) for making a great userbot for Telegram: [Hikka](https://hikka.pw/)!

>### Author logo `Hikka`, font Movement, logo-CSS: [@hikariatama](https://github.com/hikariatama)