#!/usr/bin/env python3
"""Checks for the live-data layer. Run: python3 test_data_layer.py

No network access is required or attempted.
"""

import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import hs_lookup
import landed_cost
import net
import provenance

HERE = os.path.dirname(os.path.abspath(__file__))


# ------------------------------------------------------------------ net ----

def test_proxy_refusal_is_classified_as_blocked_not_as_an_answer():
    err = net.classify(Exception("ProxyError: Cannot connect to proxy"), "https://x/")
    assert isinstance(err, net.EgressBlocked)


def test_browser_tunnel_failure_is_classified_as_blocked():
    err = net.classify(Exception("net::ERR_TUNNEL_CONNECTION_FAILED"), "https://x/")
    assert isinstance(err, net.EgressBlocked)


def test_untrusted_tls_is_blocked_and_never_suggests_disabling_verification():
    err = net.classify(Exception("SSLError: certificate verify failed"), "https://x/")
    assert isinstance(err, net.EgressBlocked)
    assert "never disable" in err.detail


def test_an_http_error_is_not_mistaken_for_a_block():
    err = net.classify(ValueError("HTTP 404"), "https://x/")
    assert isinstance(err, net.UpstreamError)
    assert not isinstance(err, net.EgressBlocked)


# ----------------------------------------------------------- provenance ----

def test_manifest_records_checksums_and_detects_tampering():
    tmp = tempfile.mkdtemp()
    try:
        path = os.path.join(tmp, "d.csv")
        with open(path, "w") as fh:
            fh.write("a,b\n1,2\n")
        provenance.write_manifest(tmp, "t", "pub", "https://x/", ["d.csv"], max_age_days=30)
        ok, problems = provenance.verify(tmp)
        assert ok, problems
        with open(path, "a") as fh:
            fh.write("3,4\n")
        ok, problems = provenance.verify(tmp)
        assert not ok and any("checksum" in p for p in problems)
    finally:
        shutil.rmtree(tmp)


def test_staleness_budget_is_enforced():
    tmp = tempfile.mkdtemp()
    try:
        with open(os.path.join(tmp, "d.csv"), "w") as fh:
            fh.write("x\n")
        m = provenance.write_manifest(tmp, "t", "pub", "https://x/", ["d.csv"], max_age_days=14)
        assert not provenance.is_stale(m)
        m["fetched_at"] = "2000-01-01T00:00:00+00:00"
        with open(os.path.join(tmp, provenance.MANIFEST), "w") as fh:
            json.dump(m, fh)
        assert provenance.is_stale(provenance.read_manifest(tmp))
        ok, problems = provenance.verify(tmp)
        assert not ok and any("stale" in p for p in problems)
    finally:
        shutil.rmtree(tmp)


def test_a_directory_with_no_manifest_never_verifies():
    tmp = tempfile.mkdtemp()
    try:
        ok, problems = provenance.verify(tmp)
        assert not ok and "no MANIFEST.json" in problems
    finally:
        shutil.rmtree(tmp)


# ------------------------------------------------------------ hs_lookup ----

def _table():
    return hs_lookup.load()


def test_real_nomenclature_is_present_and_large():
    table = _table()
    assert len(table) > 6000, "run fetch_hs.py"
    assert table["854449"]["description"]


def test_dotted_codes_are_accepted():
    assert hs_lookup.clean("8544.49.99") == "85444999"


def test_eight_digit_line_resolves_its_hs6_parent_chain():
    r = hs_lookup.validate("8544.49.99", _table())
    assert r["valid"] and r["length"] == 8
    assert [n["hs_code"] for n in r["chain"]] == ["85", "8544", "854449"]
    assert r["national_extension"] == "99"


def test_odd_length_code_is_rejected():
    assert not hs_lookup.validate("85449", _table())["valid"]


def test_code_absent_from_the_nomenclature_is_rejected():
    r = hs_lookup.validate("85449799", _table())
    assert not r["valid"]
    assert any("not in the WCO nomenclature" in p for p in r["problems"])


def test_comtrade_chapter_99_is_not_accepted_as_a_classification():
    r = hs_lookup.validate("99999999", _table())
    assert not r["valid"]
    assert any("not a WCO trade chapter" in p for p in r["problems"])


def test_six_digit_code_is_valid_but_flagged_as_unfileable():
    r = hs_lookup.validate("854449", _table())
    assert r["valid"]
    assert any("8-digit" in p for p in r["problems"])


def test_search_finds_real_headings():
    hits = hs_lookup.search("lithium", _table())
    assert any(h["hs_code"] == "850650" for h in hits)


# ---------------------------------------------------- landed_cost wiring ----

def test_hsn_is_validated_against_the_real_nomenclature():
    ok, note = landed_cost.validate_hsn("85444999")
    assert ok and "854449" in note
    ok, note = landed_cost.validate_hsn("85449")
    assert not ok


