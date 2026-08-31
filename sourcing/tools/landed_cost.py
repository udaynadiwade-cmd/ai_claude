#!/usr/bin/env python3
"""Indian import landed-cost calculator.

Arithmetic only. This tool does NOT know duty rates: every rate (BCD, AIDC,
IGST, ADD, safeguard, cess) must be supplied by the caller after a lookup on
ICEGATE / the CBIC tariff / the relevant notification. That is deliberate --
guessing a rate here would be worse than not computing at all.

Assessment order follows the standard customs sequence:

    Assessable Value (AV) = FOB + freight + insurance      (all in INR)
    BCD   = AV x bcd%
    AIDC  = AV x aidc%
    SWS   = (sum of the heads named by --sws-base) x sws%
    ADD / SG / other specific duties are added as supplied
    IGST base = AV + BCD + AIDC + SWS + ADD + SG + other
    IGST  = IGST base x igst%
    Comp cess = IGST base x cess%

Usage:
    python3 landed_cost.py --config shipment.json
    python3 landed_cost.py --fob 25000 --currency USD --rate 84.50 \
        --freight 1800 --bcd 10 --igst 18
"""

from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal, ROUND_HALF_UP

TWO = Decimal("0.01")

# Rule 10(2) of the Customs Valuation (Determination of Value of Imported Goods)
# Rules, 2007 prescribes a notional insurance loading where the actual cost is
# not ascertainable. Confirm the current percentage against the Rules before
# relying on the default -- see reference/landed-cost.md.
NOTIONAL_INSURANCE_PCT = Decimal("1.125")

# Notional freight loading where actual freight is not ascertainable. Verify
# against the Valuation Rules for the mode of transport before use.
NOTIONAL_FREIGHT_PCT = Decimal("20")

SWS_BASE_CHOICES = ("bcd", "bcd+aidc")


def d(value) -> Decimal:
    """Coerce to Decimal without float noise."""
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def money(value: Decimal) -> Decimal:
    return d(value).quantize(TWO, rounding=ROUND_HALF_UP)


def pct(base: Decimal, rate: Decimal) -> Decimal:
    return d(base) * d(rate) / Decimal("100")


class Shipment:
    """One consignment, valued and assessed in INR."""

    def __init__(self, cfg: dict):
        self.description = cfg.get("description", "")
        self.hsn = cfg.get("hsn", "")
        self.origin = cfg.get("origin", "")
        self.incoterm = (cfg.get("incoterm") or "FOB").upper()
        self.port = cfg.get("port", "")

        self.currency = cfg.get("currency", "USD")
        self.rate = d(cfg.get("exchange_rate", 1))
        self.fob_fc = d(cfg.get("fob", 0))

        self.freight_fc = cfg.get("freight")
        self.insurance_fc = cfg.get("insurance")
        self.insurance_pct = d(cfg.get("insurance_pct", NOTIONAL_INSURANCE_PCT))
        self.freight_pct = d(cfg.get("freight_pct", NOTIONAL_FREIGHT_PCT))

        self.bcd_rate = d(cfg.get("bcd", 0))
        self.aidc_rate = d(cfg.get("aidc", 0))
        self.sws_rate = d(cfg.get("sws", 10))
        self.sws_base = cfg.get("sws_base", "bcd")
        self.igst_rate = d(cfg.get("igst", 0))
        self.cess_rate = d(cfg.get("comp_cess", 0))

        # Specific / ad-valorem trade-remedy duties, supplied as INR amounts or
        # as a percentage of AV via the *_pct keys.
        self.add_inr = d(cfg.get("add", 0))
        self.add_pct = d(cfg.get("add_pct", 0))
        self.sg_inr = d(cfg.get("safeguard", 0))
        self.sg_pct = d(cfg.get("safeguard_pct", 0))
        self.other_duty = d(cfg.get("other_duty", 0))

        # Post-clearance costs: CHA, CFS, transport, ICD haulage, bank charges.
        self.local_charges = d(cfg.get("local_charges", 0))
        self.igst_creditable = bool(cfg.get("igst_creditable", True))
        self.quantity = d(cfg.get("quantity", 0))

        if self.sws_base not in SWS_BASE_CHOICES:
            raise ValueError(f"sws_base must be one of {SWS_BASE_CHOICES}")
        if self.rate <= 0:
            raise ValueError("exchange_rate must be greater than zero")
        if self.fob_fc <= 0:
            raise ValueError("fob must be greater than zero")

    # -- valuation ---------------------------------------------------------

    def compute(self) -> dict:
        notes = []

        fob_inr = self.fob_fc * self.rate

        if self.freight_fc is None:
            freight_inr = pct(fob_inr, self.freight_pct)
            notes.append(
                f"Freight not supplied: loaded notionally at {self.freight_pct}% of FOB. "
                "Replace with the actual freight on the invoice/BL before filing."
            )
        else:
            freight_inr = d(self.freight_fc) * self.rate

        if self.insurance_fc is None:
            insurance_inr = pct(fob_inr, self.insurance_pct)
            notes.append(
                f"Insurance not supplied: loaded notionally at {self.insurance_pct}% of FOB "
                "(Customs Valuation Rules, Rule 10(2)). Verify the current rate."
            )
        else:
            insurance_inr = d(self.insurance_fc) * self.rate

        av = fob_inr + freight_inr + insurance_inr

        bcd = pct(av, self.bcd_rate)
        aidc = pct(av, self.aidc_rate)
        sws_base = bcd if self.sws_base == "bcd" else bcd + aidc
        sws = pct(sws_base, self.sws_rate)

        add = self.add_inr + pct(av, self.add_pct)
        safeguard = self.sg_inr + pct(av, self.sg_pct)

        igst_base = av + bcd + aidc + sws + add + safeguard + self.other_duty
        igst = pct(igst_base, self.igst_rate)
        comp_cess = pct(igst_base, self.cess_rate)

        total_duty = bcd + aidc + sws + add + safeguard + self.other_duty + igst + comp_cess
        non_creditable = total_duty - igst if self.igst_creditable else total_duty

        landed = av + total_duty + self.local_charges
        effective = av + non_creditable + self.local_charges

        result = {
            "header": {
                "description": self.description,
                "hsn": self.hsn,
                "origin": self.origin,
                "incoterm": self.incoterm,
                "port": self.port,
                "currency": self.currency,
                "exchange_rate": self.rate,
            },
            "valuation": {
                f"FOB ({self.currency} {self.fob_fc})": money(fob_inr),
                "Freight": money(freight_inr),
                "Insurance": money(insurance_inr),
                "Assessable Value (CIF)": money(av),
            },
            "duties": {
                f"BCD @ {self.bcd_rate}%": money(bcd),
                f"AIDC @ {self.aidc_rate}%": money(aidc),
                f"SWS @ {self.sws_rate}% on {self.sws_base.upper()}": money(sws),
                "Anti-dumping duty": money(add),
                "Safeguard duty": money(safeguard),
                "Other duty": money(self.other_duty),
                f"IGST @ {self.igst_rate}%": money(igst),
                f"Compensation cess @ {self.cess_rate}%": money(comp_cess),
            },
            "totals": {
                "IGST taxable base": money(igst_base),
                "Total duty payable at customs": money(total_duty),
                "Duty net of creditable IGST": money(non_creditable),
                "Local charges (CHA/CFS/transport)": money(self.local_charges),
                "Landed cost (cash outflow)": money(landed),
                "Effective landed cost (IGST credited back)"
                if self.igst_creditable
                else "Effective landed cost": money(effective),
            },
            "notes": notes,
        }

        if self.quantity > 0:
            result["totals"]["Effective cost per unit"] = money(effective / self.quantity)

        return result


