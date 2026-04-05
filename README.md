# Pytranslator

Pytranslator is a lightweight Python library for offline translation powered by **Argos Translate**. It features a multiton pattern for efficient resource management, automatic language pack caching, and both synchronous and asynchronous translation.

## What It Does

- Downloads and caches Argos Translate language packages in a dedicated directory.
- Provides a **multiton client** where each language pair shares a single instance.
- Translates text offline without internet dependency (after initial package download).
- Handles package installation automatically.
- Supports both sync and async translation workflows.

## Install

### From GitHub (recommended for consumers):

```bash
uv add git+https://github.com/JavierCalzadaEspuny/Pytranslator.git
```

Or with pip:

```bash
pip install git+https://github.com/JavierCalzadaEspuny/Pytranslator.git
```

### For local development (clone + editable install):

```bash
git clone https://github.com/JavierCalzadaEspuny/Pytranslator.git
cd Pytranslator
pip install -e .
```

With `uv`:

```bash
uv sync
```

## Basic Use

The workflow is extremely simple: create a Translator for a language pair and translate.

```python
from pytranslator import Translator

# Create translator for Arabic → English
translator = Translator(from_code="ar", to_code="en")

# Translate text (packages auto-download on first use if missing)
result = translator.translate("مرحبا بالعالم")
print(result)  # Output: Hello world
```

**Key Points:**
- The class is a **multiton**: each language pair returns the **same shared instance**.
- Packages are automatically downloaded and cached on first use.
- Subsequent translations use the cached package (instant).

## Linear Workflow

This is the recommended way to use the library:

```python
from pytranslator import Translator

# Create translator for Arabic → English
translator = Translator(from_code="ar", to_code="en")

# Translate a phrase
phrase = "كيف حالك؟"
result = translator.translate(phrase)
print(f"Arabic: {phrase}")
print(f"English: {result}")

# Translate longer text
text = "السلام عليكم ورحمة الله وبركاته"
result = translator.translate(text)
print(f"Arabic: {text}")
print(f"English: {result}")

# Get the same instance again (multiton)
translator2 = Translator(from_code="ar", to_code="en")
print(f"Same instance? {translator is translator2}")  # True!
```

Multiple language pairs work independently:

```python
ar_to_en = Translator(from_code="ar", to_code="en")
en_to_ar = Translator(from_code="en", to_code="ar")
fr_to_en = Translator(from_code="fr", to_code="en")

# Each pair maintains its own instance and package cache
print(Translator.list_instances())
# Output: [('ar', 'en'), ('en', 'ar'), ('fr', 'en')]
```

## Methods Reference

### `Translator(from_code, to_code)`

Initialize or retrieve a translator for a language pair.

Automatically downloads and installs required packages if not already cached.

**Parameters:**
- `from_code` (str): Source language code (e.g., "ar", "en", "fr")
- `to_code` (str): Target language code

**Returns:** Shared Translator instance for the language pair

**Raises:** RuntimeError if package cannot be found or installed

**Example:**
```python
translator = Translator(from_code="ar", to_code="en")
```

### `translator.translate(text)`

Synchronously translate text.

**Parameters:**
- `text` (str): Text to translate

**Returns:** Translated text (str)

**Raises:** RuntimeError if language pair unavailable or translation fails

**Example:**
```python
result = translator.translate("مرحبا")
print(result)  # Hello
```

### `await translator.atranslate(text)`

Asynchronously translate text (runs in background thread to avoid blocking event loops).

**Parameters:**
- `text` (str): Text to translate

**Returns:** Coroutine that yields translated text (str)

**Example:**
```python
result = await translator.atranslate("مرحبا بالعالم")
print(result)
```

### `Translator.get_instance(from_code, to_code)`

Get an existing translator instance if cached, or None.

**Parameters:**
- `from_code` (str): Source language code
- `to_code` (str): Target language code

**Returns:** Translator instance or None

**Example:**
```python
t = Translator.get_instance(from_code="ar", to_code="en")
if t:
    print("Already created!")
else:
    t = Translator(from_code="ar", to_code="en")
```

### `Translator.list_instances()`

List all cached translator instances (as language pair tuples).

**Returns:** List of tuples `(from_code, to_code)`

**Example:**
```python
Translator(from_code="ar", to_code="en")
Translator(from_code="en", to_code="ar")
print(Translator.list_instances())
# Output: [('ar', 'en'), ('en', 'ar')]
```

