from __future__ import annotations

import random

import pytest

from langcheck.augment.ja import conv_hiragana


@pytest.mark.parametrize(
    "instances, num_perturbations, aug_char_p, convert_to, expected",
    [
        ########################################################################
        # To kata, single input
        ########################################################################
        (
            "ひらがなを別の字に変換する",
            1,
            0.9,
            "kata",
            ["ヒラガナヲ別ノ字ニ変換スル"],
        ),
        (
            "ひらがなを別の字に変換する",
            2,
            0.9,
            "kata",
            ["ヒラガナヲ別ノ字ニ変換スル", "ヒラガナヲ別ノ字ニ変換すル"],
        ),
        (
            ["ひらがなを別の字に変換する"],
            1,
            0.9,
            "kata",
            ["ヒラガナヲ別ノ字ニ変換スル"],
        ),
        (
            ["ひらがなを別の字に変換する"],
            2,
            0.9,
            "kata",
            ["ヒラガナヲ別ノ字ニ変換スル", "ヒラガナヲ別ノ字ニ変換すル"],
        ),
        (
            "ひらがなを別の字に変換する",
            1,
            0.1,
            "kata",
            ["ひラがなを別の字に変換すル"],
        ),
        (
            "ひらがなを別の字に変換する",
            2,
            0.1,
            "kata",
            ["ひラがなを別の字に変換すル", "ひらがなを別ノ字に変換する"],
        ),
        (
            ["ひらがなを別の字に変換する"],
            1,
            0.1,
            "kata",
            ["ひラがなを別の字に変換すル"],
        ),
        (
            ["ひらがなを別の字に変換する"],
            2,
            0.1,
            "kata",
            ["ひラがなを別の字に変換すル", "ひらがなを別ノ字に変換する"],
        ),
        ########################################################################
        # To hkata, single input
        ########################################################################
        ("ひらがなを別の字に変換する", 1, 0.9, "hkata", ["ﾋﾗｶﾞﾅｦ別ﾉ字ﾆ変換ｽﾙ"]),
        (
            "ひらがなを別の字に変換する",
            2,
            0.9,
            "hkata",
            ["ﾋﾗｶﾞﾅｦ別ﾉ字ﾆ変換ｽﾙ", "ﾋﾗｶﾞﾅｦ別ﾉ字ﾆ変換すﾙ"],
        ),
        (
            ["ひらがなを別の字に変換する"],
            1,
            0.9,
            "hkata",
            ["ﾋﾗｶﾞﾅｦ別ﾉ字ﾆ変換ｽﾙ"],
        ),
        (
            ["ひらがなを別の字に変換する"],
            2,
            0.9,
            "hkata",
            ["ﾋﾗｶﾞﾅｦ別ﾉ字ﾆ変換ｽﾙ", "ﾋﾗｶﾞﾅｦ別ﾉ字ﾆ変換すﾙ"],
        ),
        (
            "ひらがなを別の字に変換する",
            1,
            0.1,
            "hkata",
            ["ひﾗがなを別の字に変換すﾙ"],
        ),
        (
            "ひらがなを別の字に変換する",
            2,
            0.1,
            "hkata",
            ["ひﾗがなを別の字に変換すﾙ", "ひらがなを別ﾉ字に変換する"],
        ),
        (
            ["ひらがなを別の字に変換する"],
            1,
            0.1,
            "hkata",
            ["ひﾗがなを別の字に変換すﾙ"],
        ),
        (
            ["ひらがなを別の字に変換する"],
            2,
            0.1,
            "hkata",
            ["ひﾗがなを別の字に変換すﾙ", "ひらがなを別ﾉ字に変換する"],
        ),
        ########################################################################
        # To alpha, single input
        ########################################################################
        (
            "ひらがなを別の字に変換する",
            1,
            0.9,
            "alpha",
            ["hiraganawo別no字ni変換suru"],
        ),
        (
            "ひらがなを別の字に変換する",
            2,
            0.9,
            "alpha",
            ["hiraganawo別no字ni変換suru", "hiraganawo別no字ni変換すru"],
        ),
        (
            ["ひらがなを別の字に変換する"],
            1,
            0.9,
            "alpha",
            ["hiraganawo別no字ni変換suru"],
        ),
        (
            ["ひらがなを別の字に変換する"],
            2,
            0.9,
            "alpha",
            ["hiraganawo別no字ni変換suru", "hiraganawo別no字ni変換すru"],
        ),
        (
            "ひらがなを別の字に変換する",
            1,
            0.1,
            "alpha",
            ["ひraがなを別の字に変換すru"],
        ),
        (
            "ひらがなを別の字に変換する",
            2,
            0.1,
            "alpha",
            ["ひraがなを別の字に変換すru", "ひらがなを別no字に変換する"],
        ),
        (
            ["ひらがなを別の字に変換する"],
            1,
            0.1,
            "alpha",
            ["ひraがなを別の字に変換すru"],
        ),
        (
            ["ひらがなを別の字に変換する"],
            2,
            0.1,
            "alpha",
            ["ひraがなを別の字に変換すru", "ひらがなを別no字に変換する"],
        ),
        ########################################################################
        # Multiple inputs
        ########################################################################
        (
            ["ひらがなを別の字に変換する", "カタカナは別の字に変換しない"],
            1,
            0.9,
            "kata",
            ["ヒラガナヲ別ノ字ニ変換スル", "カタカナハ別ノ字ニ変換しナイ"],
        ),
        (
            ["ひらがなを別の字に変換する", "カタカナは別の字に変換しない"],
            2,
            0.9,
            "kata",
            [
                "ヒラガナヲ別ノ字ニ変換スル",
                "ヒラガナヲ別ノ字ニ変換すル",
                "カタカナハ別ノ字ニ変換シナイ",
                "カタカナハ別ノ字ニ変換シナい",
            ],
        ),
        (
            ["ひらがなを別の字に変換する", "カタカナは別の字に変換しない"],
            1,
            0.9,
            "hkata",
            ["ﾋﾗｶﾞﾅｦ別ﾉ字ﾆ変換ｽﾙ", "カタカナﾊ別ﾉ字ﾆ変換しﾅｲ"],
        ),
        (
            ["ひらがなを別の字に変換する", "カタカナは別の字に変換しない"],
            2,
            0.9,
            "hkata",
            [
                "ﾋﾗｶﾞﾅｦ別ﾉ字ﾆ変換ｽﾙ",
                "ﾋﾗｶﾞﾅｦ別ﾉ字ﾆ変換すﾙ",
                "カタカナﾊ別ﾉ字ﾆ変換ｼﾅｲ",
                "カタカナﾊ別ﾉ字ﾆ変換ｼﾅい",
            ],
        ),
    ],
)
def test_change_case(
    instances: list[str] | str,
    num_perturbations: int,
    aug_char_p: float,
    convert_to: str,
    expected: list[str],
):
    seed = 42
    random.seed(seed)
    actual = conv_hiragana(
        instances,
        convert_to=convert_to,
        aug_char_p=aug_char_p,
        num_perturbations=num_perturbations,
    )
    assert actual == expected
