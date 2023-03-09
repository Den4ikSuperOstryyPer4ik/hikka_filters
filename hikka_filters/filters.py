import inspect
import telethon
import re
from typing import Optional, Union, Callable


class Filter:
    """
    Class Filter
    
    I edited Pyrogram filters.
    """
    async def __call__(self, update, *args, **kwargs):
        raise NotImplementedError

    def __invert__(self):
        return InvertFilter(self)

    def __and__(self, other):
        return AndFilter(self, other)

    def __or__(self, other):
        return OrFilter(self, other)


class InvertFilter(Filter):
    """
    Invert Class Filter
    
    I edited Pyrogram filters.
    """
    def __init__(self, base):
        self.base = base

    async def __call__(self, update, *args, **kwargs):
        if inspect.iscoroutinefunction(self.base.__call__):
            x = await self.base(update, *args, **kwargs)
        else:
            x = await update.client.loop.run_in_executor(
                None,
                self.base,
                update, *args, **kwargs
            )

        return not x


class AndFilter(Filter):
    """
    And Class Filter
    
    I edited Pyrogram filters.
    """
    def __init__(self, base, other):
        self.base = base
        self.other = other

    async def __call__(self, update, *args, **kwargs):
        if inspect.iscoroutinefunction(self.base.__call__):
            x = await self.base(update, *args, **kwargs)
        else:
            x = await update.client.loop.run_in_executor(
                None,
                self.base,
                update, *args, **kwargs
            )

        # short circuit
        if not x:
            return False

        if inspect.iscoroutinefunction(self.other.__call__):
            y = await self.other(update, *args, **kwargs)
        else:
            y = await update.client.loop.run_in_executor(
                None,
                self.other,
                update, *args, **kwargs
            )

        return x and y


class OrFilter(Filter):
    """
    Or Class Filter
    
    I edited Pyrogram filters.
    """
    def __init__(self, base, other):
        self.base = base
        self.other = other

    async def __call__(self, update, *args, **kwargs):
        if inspect.iscoroutinefunction(self.base.__call__):
            x = await self.base(update, *args, **kwargs)
        else:
            x = await update.client.loop.run_in_executor(
                None,
                self.base,
                update, *args, **kwargs
            )

        # short circuit
        if x:
            return True

        if inspect.iscoroutinefunction(self.other.__call__):
            y = await self.other(update, *args, **kwargs)
        else:
            y = await update.client.loop.run_in_executor(
                None,
                self.other,
                update, *args, **kwargs
            )

        return x or y


def create_filter(func: Callable, **kwargs) -> Filter:
    """
    Create Your Filter for update handler for Telegram UserBot Hikka.
    
    Params:
        func (`callable`): A function that accepts two positional arguments *(filter, update)* and returns a boolean: True if the update should be handled, False otherwise.
        
        **kwargs (``any``, optional): Any keyword argument you would like to pass.
            Useful when creating parameterized custom filters, such as
            :meth:`~hikka_filters.chat` or :meth:`~hikka_filters.user`.
        
    I edited Pyrogram filters.
    """
    
    return type(
        func.__name__ or "Custom_Filter",
        (Filter,),
        {"__call__": func, **kwargs}
    )()


def check_filters(filters: Union[Filter, AndFilter, OrFilter, InvertFilter]):
    """
    Pass the filters from ``hikka_filters.filters`` or custom filters(created by ``hikka_filters.filters.create_filter(func, **kwargs)``)
    to check the update on filters.
    """
    
    def decorator(func):
        async def checking_filters(_, update, *args, **kwargs):
            if (await filters(update, *args, **kwargs)):
                return await func(_, update, *args, **kwargs)
            else:
                return False
        checking_filters.__name__ = func.__name__
        return checking_filters
    
    return decorator


