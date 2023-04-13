"""The main file containing the persistence extension."""

from json import JSONDecodeError
import logging
from types import MethodType
from typing import Callable, Dict, Optional, Tuple, Union
from collections.abc import Awaitable

import interactions as inter

from .cipher import Cipher
from .client import persistent_component, persistent_modal
from .parse import PersistentCustomID


class Persistence(inter.Extension):
    """
    The Persistence extension.

    The Persistence extension handles the persistent custom_ids. It is a simple extension that makes adding information to custom_ids simple and easy.
    """

    def __init__(self, bot, cipher_key=None):
        """
        The constructor for the Persistence extension.

        Parameters:
            bot (interactions.Client): The client instance.
            cipher_key (str): The cipher key to use. When not provided, a random key will be generated and components will never persist restarts.
                (default is None)
        """
        self._cipher = Cipher(cipher_key)

        #TODO: Decide whether the following should stay typehinted or not.
        self._component_callbacks: Dict[str, 
                                        Callable[
                                            [inter.ComponentContext, Union[str, int, float, list, dict]], #arguments
                                            Awaitable[Union[list, None]] #return type
                                        ]
                                        ] = {}
        self._modal_callbacks: Dict[str,
                                        Callable[
                                            [inter.ModalContext, Union[str, int, float, list, dict]], #arguments
                                            Awaitable[None]
                                        ], #return type
                                    ] = {}

        # set as bot.persistence for convenience
        bot.persistence = self

        bot.persistent_component = MethodType(persistent_component, bot)
        bot.persistent_modal = MethodType(persistent_modal, bot)

    def component(self, tag: str):
        """
        The persistent component decorator.

        Parameters:
            tag (str): The tag to identify your component.
        """

        def inner(coro):
            self._component_callbacks[tag] = coro
            logging.debug(f"Registered persistent component: {tag}")
            return coro

        return inner

    def modal(self, tag: str):
        """
        The persistent modal decorator.

        Parameters:
            tag (str): The tag to identify your modal.
        """

        def inner(coro):
            self._modal_callbacks[tag] = coro
            logging.debug(f"Registered persistent modal: {tag}")
            return coro

        return inner

    @inter.listen()
    async def on_component(self, ev: inter.events.Component):
        """The on_component listener. This is called when a component is used."""
        if not any((
            ev.ctx.custom_id.startswith("p~"),
            ev.ctx.custom_id[0] == "p" and ev.ctx.custom_id[2] == "~"
        )):
            return

        try:
            pid = PersistentCustomID.from_discord(self._cipher, ev.ctx.custom_id)
        except JSONDecodeError:
            logging.info("Interaction made with invalid persistent custom_id. Skipping.")
            return

        if pid.tag in self._component_callbacks:
            await self._component_callbacks[pid.tag](ev.ctx, pid.package)

    @inter.listen()
    async def on_modal(self, ev: inter.events.ModalCompletion):
        """The on_modal listener. This is called when a modal is submitted."""
        if not any((
            ev.ctx.custom_id.startswith("p~"),
            ev.ctx.custom_id[0] == "p" and ev.ctx.custom_id[2] == "~"
        )):
            return

        try:
            pid = PersistentCustomID.from_discord(self._cipher, ev.ctx.custom_id)
        except JSONDecodeError:
            logging.info("Interaction made with invalid persistent custom_id. Skipping.")
            return

        callback = self._modal_callbacks.get(pid.tag)
        if callback is not None:
            await callback(ev.ctx, pid.package)
