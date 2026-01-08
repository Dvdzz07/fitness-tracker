#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test script for NEASaltGenerator hashing algorithm"""

import sys
import io

# Fix Windows encoding issues
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from accounts.utils.salt import NEASaltGenerator


def test_consistency():
    """Test that the same input produces the same hash"""
    print("Test 1: Consistency check")
    seed = "test_password_123"
    gen1 = NEASaltGenerator(seed)
    gen2 = NEASaltGenerator(seed)

    hash1 = gen1.generate()
    hash2 = gen2.generate()

    print(f"  Seed: {seed}")
    print(f"  Hash 1: {hash1}")
    print(f"  Hash 2: {hash2}")
    print(f"  ✓ PASS" if hash1 == hash2 else f"  ✗ FAIL")
    print()
    return hash1 == hash2


def test_different_inputs():
    """Test that different inputs produce different hashes"""
    print("Test 2: Different inputs produce different hashes")
    seeds = ["password1", "password2", "admin", "user123", ""]
    hashes = []

    for seed in seeds:
        gen = NEASaltGenerator(seed)
        hash_val = gen.generate()
        hashes.append(hash_val)
        print(f"  '{seed}' -> {hash_val}")

    unique_hashes = len(set(hashes))
    print(f"  Unique hashes: {unique_hashes}/{len(seeds)}")
    print(f"  ✓ PASS" if unique_hashes == len(seeds) else f"  ✗ FAIL")
    print()
    return unique_hashes == len(seeds)


def test_hash_format():
    """Test that the hash has the correct format (32 hex characters)"""
    print("Test 3: Hash format validation")
    seed = "format_test"
    gen = NEASaltGenerator(seed)
    hash_val = gen.generate()

    print(f"  Seed: {seed}")
    print(f"  Hash: {hash_val}")
    print(f"  Length: {len(hash_val)} (expected 32)")

    is_hex = all(c in '0123456789abcdef' for c in hash_val)
    is_correct_length = len(hash_val) == 32

    print(f"  Is hexadecimal: {is_hex}")
    print(f"  Is correct length: {is_correct_length}")
    print(f"  ✓ PASS" if is_hex and is_correct_length else f"  ✗ FAIL")
    print()
    return is_hex and is_correct_length


def test_edge_cases():
    """Test edge cases like empty strings and special characters"""
    print("Test 4: Edge cases")
    test_cases = [
        ("", "Empty string"),
        ("a", "Single character"),
        ("🔐password123", "Unicode characters"),
        ("a" * 1000, "Very long string"),
        ("!@#$%^&*()", "Special characters"),
    ]

    results = []
    for seed, description in test_cases:
        try:
            gen = NEASaltGenerator(seed)
            hash_val = gen.generate()
            is_valid = len(hash_val) == 32 and all(c in '0123456789abcdef' for c in hash_val)
            results.append(is_valid)
            status = "✓" if is_valid else "✗"
            print(f"  {status} {description}: {hash_val[:16]}...")
        except Exception as e:
            results.append(False)
            print(f"  ✗ {description}: ERROR - {e}")

    all_passed = all(results)
    print(f"  ✓ PASS" if all_passed else f"  ✗ FAIL")
    print()
    return all_passed


def test_avalanche_effect():
    """Test that small changes in input produce significantly different hashes"""
    print("Test 5: Avalanche effect (small input change = big hash change)")
    seed1 = "password"
    seed2 = "Password"  # Only one character different

    gen1 = NEASaltGenerator(seed1)
    gen2 = NEASaltGenerator(seed2)

    hash1 = gen1.generate()
    hash2 = gen2.generate()

    # Count different characters
    diff_count = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))

    print(f"  Seed 1: '{seed1}'")
    print(f"  Hash 1: {hash1}")
    print(f"  Seed 2: '{seed2}'")
    print(f"  Hash 2: {hash2}")
    print(f"  Different characters: {diff_count}/32")

    # Good avalanche effect if at least 50% of characters are different
    good_avalanche = diff_count >= 16
    print(f"  ✓ PASS" if good_avalanche else f"  ✗ FAIL")
    print()
    return good_avalanche


def main():
    print("=" * 60)
    print("NEASaltGenerator Hashing Algorithm Test Suite")
    print("=" * 60)
    print()

    results = []
    results.append(("Consistency", test_consistency()))
    results.append(("Different inputs", test_different_inputs()))
    results.append(("Hash format", test_hash_format()))
    results.append(("Edge cases", test_edge_cases()))
    results.append(("Avalanche effect", test_avalanche_effect()))

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {test_name}")

    total_passed = sum(1 for _, passed in results if passed)
    print()
    print(f"Total: {total_passed}/{len(results)} tests passed")
    print("=" * 60)

    return all(passed for _, passed in results)


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
