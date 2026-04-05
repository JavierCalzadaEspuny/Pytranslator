"""Core translation engine logic powered by Argos Translate."""

import argostranslate.translate


class TranslationEngine:
    """
    Low-level translation engine wrapping Argos Translate logic.

    Methods
    -------
    translate(text, from_code, to_code): Perform translation for a language pair.
    get_language(code): Get language object by code.
    """

    @staticmethod
    def translate(text: str, from_code: str, to_code: str) -> str:
        """
        Translate text using installed Argos packages.

        Parameters
        ----------
        text : str
            Text to translate.
        from_code : str
            Source language code.
        to_code : str
            Target language code.

        Returns
        -------
        str
            Translated text.

        Raises
        ------
        RuntimeError
            If language pair is not available or translation fails.
        """
        if not text:
            return ""

        source_lang = TranslationEngine.get_language(from_code)
        target_lang = TranslationEngine.get_language(to_code)

        if source_lang is None or target_lang is None:
            raise RuntimeError(
                f"Language pair {from_code}->{to_code} not available. "
                f"Languages installed: {[l.code for l in argostranslate.translate.get_installed_languages()]}"
            )

        translation = source_lang.get_translation(target_lang)
        if translation is None:
            raise RuntimeError(
                f"No translation path configured for {from_code}->{to_code}."
            )

        return translation.translate(text)

    @staticmethod
    def get_language(code: str):
        """
        Get an installed language object by code.

        Parameters
        ----------
        code : str
            Language code.

        Returns
        -------
        Language object or None
            The language if installed, None otherwise.
        """
        langs = argostranslate.translate.get_installed_languages()
        return next((lang for lang in langs if lang.code == code), None)
