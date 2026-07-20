#!/usr/bin/env python3
"""Exact, order-independent comparison of sums of finite binary64 leaves."""

from __future__ import annotations

import struct
from collections.abc import Iterable, Sequence
from typing import Any


BINARY64_GRID_EXPONENT = -1074
SIGN_MASK = 1 << 63
EXPONENT_MASK = 0x7FF
FRACTION_MASK = (1 << 52) - 1


def float_to_bits(value: float) -> int:
    return struct.unpack("!Q", struct.pack("!d", value))[0]


def bits_to_float(bits: int) -> float:
    return struct.unpack("!d", int(bits).to_bytes(8, "big"))[0]


def binary64_bits_to_grid_int(bits: int) -> int:
    """Return the exact coefficient of a finite binary64 value on the 2^-1074 grid."""

    raw = int(bits)
    if raw < 0 or raw >= 1 << 64:
        raise ValueError("binary64 bit pattern must fit in an unsigned 64-bit word")
    exponent = (raw >> 52) & EXPONENT_MASK
    fraction = raw & FRACTION_MASK
    if exponent == EXPONENT_MASK:
        raise ValueError("NaN and infinity are not valid score leaves")
    if exponent == 0:
        coefficient = fraction
    else:
        coefficient = ((1 << 52) | fraction) << (exponent - 1)
    return -coefficient if raw & SIGN_MASK else coefficient


def exact_grid_sum(leaf_bits: Iterable[int]) -> int:
    return sum(binary64_bits_to_grid_int(bits) for bits in leaf_bits)


def candidate_exact_key(candidate: dict[str, Any]) -> int:
    return exact_grid_sum(int(bits) for bits in candidate["source_leaf_bits"])


def select_first_exact_minimum(
    candidates: Sequence[dict[str, Any]],
) -> tuple[int, list[int], list[int]]:
    """Select the first exact minimum and return index, tied indices, and exact keys."""

    if not candidates:
        raise ValueError("at least one candidate is required")
    keys = [candidate_exact_key(candidate) for candidate in candidates]
    minimum = min(keys)
    tied = [index for index, key in enumerate(keys) if key == minimum]
    return tied[0], tied, keys

