import inspect
import telethon


class Filter:
    """
    Class Filter
    
    I edited Pyrogram filters.
    """
    async def __call__(self, update):
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

    async def __call__(self, update):
        if inspect.iscoroutinefunction(self.base.__call__):
            x = await self.base(update)
        else:
            x = await update.client.loop.run_in_executor(
                None,
                self.base,
                update
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

    async def __call__(self, update):
        if inspect.iscoroutinefunction(self.base.__call__):
            x = await self.base(update)
        else:
            x = await update.client.loop.run_in_executor(
                None,
                self.base,
                update
            )

        # short circuit
        if not x:
            return False

        if inspect.iscoroutinefunction(self.other.__call__):
            y = await self.other(update)
        else:
            y = await update.client.loop.run_in_executor(
                None,
                self.other,
                update
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

    async def __call__(self, update):
        if inspect.iscoroutinefunction(self.base.__call__):
            x = await self.base(update)
        else:
            x = await update.client.loop.run_in_executor(
                None,
                self.base,
                update
            )

        # short circuit
        if x:
            return True

        if inspect.iscoroutinefunction(self.other.__call__):
            y = await self.other(update)
        else:
            y = await update.client.loop.run_in_executor(
                None,
                self.other,
                update
            )

        return x or y


def create_filter(func: callable, **kwargs) -> Filter:
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
        func.__name__ or 'Custom_Filter',
        (Filter,),
        {"__call__": func, **kwargs}
    )()


def check_filter(filters):
    def decorator(func):
        async def checking_filters(_, update):
            __name__ = func.__name__
            if (await filters(update)):
                await func(_, update)
            else: return None
        return checking_filters
    return decorator


def user(users: int | str | list[int | str]):
    """User Filter (:param:users (``int`` | ``str`` | ``list[`int` | `str`]`` - users IDs/usernames)"""
    users = users if isinstance(users, list) else [users]
    
    async def user_filter(_, msg):
        return True if isinstance(msg.sender, telethon.tl.types.User) and (msg.sender.id in _.users or msg.sender.username in _.users) else False
    
    return create_filter(user_filter, users=users)


def chat(chats: int | str | list[int | str]):
    """Chat Filter (:param:chats (``int`` | ``str`` | ``list[`int` | `str`]`` - chats IDs/usernames)"""
    chats = chats if isinstance(chats, list) else [chats]
    
    async def chat_filter(_, msg):
        return True if msg.chat and (isinstance(msg.chat, telethon.tl.types.Channel) or isinstance(msg.chat, telethon.tl.types.User) or isinstance(msg.chat, telethon.tl.types.Chat)) and (msg.chat.id in _.chats or msg.chat.username and msg.chat.username in _.chats) else False
    
    return create_filter(chat_filter, chats=chats)


def text(text: str, check_caption: bool = True):
    """Filter on the message text/caption == your text"""
    async def check_text(_, msg):
        return bool(msg.text) and msg.text == _.text or (hasattr(msg, 'caption') and bool(msg.caption) and msg.caption == _.text) if _.check_caption else False
    
    return create_filter(
        check_text,
        text=text,
        check_caption=check_caption
    )


async def chat_admin_filter(_, msg):
    if msg.peer_id and isinstance(msg.peer_id, telethon.tl.types.PeerChannel) and msg.chat.megagroup and (str(msg.sender_id).startswith('-100') is False):
        return (await msg.client.get_permissions(msg.peer_id.channel_id, msg.sender_id)).is_admin
    else: return False


async def premium_user_filter(_, msg):
    return msg.sender and msg.sender.premium


async def user_has_username_filter(_, msg):
    return msg.sender and isinstance(msg.sender, telethon.tl.types.User) and bool(msg.sender.username)


async def sender_bot_filter(_, msg):
    return msg.sender and isinstance(msg.sender, telethon.tl.types.User) and bool(msg.sender.bot)


async def user_has_bio_filter(_, msg):
    return msg.sender and isinstance(msg.sender, telethon.tl.types.User) and bool((await msg.client.get_fulluser(msg.sender.id)).full_user.about)


async def me_filter(_, msg):
    return msg.sender and isinstance(msg.sender, telethon.tl.types.User) and bool(msg.sender.is_self)


async def reply_filter(_, msg):
    return bool((await msg.get_reply_message()))


async def group_chat_filter(_, msg):
    return msg.peer_id and (isinstance(msg.peer_id, telethon.tl.types.PeerChannel) and msg.chat.megagroup or isinstance(msg.peer_id, telethon.tl.types.PeerChat))


async def channel_filter(_, msg):
    return msg.chat and msg.peer_id and (isinstance(msg.chat, telethon.tl.types.Channel) and msg.chat.megagroup is False and isinstance(msg.peer_id, telethon.tl.types.PeerChannel))


def get_args_raw(message) -> str | bool:
    """
    Get the parameters to the command as a raw string (not split)
    :param message: Message or string to get arguments from
    :return: Raw string of arguments
    
    By hikariatama :)
    """
    if not (message := getattr(message, "message", message)):
        return False
    
    return args[1] if len(args := message.split(maxsplit=1)) > 1 else ""


async def args_filter(_, msg):
    return bool((get_args_raw(msg)))


async def via_bot_filter(_, msg):
    return bool(msg.via_bot)


async def media_filter(_, msg):
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
"""Filter on the message command, has arguments (get by ``from .. import utils; args = utils.get_args_raw(message)`` in a module for Hikka"""

via_bot = create_filter(via_bot_filter)
"""Filter messages sent via inline bots"""

media = create_filter(media_filter)
"""Filter media messages.

A media message contains any of the following fields set: *audio*, *document*, *photo*, *sticker*, *video*, *voice*, *video_note*, *dice*, *poll*.
"""


__all__ = [
    'create_filter',
    'user',
    'chat_admin',
    'premium_user',
    'user_has_username',
    'sender_bot',
    'user_has_bio',
    'me',
    'reply',
    'group_chat',
    'channel',
    'args',
    'via_bot',
    'media',
    'chat',
    'check_filter',
    'text',
]