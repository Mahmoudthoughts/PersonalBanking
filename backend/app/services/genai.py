"""Utility functions for interacting with OpenAI's Agents API."""

from __future__ import annotations

import asyncio

from openai import OpenAI
from openai.agents import Runner


client = OpenAI()


def ensure_event_loop() -> None:
    """Ensure an event loop exists for synchronous runner usage."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)


def run_prompt(prompt: str) -> dict:
    """Run a prompt through the OpenAI Agents Runner."""
    ensure_event_loop()
    runner = Runner(client)
    return runner.run_sync(prompt)

