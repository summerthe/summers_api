import asyncio
from enum import Enum
from typing import Any, Awaitable, Coroutine, TypeVar

import aiohttp

_T = TypeVar("_T")


class ResponseType(Enum):
    text = "text"
    json = "json"


class AsyncRequest:
    @classmethod
    def get_or_create_event_loop(cls) -> asyncio.AbstractEventLoop:
        """Try to get asyncio event loop from current thread or create if not
        exist.

        Returns
        -------
        asyncio.AbstractEventLoop
        """
        try:
            loop = asyncio.get_event_loop()
            return loop
        except RuntimeError as e:
            if str(e).startswith("There is no current event loop in thread"):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                return loop
            else:
                raise

    @classmethod
    def run_async(cls, future: Awaitable[_T] | Coroutine[Any, Any, Any]) -> _T:
        """asyncio.run_until_complete wrapper with event loop guaranteed.

        Parameters
        ----------
        future : Awaitable[_T] | Coroutine[Any, Any, Any]

        Returns
        -------
        _T
        """
        loop = cls.get_or_create_event_loop()
        return loop.run_until_complete(future)

    @classmethod
    async def post(
        cls,
        url: str,
        *,
        data: Any = None,
        **kwargs,
    ) -> Any:
        """Performs async post request.

        Parameters
        ----------
        url : str
        data : Any, optional, by default None

        Returns
        -------
        Any
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                data=data,
                **kwargs,
            ) as response:
                response.raise_for_status()
                return await response.json()

    @classmethod
    async def put(
        cls,
        url: str,
        *,
        data: Any = None,
        **kwargs,
    ) -> Any:
        """Performs async put request.

        Parameters
        ----------
        url : str
        data : Any, optional, by default None

        Returns
        -------
        Any
        """
        async with aiohttp.ClientSession() as session:
            async with session.put(
                url,
                data=data,
                **kwargs,
            ) as response:
                response.raise_for_status()
                return await response.json()

    @classmethod
    async def get(cls, url: str, return_type: ResponseType = ResponseType.text) -> Any:
        """Performs async get request.

        Parameters
        ----------
        url : str
        return_type : ResponseType, optional, by default ResponseType.text

        Returns
        -------
        Any
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
            ) as response:
                if response.status == 200:
                    if return_type == ResponseType.text:
                        response.raise_for_status()
                        return await response.text()
                    else:
                        response.raise_for_status()
                        return await response.json()
