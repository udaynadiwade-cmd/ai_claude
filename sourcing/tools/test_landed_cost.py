#!/usr/bin/env python3
"""Checks for the landed-cost arithmetic. Run: python3 test_landed_cost.py"""

from decimal import Decimal

from landed_cost import Shipment

BASE = {
    "fob": 10000,
    "currency": "USD",
    "exchange_rate": 80,
    "freight": 1000,
    "insurance": 100,
    "bcd": 10,
    "igst": 18,
}


def amounts(cfg):
    r = Shipment(cfg).compute()
    flat = {}
    for section in ("valuation", "duties", "totals"):
        flat.update(r[section])
    return flat, r


def test_assessable_value_is_fob_plus_freight_plus_insurance():
    flat, _ = amounts(BASE)
    # (10000 + 1000 + 100) * 80
    assert flat["Assessable Value (CIF)"] == Decimal("888000.00")


def test_duty_cascade():
    flat, _ = amounts(BASE)
    assert flat["BCD @ 10%"] == Decimal("88800.00")
    assert flat["SWS @ 10% on BCD"] == Decimal("8880.00")
    # IGST base = AV + BCD + SWS
    assert flat["IGST taxable base"] == Decimal("985680.00")
    assert flat["IGST @ 18%"] == Decimal("177422.40")
    assert flat["Total duty payable at customs"] == Decimal("275102.40")


def test_anti_dumping_duty_enters_the_igst_base():
    cfg = dict(BASE, add=50000)
    flat, _ = amounts(cfg)
    assert flat["Anti-dumping duty"] == Decimal("50000.00")
    assert flat["IGST taxable base"] == Decimal("1035680.00")


def test_sws_can_include_aidc():
    cfg = dict(BASE, aidc=5, sws_base="bcd+aidc")
    flat, _ = amounts(cfg)
    assert flat["AIDC @ 5%"] == Decimal("44400.00")
    assert flat["SWS @ 10% on BCD+AIDC"] == Decimal("13320.00")


def test_notional_loadings_emit_a_warning():
    cfg = {k: v for k, v in BASE.items() if k not in ("freight", "insurance")}
    _, r = amounts(cfg)
    assert len(r["notes"]) == 2
    assert any("Freight not supplied" in n for n in r["notes"])
    assert any("Insurance not supplied" in n for n in r["notes"])


def test_creditable_igst_is_excluded_from_effective_cost():
    cfg = dict(BASE, local_charges=20000, quantity=1000)
    flat, _ = amounts(cfg)
    assert flat["Duty net of creditable IGST"] == Decimal("97680.00")
    # 888000 + 97680 + 20000
    assert flat["Effective landed cost (IGST credited back)"] == Decimal("1005680.00")
    assert flat["Effective cost per unit"] == Decimal("1005.68")


def test_non_creditable_igst_is_carried_into_cost():
    cfg = dict(BASE, igst_creditable=False)
    flat, _ = amounts(cfg)
    assert flat["Duty net of creditable IGST"] == flat["Total duty payable at customs"]


def test_bad_inputs_are_rejected():
    for bad in ({"fob": 0, "exchange_rate": 80}, {"fob": 100, "exchange_rate": 0},
                dict(BASE, sws_base="nonsense")):
        try:
            Shipment(bad)
        except ValueError:
            continue
        raise AssertionError(f"expected ValueError for {bad}")


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in tests:
        fn()
        print(f"ok  {fn.__name__}")
    print(f"\n{len(tests)} passed")
