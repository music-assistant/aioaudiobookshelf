# aioaudiobookshelf
Async python library to interact with
[Audiobookshelf](https://github.com/advplyr/audiobookshelf) (ABS).

This lib's primary goal is to be used within the Audiobookshelf music provider
in Music Assistant, but it can be used independently. Calls to endpoints not
needed for the provider will be added over time.

Not all endpoints are yet implemented.

## Releases
Releases can be found on [pypi](https://pypi.org/project/aioaudiobookshelf/),
and are tagged.

## Basic usage
ABS has a rest api, documented
[here](https://api.audiobookshelf.org) and additionally uses socket.io, see
[here](https://api.audiobookshelf.org/#socket) for some event driven
functionality.
Accessibility to the endpoints is determined by the [user
types](https://api.audiobookshelf.org/#user), which may be `root, admin, user, guest`.
This lib is not tested with a `guest` user.

As of `0.1.2` this lib has two different clients, the `UserClient` and the
`SocketClient`. Admin endpoints are not yet implemented. The user client
handles calls to the Rest API, the socket client allows to subscribe to certain
events.

To authenticate the socket client, you always need the user's token, username
and password are not enough. The user client can be authenticated by username
and password, which yields the token.

Usage example:
```python
import asyncio
import logging
import os

import aiohttp

from aioaudiobookshelf import SessionConfiguration, get_user_client
from aioaudiobookshelf.schema.library import LibraryItemMinifiedBook, LibraryItemMinifiedPodcast

ABS_HOST = os.environ.get("ABS_HOST")
ABS_USER = os.environ.get("ABS_USER")
ABS_PASSWORD = os.environ.get("ABS_PASSWORD")


async def abs_basics():
    assert ABS_HOST is not None
    assert ABS_USER is not None
    assert ABS_PASSWORD is not None

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    async with aiohttp.ClientSession() as session:
        client = await get_user_client(
            session_config=SessionConfiguration(
                session=session, url=ABS_HOST, logger=logger, pagination_items_per_page=30
            ),
            username=ABS_USER,
            password=ABS_PASSWORD,
        )

        # get libraries
        libraries = await client.get_all_libraries()

        # get library items
        for library in libraries:
            async for response in client.get_library_items(library_id=library.id_):
                if not response.results:
                    break
                for lib_item_minified in response.results:
                    if isinstance(lib_item_minified, LibraryItemMinifiedPodcast):
                        ...
                    if isinstance(lib_item_minified, LibraryItemMinifiedBook):
                        ...

        # get a single podcast
        podcast_id = "dda96167-eaad-4012-83e1-149c6700d3e8"
        podcast_expanded = await client.get_library_item_podcast(podcast_id=podcast_id, expanded=True)


asyncio.run(abs_basics())
```

Have a look into `aioaudiobookshelf/client/*.py` to see which endpoints are
currently implemented. And the [provider
implementation](https://github.com/music-assistant/server/blob/dev/music_assistant/providers/audiobookshelf/__init__.py) shows, how the lib can potentially be used.