def render(result: dict) -> str:
    out = []
    head = result["header"]
    title = head["description"] or "Import consignment"
    out.append(f"LANDED COST — {title}")
    meta = [
        f"ITC(HS): {head['hsn'] or 'NOT SUPPLIED'}",
        f"Origin: {head['origin'] or 'NOT SUPPLIED'}",
        f"Incoterm: {head['incoterm']}",
        f"Port: {head['port'] or 'NOT SUPPLIED'}",
        f"FX: 1 {head['currency']} = INR {head['exchange_rate']}",
    ]
    out.append(" | ".join(meta))
    out.append("=" * 72)

    for section in ("valuation", "duties", "totals"):
        out.append(section.upper())
        for label, amount in result[section].items():
            if amount == 0 and section == "duties":
                continue
            out.append(f"  {label:<52} {amount:>16,}")
        out.append("")

    if result["notes"]:
        out.append("NOTES")
        for note in result["notes"]:
            out.append(f"  ! {note}")
        out.append("")

    out.append(
        "All rates are caller-supplied. Verify BCD/AIDC/IGST/ADD against the CBIC tariff "
        "and the operative notification on ICEGATE before filing the Bill of Entry."
    )
    return "\n".join(out)


def parse_args(argv):
    p = argparse.ArgumentParser(description="Indian import landed-cost calculator")
    p.add_argument("--config", help="JSON file with the shipment parameters")
    p.add_argument("--fob", type=float, help="FOB value in foreign currency")
    p.add_argument("--currency", default="USD")
    p.add_argument("--rate", type=float, help="CBIC notified exchange rate to INR")
    p.add_argument("--freight", type=float, help="Actual freight in foreign currency")
    p.add_argument("--insurance", type=float, help="Actual insurance in foreign currency")
    p.add_argument("--bcd", type=float, default=0.0, help="BCD rate %%")
    p.add_argument("--aidc", type=float, default=0.0, help="AIDC rate %%")
    p.add_argument("--sws", type=float, default=10.0, help="SWS rate %%")
    p.add_argument("--sws-base", choices=SWS_BASE_CHOICES, default="bcd")
    p.add_argument("--igst", type=float, default=0.0, help="IGST rate %%")
    p.add_argument("--add-pct", type=float, default=0.0, help="Anti-dumping duty as %% of AV")
    p.add_argument("--local-charges", type=float, default=0.0, help="CHA/CFS/transport in INR")
    p.add_argument("--quantity", type=float, default=0.0)
    p.add_argument("--hsn", default="")
    p.add_argument("--origin", default="")
    p.add_argument("--incoterm", default="FOB")
    p.add_argument("--port", default="")
    p.add_argument("--json", action="store_true", help="Emit JSON instead of a table")
    return p.parse_args(argv)


def config_from_args(args) -> dict:
    if args.config:
        with open(args.config, encoding="utf-8") as fh:
            return json.load(fh)
    if args.fob is None or args.rate is None:
        raise SystemExit("--fob and --rate are required when --config is not used")
    return {
        "fob": args.fob,
        "currency": args.currency,
        "exchange_rate": args.rate,
        "freight": args.freight,
        "insurance": args.insurance,
        "bcd": args.bcd,
        "aidc": args.aidc,
        "sws": args.sws,
        "sws_base": args.sws_base,
        "igst": args.igst,
        "add_pct": args.add_pct,
        "local_charges": args.local_charges,
        "quantity": args.quantity,
        "hsn": args.hsn,
        "origin": args.origin,
        "incoterm": args.incoterm,
        "port": args.port,
    }


def main(argv=None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    result = Shipment(config_from_args(args)).compute()
    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(render(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