def test_missing_bcd_and_igst_are_flagged_not_silently_zero():
    r = landed_cost.Shipment(
        {"fob": 100, "exchange_rate": 84, "freight": 1, "insurance": 1}
    ).compute()
    assert sum("treated as 0%" in n for n in r["notes"]) == 2


def test_supplied_rates_do_not_raise_the_zero_warning():
    r = landed_cost.Shipment(
        {
            "fob": 100, "exchange_rate": 84, "freight": 1, "insurance": 1,
            "bcd": 10, "igst": 18,
            "_rate_sources": {"bcd": "command line", "igst": "command line"},
        }
    ).compute()
    assert not any("treated as 0%" in n for n in r["notes"])


def test_auto_fills_rates_from_fetched_data_and_stamps_the_source():
    """--auto must take rates only from a fetched file, and record where from."""
    tmp = tempfile.mkdtemp()
    original = landed_cost.TARIFF_DIR
    try:
        landed_cost.TARIFF_DIR = tmp
        with open(os.path.join(tmp, "85444999.json"), "w") as fh:
            json.dump(
                {
                    "hsn": "85444999",
                    "retrieved_at": "2026-08-31T00:00:00+00:00",
                    "duty_heads": {
                        "bcd": {"rate": 10.0, "label": "Basic Duty"},
                        "igst": {"rate": 18.0, "label": "IGST"},
                    },
                },
                fh,
            )
        provenance.write_manifest(
            tmp, "icegate_tariff", "CBIC", "https://www.icegate.gov.in/cdc",
            ["85444999.json"], max_age_days=30,
        )
        rates, stamp = landed_cost.load_fetched_rates("8544.49.99")
        assert rates == {"bcd": 10.0, "igst": 18.0}
        assert "ICEGATE" in stamp and "STALE" not in stamp

        class Args:
            auto = True

        cfg = landed_cost.apply_data_layer(
            {"hsn": "85444999", "_rate_sources": {}}, Args()
        )
        assert cfg["bcd"] == 10.0 and cfg["igst"] == 18.0
        assert "ICEGATE" in cfg["_rate_sources"]["bcd"]
    finally:
        landed_cost.TARIFF_DIR = original
        shutil.rmtree(tmp)


def test_auto_does_not_overwrite_an_explicitly_supplied_rate():
    tmp = tempfile.mkdtemp()
    original = landed_cost.TARIFF_DIR
    try:
        landed_cost.TARIFF_DIR = tmp
        with open(os.path.join(tmp, "85444999.json"), "w") as fh:
            json.dump(
                {"retrieved_at": "x", "duty_heads": {"bcd": {"rate": 10.0, "label": "BCD"}}},
                fh,
            )

        class Args:
            auto = True

        cfg = landed_cost.apply_data_layer(
            {"hsn": "85444999", "bcd": 7.5, "_rate_sources": {"bcd": "command line"}}, Args()
        )
        assert cfg["bcd"] == 7.5
        assert cfg["_rate_sources"]["bcd"] == "command line"
    finally:
        landed_cost.TARIFF_DIR = original
        shutil.rmtree(tmp)


def test_auto_with_no_fetched_file_leaves_rates_unset_rather_than_guessing():
    tmp = tempfile.mkdtemp()
    original = landed_cost.TARIFF_DIR
    try:
        landed_cost.TARIFF_DIR = tmp

        class Args:
            auto = True

        cfg = landed_cost.apply_data_layer({"hsn": "85444999", "_rate_sources": {}}, Args())
        assert "bcd" not in cfg
        assert "run" in cfg["_hsn_note"]
    finally:
        landed_cost.TARIFF_DIR = original
        shutil.rmtree(tmp)


def test_stale_fetched_rates_are_marked_stale():
    tmp = tempfile.mkdtemp()
    original = landed_cost.TARIFF_DIR
    try:
        landed_cost.TARIFF_DIR = tmp
        with open(os.path.join(tmp, "85444999.json"), "w") as fh:
            json.dump(
                {"retrieved_at": "x", "duty_heads": {"bcd": {"rate": 10.0, "label": "BCD"}}}, fh
            )
        m = provenance.write_manifest(
            tmp, "icegate_tariff", "CBIC", "https://x/", ["85444999.json"], max_age_days=30
        )
        m["fetched_at"] = "2000-01-01T00:00:00+00:00"
        with open(os.path.join(tmp, provenance.MANIFEST), "w") as fh:
            json.dump(m, fh)
        _, stamp = landed_cost.load_fetched_rates("85444999")
        assert "STALE" in stamp
    finally:
        landed_cost.TARIFF_DIR = original
        shutil.rmtree(tmp)


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for fn in tests:
        try:
            fn()
        except AssertionError as exc:
            failed += 1
            print(f"FAIL  {fn.__name__}: {exc}")
        else:
            print(f"ok    {fn.__name__}")
    print(f"\n{len(tests) - failed} passed, {failed} failed")
    raise SystemExit(1 if failed else 0)