def user(users: Union[int, str, list[Union[int, str]]]):
    """User Filter (:param:users (``int`` | ``str`` | ``list[`int` | `str`]`` - users IDs/usernames)"""
    users = users if isinstance(users, list) else [users]
    
    async def user_filter(flt, msg):
        if not (msg.sender and isinstance(msg.sender, telethon.tl.types.User)):
            return False
        
        for user in flt.users:
            if isinstance(user, str) and hasattr(msg.sender, "username") and msg.sender.username:
                if user.lower() == msg.sender.username.lower():
                    return True
            elif isinstance(user, int):
                if msg.sender.id == user:
                    return True
        
        return False
    
    return create_filter(user_filter, users=users)


def chat(chats: Union[int, str, list[Union[int, str]]]):
    """
    Chat Filter
    :param:chats (``int`` | ``str`` | ``list[`int` | `str`]`` - chats IDs/usernames)
    """
    chats = chats if isinstance(chats, list) else [chats]
    
    async def chat_filter(flt, msg):
        if not (
            msg.chat and (
                isinstance(msg.chat, telethon.tl.types.Channel)
                or isinstance(msg.chat, telethon.tl.types.User)
                or isinstance(msg.chat, telethon.tl.types.Chat)
            )
        ):
            return False
        
        for chat in flt.chats:
            if isinstance(chat, str) and hasattr(msg.chat, "username") and msg.chat.username:
                if chat.lower() == msg.chat.username.lower():
                    return True
            elif isinstance(chat, int):
                if msg.chat.id == chat:
                    return True
        
        return False
    
    return create_filter(chat_filter, chats=chats)


def text(
    text: Optional[Union[str, list[str]]] = None,
    startswith: Optional[Union[str, list[str]]] = None,
    endswith: Optional[Union[str, list[str]]] = None,
    lower: bool = True,
    re_match: Optional[Union[str, list[str]]] = None,
    re_search: Optional[Union[str, list[str]]] = None,
):
    """Filter on the message text/caption"""
    if (
        not text
        and not startswith
        and not endswith
        and not re_match
        and not re_search
    ):
        raise ValueError("Please pass at least one argument in filter <hikka_filters.filters.text>")
    
    async def check_text(flt, msg):
        if flt.text:
            return msg.text == flt.text if isinstance(flt.text, str) else msg.text in flt.text
        elif flt.startswith and flt.endswith:
            if isinstance(flt.startswith, str):
                if isinstance(flt.endswith, str):
                    return (
                        msg.text.lower().startswith(flt.startswith.lower()) and msg.text.lower().endswith(flt.endswith.lower())
                    ) if flt.lower else (
                        msg.text.startswith(flt.startswith)
                    )
                else:
                    for end in flt.endswith:
                        if lower and msg.text.lower().startswith(flt.startswith.lower()) and msg.text.lower().endswith(end.lower()):
                            return True
                        elif msg.text.startswith(flt.startswith) and msg.text.endswith(end):
                            return True
            elif isinstance(flt.startswith, list):
                for stwith in flt.startswith:
                    if isinstance(flt.endswith, str):
                        if lower and msg.text.lower().startswith(stwith.lower()) and msg.text.lower().endswith(flt.endswith.lower()):
                            return True
                        elif msg.text.startswith(stwith) and msg.text.endswith(flt.endswith):
                            return True
                    else:
                        for end in flt.endswith:
                            if lower and msg.text.lower().startswith(stwith.lower()) and msg.text.lower().endswith(end.lower()):
                                return True
                            elif msg.text.startswith(stwith) and msg.text.endswith(end):
                                return True
        elif flt.startswith:
            if isinstance(flt.startswith, str):
                return (
                    msg.text.lower().startswith(flt.startswith.lower())
                ) if flt.lower else (
                    msg.text.startswith(flt.startswith)
                )
            elif isinstance(flt.startswith, list):
                for stwith in flt.startswith:
                    if lower and msg.text.lower().startswith(stwith.lower()) or msg.text.startswith(stwith):
                        return True    
        elif flt.endswith:
            if isinstance(flt.endswith, str):
                return (
                    msg.text.lower().endswith(flt.endswith.lower())
                ) if flt.lower else (
                    msg.text.endswith(flt.endswith)
                )
            else:
                for end in flt.endswith:
                    if lower and msg.text.lower().endswith(end.lower()):
                        return True
                    elif msg.text.endswith(end):
                        return True
        elif flt.re_match:
            if isinstance(flt.re_match, str):
                if not (_match := re.match(flt.re_match, msg.text)):
                    return False
                msg.match = _match
                return True
            else:
                for match in flt.re_match:
                    if (_match := re.match(match, msg.text)):
                        msg.match = _match
                        return True
        elif flt.re_search:
            if isinstance(flt.re_search, str):
                if not (_search := re.search(flt.re_search, msg.text)):
                    return False
                msg.search = _search
                return True
            else:
                for search in flt.re_search:
                    if (_search := re.search(search, msg.text)):
                        msg.search = _search
                        return True
        
        return False
    
    return create_filter(
        check_text,
        text=text,
        startswith=startswith,
        endswith=endswith,
        lower=lower,
        re_match=re_match,
        re_search=re_search,
    )


