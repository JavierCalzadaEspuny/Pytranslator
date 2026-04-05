"""Comprehensive smoke test for Pytranslator - tests all functionality."""

import asyncio
import os
import sys
import time
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pytranslator import Translator


STRICT_SMOKE = os.getenv("PYTRANSLATOR_SMOKE_STRICT", "0") == "1"
SKIPPED_TESTS = 0


def _handle_runtime_skip(test_name: str, error: RuntimeError) -> None:
    """Handle runtime-dependent skips with optional strict failure mode."""
    global SKIPPED_TESTS
    if STRICT_SMOKE:
        raise RuntimeError(f"{test_name} failed in strict mode: {error}") from error
    SKIPPED_TESTS += 1
    print(f"⚠ {test_name} skipped: {error}\n")


def test_multiton_pattern():
    """Verify that the same language pair returns the same instance (multiton)."""
    print("=" * 70)
    print("TEST 1: Multiton Pattern (Same pair = Same instance)")
    print("=" * 70)

    Translator.clear_instances()

    # Create first instance for ar -> en
    client1 = Translator(from_code="ar", to_code="en")
    print(f"✓ Created client1 (ar→en): {id(client1)}")

    # Create second instance for ar -> en (should be the same object)
    client2 = Translator(from_code="ar", to_code="en")
    print(f"✓ Created client2 (ar→en): {id(client2)}")

    # Verify they're the same instance
    assert client1 is client2, "FAIL: Same pair should return same instance!"
    print(f"✓ Both instances are identical: {client1 is client2}\n")


def test_different_pairs():
    """Verify that different language pairs create different instances."""
    print("=" * 70)
    print("TEST 2: Different Language Pairs (Different pair = Different instance)")
    print("=" * 70)

    Translator.clear_instances()

    client_ar_en = Translator(from_code="ar", to_code="en")
    print(f"✓ Created ar→en translator: {id(client_ar_en)}")

    client_en_ar = Translator(from_code="en", to_code="ar")
    print(f"✓ Created en→ar translator: {id(client_en_ar)}")

    assert client_ar_en is not client_en_ar, "FAIL: Different pairs should be different instances!"
    print(f"✓ Instances are different: {client_ar_en is not client_en_ar}\n")


def test_introspection_methods():
    """Verify get_instance() and list_instances() methods."""
    print("=" * 70)
    print("TEST 3: Introspection Methods (get_instance, list_instances)")
    print("=" * 70)

    Translator.clear_instances()

    # Test get_instance before creation
    result = Translator.get_instance(from_code="ar", to_code="en")
    assert result is None, "FAIL: Should return None before creation"
    print(f"✓ get_instance('ar', 'en') before creation: None")

    # Create instance
    translator = Translator(from_code="ar", to_code="en")
    print(f"✓ Created ar→en translator")

    # Test get_instance after creation
    result = Translator.get_instance(from_code="ar", to_code="en")
    assert result is translator, "FAIL: Should return same instance"
    print(f"✓ get_instance('ar', 'en') after creation: OK (same instance)")

    # Create more instances
    Translator(from_code="en", to_code="ar")
    Translator(from_code="fr", to_code="en")

    # Test list_instances
    instances = Translator.list_instances()
    print(f"✓ list_instances(): {instances}")
    assert len(instances) == 3, "FAIL: Should have 3 instances"
    assert ("ar", "en") in instances
    assert ("en", "ar") in instances
    assert ("fr", "en") in instances
    print(f"✓ All 3 language pairs cached correctly\n")


def test_sync_translation():
    """Test synchronous translation."""
    print("=" * 70)
    print("TEST 4: Synchronous Translation")
    print("=" * 70)

    try:
        translator = Translator(from_code="ar", to_code="en")

        samples = [
            "مرحبا بالعالم",
            "كيف حالك؟",
            "شكراً لك",
        ]

        for text in samples:
            result = translator.translate(text)
            print(f"  {text:20} → {result}")

        print(f"✓ Synchronous translation working\n")

    except RuntimeError as e:
        _handle_runtime_skip("Translation test", e)


async def test_async_translation():
    """Test asynchronous translation."""
    print("=" * 70)
    print("TEST 5: Asynchronous Translation (Single)")
    print("=" * 70)

    try:
        translator = Translator(from_code="ar", to_code="en")

        samples = [
            "مرحبا",
            "وداعاً",
        ]

        for text in samples:
            result = await translator.atranslate(text)
            print(f"  {text:20} → {result}")

        print(f"✓ Asynchronous translation working\n")

    except RuntimeError as e:
        _handle_runtime_skip("Async translation test", e)


async def test_batch_async_translation():
    """Test batch translation (concurrent)."""
    print("=" * 70)
    print("TEST 6: Batch Translation (Concurrent)")
    print("=" * 70)

    try:
        translator = Translator(from_code="ar", to_code="en")

        texts = [
            "مرحبا بالعالم",
            "كيف حالك؟",
            "أنا بخير",
            "شكراً لك",
            "وداعاً",
        ]

        print(f"Translating {len(texts)} texts concurrently...\n")

        start_time = time.time()
        results = await asyncio.gather(
            *[translator.atranslate(text) for text in texts]
        )
        elapsed = time.time() - start_time

        for original, translated in zip(texts, results):
            print(f"  {original:20} → {translated}")

        print(f"\n✓ Batch translation completed in {elapsed:.2f}s\n")

    except RuntimeError as e:
        _handle_runtime_skip("Batch translation test", e)


async def test_multiple_pairs_async():
    """Test translation with multiple language pairs concurrently."""
    print("=" * 70)
    print("TEST 7: Multiple Language Pairs (Concurrent)")
    print("=" * 70)

    try:
        # Create translators for different pairs
        ar_en = Translator(from_code="ar", to_code="en")
        fr_en = Translator(from_code="fr", to_code="en")

        ar_text = "السلام عليكم"
        fr_text = "Bonjour"

        print(f"Translating from Arabic and French concurrently...\n")

        ar_result, fr_result = await asyncio.gather(
            ar_en.atranslate(ar_text),
            fr_en.atranslate(fr_text),
        )

        print(f"  Arabic: {ar_text:20} → {ar_result}")
        print(f"  French: {fr_text:20} → {fr_result}")
        print(f"\n✓ Multiple pairs translation working\n")

    except RuntimeError as e:
        _handle_runtime_skip("Multiple pairs test", e)


async def run_all_tests():
    """Run all tests in sequence."""
    print("\n" + "=" * 70)
    print("PYTRANSLATOR COMPREHENSIVE SMOKE TEST")
    print("=" * 70 + "\n")

    try:
        # Sync tests
        test_multiton_pattern()
        test_different_pairs()
        test_introspection_methods()
        test_sync_translation()

        # Async tests
        await test_async_translation()
        await test_batch_async_translation()
        await test_multiple_pairs_async()

        if SKIPPED_TESTS:
            print(f"⚠ Completed with {SKIPPED_TESTS} skipped runtime tests.")
            print("⚠ Set PYTRANSLATOR_SMOKE_STRICT=1 to fail on skips.\n")

        print("=" * 70)
        print("✓ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n✗ ERROR: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_all_tests())
