"""High-level Translator class with multiton pattern for language pairs."""

import asyncio
import threading
from typing import Optional

from .engine import TranslationEngine
from .manager import PackageManager


class Translator:
    """
    Multiton translation class for offline translation using Argos Translate.

    Each unique language pair (from_code, to_code) shares a single Translator instance.
    This ensures efficient resource usage and automatic package caching.

    Methods
    -------
    translate(text): Translate text from source to target language.
    atranslate(text): Async wrapper for translate.

    Example
    -------
    >>> translator = Translator(from_code="ar", to_code="en")
    >>> result = translator.translate("مرحبا بالعالم")
    >>> print(result)
    """

    # Multiton storage: maps (from_code, to_code) -> Translator instance
    _instances: dict[tuple[str, str], "Translator"] = {}
    _instances_lock = threading.Lock()

    def __new__(
        cls,
        from_code: str,
        to_code: str,
    ):
        """
        Return a shared instance for the given language pair (multiton pattern).

        Parameters
        ----------
        from_code : str
            Source language code.
        to_code : str
            Target language code.

        Returns
        -------
        Translator
            Shared instance for the language pair.
        """
        key = (from_code.lower(), to_code.lower())

        with cls._instances_lock:
            if key not in cls._instances:
                instance = super().__new__(cls)
                instance._init_lock = threading.Lock()
                cls._instances[key] = instance

        return cls._instances[key]

    def __init__(
        self,
        from_code: str,
        to_code: str,
    ):
        """
        Initialize the translator for a language pair.

        Downloads and installs packages if not already present.
        Only the first initialization call for a language pair will set up the instance.
        Subsequent calls with the same pair reuse the cached instance without re-initializing.

        Parameters
        ----------
        from_code : str
            Source language code (e.g., "ar", "en").
        to_code : str
            Target language code (e.g., "en", "ar").

        Returns
        -------
        None
            Instance is configured in place.

        Raises
        ------
        RuntimeError
            If required package cannot be found or installed.
        """
        with self._init_lock:
            # Avoid re-initialization for cached instances
            if getattr(self, "_initialized", False):
                return

            self.from_code = from_code.lower()
            self.to_code = to_code.lower()

            # Initialize manager and engine
            self.manager = PackageManager()

            # Ensure language pair is available (downloads if needed)
            self.manager.ensure_installed(self.from_code, self.to_code)

            self._initialized = True

    def translate(self, text: str) -> str:
        """
        Translate text from source to target language.

        Parameters
        ----------
        text : str
            Text to translate. Empty strings return empty strings.

        Returns
        -------
        str
            Translated text.

        Raises
        ------
        RuntimeError
            If translation fails or language pair is unavailable.

        Example
        -------
        >>> translator = Translator(from_code="ar", to_code="en")
        >>> translator.translate("مرحبا")
        'Hello'
        """
        if not text:
            return ""

        return TranslationEngine.translate(text, self.from_code, self.to_code)

    async def atranslate(self, text: str) -> str:
        """
        Asynchronously translate text (runs in background thread).

        This prevents long translations from blocking event loops.

        Parameters
        ----------
        text : str
            Text to translate.

        Returns
        -------
        str
            Translated text.

        Example
        -------
        >>> translator = Translator(from_code="ar", to_code="en")
        >>> result = await translator.atranslate("مرحبا بالعالم")
        """
        return await asyncio.to_thread(self.translate, text)

    # Multiton introspection

    @classmethod
    def get_instance(cls, from_code: str, to_code: str) -> Optional["Translator"]:
        """
        Get an existing Translator instance if it's cached, or None.

        Parameters
        ----------
        from_code : str
            Source language code.
        to_code : str
            Target language code.

        Returns
        -------
        Optional[Translator]
            The cached instance, or None if not yet created.
        """
        key = (from_code.lower(), to_code.lower())
        return cls._instances.get(key)

    @classmethod
    def list_instances(cls) -> list[tuple[str, str]]:
        """
        List all cached Translator instances (language pairs).

        Returns
        -------
        list[tuple[str, str]]
            List of (from_code, to_code) tuples for all cached instances.

        Example
        -------
        >>> Translator("ar", "en")
        >>> Translator("en", "ar")
        >>> Translator.list_instances()
        [('ar', 'en'), ('en', 'ar')]
        """
        return list(cls._instances.keys())

    @classmethod
    def clear_instances(cls) -> None:
        """
        Clear all cached Translator instances.

        Useful for testing or releasing resources. New instances will be created fresh
        on the next Translator() call.

        Returns
        -------
        None
        """
        cls._instances.clear()