async def chat_admin_filter(flt, msg):
    if msg.peer_id and isinstance(msg.peer_id, telethon.tl.types.PeerChannel) and msg.chat.megagroup and (str(msg.sender_id).startswith('-100') is False):
        return (await msg.client.get_permissions(msg.peer_id.channel_id, msg.sender_id)).is_admin
    else:
        return False


async def premium_user_filter(flt, msg):
    return msg.sender and isinstance(msg.sender, telethon.tl.types.User) and msg.sender.premium


async def user_has_username_filter(flt, msg):
    return msg.sender and isinstance(msg.sender, telethon.tl.types.User) and bool(msg.sender.username)


async def sender_bot_filter(flt, msg):
    return msg.sender and isinstance(msg.sender, telethon.tl.types.User) and bool(msg.sender.bot)


async def user_has_bio_filter(flt, msg):
    return msg.sender and isinstance(msg.sender, telethon.tl.types.User) and bool((await msg.client.get_fulluser(msg.sender.id)).full_user.about)


async def me_filter(flt, msg):
    return msg.sender and isinstance(msg.sender, telethon.tl.types.User) and bool(msg.sender.is_self)


async def reply_filter(flt, msg):
    return bool((await msg.get_reply_message()))


async def group_chat_filter(flt, msg):
    return hasattr(msg, "peer_id") and msg.peer_id and (isinstance(msg.peer_id, telethon.tl.types.PeerChannel) and msg.chat.megagroup or isinstance(msg.peer_id, telethon.tl.types.PeerChat))


async def channel_filter(flt, msg):
    return msg.chat and msg.peer_id and (isinstance(msg.chat, telethon.tl.types.Channel) and not msg.chat.megagroup and isinstance(msg.peer_id, telethon.tl.types.PeerChannel))


def get_args_raw(message) -> Union[str, bool]:
    """
    Get the parameters to the command as a raw string (not split)
    :param message: Message or string to get arguments from
    :return: Raw string of arguments
    
    by utils from hikka
    """
    if not (message := getattr(message, "message", message)):
        return False
    
    return args[1] if len(args := message.split(maxsplit=1)) > 1 else ""


async def args_filter(flt, msg):
    if not (_args := get_args_raw(msg)):
        return False
    msg.args = _args
    return True


async def via_bot_filter(flt, msg):
    return bool(msg.via_bot)


async def media_filter(flt, msg):
    return bool(msg.media)



chat_admin = create_filter(chat_admin_filter)
"""Filter on the message sender user and user is a chat admin"""

premium_user = create_filter(premium_user_filter)
"""Filter on the message sender user and user has premium"""

user_has_username = create_filter(user_has_username_filter)
"""Filter on the message sender user and user has username"""

sender_bot = create_filter(sender_bot_filter)
"""Filter on the message sender is a bot"""

