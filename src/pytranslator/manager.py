"""Package manager for downloading and installing Argos Translate language packs."""

from pathlib import Path
import threading

import argostranslate.package
import argostranslate.settings
import argostranslate.translate

from .models import DEFAULT_CACHE


class PackageManager:
    """
    Manages installation and cache of Argos Translate language packs.

    Methods
    -------
    ensure_installed(from_code, to_code): Ensure a language pair is available.
    get_installed_languages(): Get list of installed language codes.
    get_available_packages(): Return available packages from Argos index.
    """

    _pair_locks: dict[tuple[str, str], threading.Lock] = {}
    _pair_locks_guard = threading.Lock()

    def __init__(self):
        """
        Initialize the package manager and configure Argos settings.

        Cache is managed automatically at ~/.cache_pytranslator

        Returns
        -------
        None
            Configures Argos settings in place.
        """
        self.cache_path = DEFAULT_CACHE
        self.cache_path.mkdir(parents=True, exist_ok=True)

        # Configure Argos to use our cache directory
        argostranslate.settings.package_data_dir = self.cache_path
        argostranslate.settings.package_dirs = [self.cache_path]

    def ensure_installed(
        self,
        from_code: str,
        to_code: str,
    ) -> bool:
        """
        Ensure a language pair translation package is installed.

        Downloads and installs if not already present.

        Parameters
        ----------
        from_code : str
            Source language code (e.g., "ar", "en").
        to_code : str
            Target language code (e.g., "en", "ar").

        Returns
        -------
        bool
            True if the language pair is available.

        Raises
        ------
        RuntimeError
            If package cannot be found or installation fails.
        """
        source = from_code.lower()
        target = to_code.lower()

        # Check if language pair is already installed
        if self._is_pair_installed(source, target):
            return True

        lock = self._get_pair_lock(source, target)
        with lock:
            # Double-check inside lock to avoid duplicate downloads
            if self._is_pair_installed(source, target):
                return True

            # Download and install the package
            return self._download_and_install(source, target)

    @classmethod
    def _get_pair_lock(cls, from_code: str, to_code: str) -> threading.Lock:
        """Get or create a per-language-pair lock for installation."""
        key = (from_code, to_code)
        with cls._pair_locks_guard:
            if key not in cls._pair_locks:
                cls._pair_locks[key] = threading.Lock()
            return cls._pair_locks[key]

    def _is_pair_installed(self, from_code: str, to_code: str) -> bool:
        """Check if a language pair is already installed."""
        source_lang = self._get_language(from_code)
        target_lang = self._get_language(to_code)

        if source_lang is None or target_lang is None:
            return False

        return source_lang.get_translation(target_lang) is not None

    def _download_and_install(self, from_code: str, to_code: str) -> bool:
        """Download and install a language pair from Argos index."""
        # Update package index from Argos
        argostranslate.package.update_package_index()

        # Find matching package
        available_packages = argostranslate.package.get_available_packages()
        package = next(
            (
                p
                for p in available_packages
                if p.from_code == from_code and p.to_code == to_code
            ),
            None,
        )

        if package is None:
            raise RuntimeError(
                f"Package for {from_code}->{to_code} not found in Argos index."
            )

        # Download and install
        package_path = package.download()
        argostranslate.package.install_from_path(package_path)

        # Verify installation
        return self._is_pair_installed(from_code, to_code)

    def get_installed_languages(self) -> list[str]:
        """Return list of installed language codes."""
        langs = argostranslate.translate.get_installed_languages()
        return [lang.code for lang in langs]

    def get_available_packages(self) -> list:
        """Return available packages from Argos index."""
        argostranslate.package.update_package_index()
        return argostranslate.package.get_available_packages()

    @staticmethod
    def _get_language(code: str):
        """Return an installed Argos language object for a code, or None."""
        langs = argostranslate.translate.get_installed_languages()
        return next((lang for lang in langs if lang.code == code), None)