### `Translator.clear_instances()`

Clear all cached translator instances. Useful for testing or releasing resources.

**Returns:** None

**Example:**
```python
Translator.clear_instances()
# New instances will be created fresh on next Translator() call
```

## Examples

### English to Arabic

```python
from pytranslator import Translator

translator = Translator(from_code="en", to_code="ar")

text = "Hello, how are you today?"
result = translator.translate(text)
print(f"English: {text}")
print(f"Arabic: {result}")
```

### Arabic to English

```python
from pytranslator import Translator

translator = Translator(from_code="ar", to_code="en")

samples = [
    "مرحبا بالعالم",
    "كيف حالك؟",
    "السلام عليكم",
]

for sample in samples:
    result = translator.translate(sample)
    print(f"{sample} → {result}")
```

### Multiple Language Pairs

```python
from pytranslator import Translator

# Create translators for different pairs
ar_en = Translator(from_code="ar", to_code="en")
en_ar = Translator(from_code="en", to_code="ar")
fr_en = Translator(from_code="fr", to_code="en")

# Each maintains its own instance and cache
text_ar = "مرحبا"
text_en = "Hello"
text_fr = "Bonjour"

print(ar_en.translate(text_ar))  # Hello
print(en_ar.translate(text_en))  # مرحبا
print(fr_en.translate(text_fr))  # Hello
```

## Async Use

For async workflows (e.g., in async web frameworks), use `atranslate()`:

```python
import asyncio
from pytranslator import Translator


async def main():
    translator = Translator(from_code="ar", to_code="en")

    # Translate multiple texts concurrently
    texts = [
        "مرحبا بالعالم",
        "كيف حالك؟",
        "شكراً لك",
    ]

    results = await asyncio.gather(
        *[translator.atranslate(text) for text in texts]
    )

    for original, translated in zip(texts, results):
        print(f"{original} → {translated}")


asyncio.run(main())
```

## Manual Smoke Test

Run the included smoke test to verify installation and behavior:

```bash
python smoke_run.py
```

For release/CI validation, run in strict mode so translation checks cannot be skipped:

```bash
PYTRANSLATOR_SMOKE_STRICT=1 python smoke_run.py
```

The smoke test covers:

- Multiton initialization and instance reuse
- Different language pairs creating separate instances
- `list_instances()` and `get_instance()` methods
- Synchronous and asynchronous translation
- Instance caching and retrieval

## Project Structure

```
src/pytranslator/
├── __init__.py       # Public API (exports Translator)
├── main.py           # Translator class (multiton pattern)
├── engine.py         # TranslationEngine (low-level translation logic)
├── manager.py        # PackageManager (Argos package handling)
└── models.py         # Configuration, constants, cache paths

pyproject.toml        # Package and dependency configuration
.gitignore            # Standard Python ignore rules
smoke_run.py          # Manual smoke test script
README.md             # This file
```

## How It Works

### Multiton Pattern

Pytranslator uses the **multiton pattern** to ensure each language pair shares a single instance:

```python
# These return the same object
t1 = Translator(from_code="ar", to_code="en")
t2 = Translator(from_code="ar", to_code="en")
assert t1 is t2  # True!

# Different pairs create different instances
t3 = Translator(from_code="en", to_code="ar")
assert t1 is not t3  # True
```

**Benefits:**
- Avoids redundant package downloads
- Reduces memory footprint
- Efficient resource sharing across the application

### Package Caching & Auto-Installation

1. First call to `Translator(from_code="ar", to_code="en")`:
   - Checks if package is cached in `~/.cache_pytranslator`
   - If not found, downloads from Argos index and installs
   - Caches for future use

2. Subsequent calls with same pair:
   - Uses cached package (instant)
   - No downloading needed

Package cache location:

```bash
ls ~/.cache_pytranslator/
# Output: files from downloaded Argos packages
```

## Notes

- The `Translator` instance is shared per language pair across your entire application.
- Simply call `Translator(from_code, to_code)` to get a translator.
- Packages are downloaded automatically on first use and cached locally.
- Use `atranslate()` for async/concurrent workflows to avoid blocking event loops.
- Use `Translator.clear_instances()` only for testing purposes.

## License

MIT

## Repository

- **Web:** https://github.com/JavierCalzadaEspuny/Pytranslator
- **Git clone:** `git clone https://github.com/JavierCalzadaEspuny/Pytranslator.git`