user_has_bio = create_filter(user_has_bio_filter)
"""Filter on the message sender user and user has bio"""

me = create_filter(me_filter)
"""Filter on the message sender is self (`me`)"""

reply = create_filter(reply_filter)
"""Filter on the message, has reply message"""

group_chat = create_filter(group_chat_filter)
"""Filter on the message, in a group and supergroup"""

channel = create_filter(channel_filter)
"""Filter on the message, in a channel"""

args = create_filter(args_filter)
"""Filter on the message command, has arguments (get by ``from .. import utils; args = utils.get_args_raw(message)`` in a module for Hikka); if message has args: args = message.args"""

via_bot = create_filter(via_bot_filter)
"""Filter messages sent via inline bots"""

media = create_filter(media_filter)
"""Filter media messages.

A media message contains any of the following fields set: *audio*, *document*, *photo*, *sticker*, *video*, *voice*, *video_note*, *dice*, *poll*.
"""

def command(filters: Optional[Filter] = None, args: Optional[Union[bool, Filter]] = None, *args_, **kwargs):
    """
    Decorator for hikka-command.
    
    Parameters:
        ``filters``(*optional*, ``Filter``) - filters to check command
        
        ``args`` (*optional*, ``bool | Filter``) - check command for arguments?
        
        ``*args_, **kwargs``
    """
    def command_decorator(cmd_func):
        _filters = filters
        if args:
            if isinstance(args, bool):
                _args_flt = create_filter(args_filter)
            else:
                _args_flt = args
            
            if not _filters:
                _filters = _args_flt
            else:
                _filters = _filters & _args_flt
        
        async def func(_, update, *func_args, **func_kwargs):
            if _filters and (await _filters(update, *func_args, **func_kwargs)) or not _filters:
                return await cmd_func(_, update, *func_args, **func_kwargs)
            else:
                return False
        
        func.__name__ = cmd_func.__name__
        setattr(func, "is_command", True)
        for arg in args_:
            setattr(func, arg, True)
    
        for kwarg, value in kwargs.items():
            setattr(func, kwarg, value)
        
        return func
    
    return command_decorator

CONTENT_TYPES = [
    "photo",
    "text",
    "video",
    "dice",
    "forwarded",
    "audio",
    "document",
    "sticker",
    "via_bot",
    "animation",
]

def content_types(types: Union[list[str], str]):
    """Check message with content-types
    Parameters:
        ``types`` (``list[str] | str``) - list for content types or one content type
    
    ContentTypesList:
        ``photo``, 
        ``text``, 
        ``video``, 
        ``dice``, 
        ``forwarded``, 
        ``audio``, 
        ``document``, 
        ``sticker``, 
        ``via_bot``, 
        ``animation``
    """
    
    async def check_content_types(flt, message):
        _types = {
            "photo": (message.photo is not None),
            "text": (message.text is not None),
            "video": (message.video is not None),
            "dice": (message.dice is not None),
            "forwarded": (message.fwd_from is not None),
            "audio": (message.audio is not None),
            "document": (message.document is not None),
            "sticker": (message.sticker is not None),
            "via_bot": (message.via_bot is not None),
            "animation": (message.gif is not None),
        }
        
        for _type in flt.types:
            if _types[_type]:
                return True
        
        return False
    
    if isinstance(types, str):
        types = [types]
    
    for _type in types:
        if _type not in CONTENT_TYPES:
            raise ValueError(f"Type, passed in filter <content_types>: \"{_type}\" not is a content type!")
    
    return create_filter(check_content_types, types=types)


__all__ = [
    "create_filter",
    "user",
    "chat_admin",
    "premium_user",
    "user_has_username",
    "sender_bot",
    "user_has_bio",
    "me",
    "reply",
    "group_chat",
    "channel",
    "args",
    "via_bot",
    "media",
    "chat",
    "check_filters",
    "text",
    "content_types",
    "command",
]