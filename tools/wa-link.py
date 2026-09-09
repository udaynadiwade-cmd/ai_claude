#!/usr/bin/env python3
"""
Generate a WhatsApp click-to-chat link.

Opening the link on the phone (or WhatsApp Web) opens a chat with that number
with the message already typed in. You press send. The message goes from YOUR
number, from your own WhatsApp account.

No API, no cost, no setup, no WhatsApp terms-of-service risk.

Usage:
    python3 tools/wa-link.py 9640769453 "message text"
    python3 tools/wa-link.py 9640769453 --file message.txt
"""
import sys, urllib.parse

def normalise(num: str, default_cc: str = "91") -> str:
    """Strip formatting and ensure a country code. Defaults to India."""
    d = "".join(c for c in num if c.isdigit())
    if len(d) == 10:            # bare Indian mobile
        d = default_cc + d
    elif d.startswith("0"):     # domestic trunk prefix
        d = default_cc + d[1:]
    return d

def main():
    args = sys.argv[1:]
    if len(args) < 2:
        print(__doc__.strip())
        sys.exit(1)
    number = normalise(args[0])
    if args[1] == "--file":
        text = open(args[2]).read()
    else:
        text = args[1]
    print(f"https://wa.me/{number}?text={urllib.parse.quote(text.strip())}")

if __name__ == "__main__":
    main()
