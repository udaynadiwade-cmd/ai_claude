#!/usr/bin/env python3
"""
Shoonya as a Claude connector. Read-only.

Claude ships no Shoonya connector and Shoonya publishes none, so this is
the custom one: a small MCP server that logs in to Shoonya's API with the
credentials in .env and exposes today's books as tools. Register its
public URL in claude.ai and any chat can pull the books directly.

Run it on a machine in India (Shoonya refuses foreign addresses):

    pip install "mcp>=2" uvicorn
    python3 shoonya_mcp.py          # http://127.0.0.1:8765/<secret>/mcp

Expose it to Anthropic's servers with a tunnel — either:

    cloudflared tunnel --url http://127.0.0.1:8765        # new URL each start
    ngrok http 8765 --url <yours>.ngrok-free.app          # stable free URL

Then in claude.ai: Customize -> Connectors -> + -> Add custom connector.
Name "Shoonya", URL https://<tunnel-host>/<secret>/mcp, no OAuth. Enable it
in the chat's connector settings and ask for the tradebook.

The secret path is the only lock on this door, so the full URL is a
credential — keep it private. Every tool is read-only: no order placement,
no funds, no modification, and none will be added here.

MCP_SECRET in .env is the path secret; generated and saved on first run.
"""

import json
import secrets
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import daily_report as dr  # noqa: E402

try:
    import uvicorn
    from mcp.server.mcpserver import MCPServer
    from mcp.server.mcpserver.server import TransportSecuritySettings
except ImportError:
    sys.exit('pip install "mcp>=2" uvicorn')

PORT = 8765
server = MCPServer(
    "Shoonya",
    instructions="Read-only access to today's Shoonya books for the Business "
                 "Onlooker desk: fills, orders (with rejections), positions, "
                 "and the rule-check report with taxes and charges.")

_sess = {"uid": None, "token": None, "at": 0.0}


def env():
    return dr.load_env()


def login(force=False):
    if not force and _sess["token"] and time.time() - _sess["at"] < 6 * 3600:
        return _sess["uid"], _sess["token"]
    uid, tok = dr.shoonya_login(env())          # SystemExit carries the reason
    _sess.update(uid=uid, token=tok, at=time.time())
    return uid, tok


def call(path, with_actid=False):
    """One Noren call, re-logging in once if the session has expired."""
    e = env()
    for attempt in (0, 1):
        try:
            uid, tok = login(force=bool(attempt))
        except SystemExit as ex:
            return {"error": str(ex)}
        extra = {"actid": uid} if with_actid else {}
        body = f"jData={json.dumps({'uid': uid, **extra})}&jKey={tok}"
        try:
            res = dr.post(f"{dr.shoonya_base(e)}/{path}", body, dr.FORM)
        except Exception as ex:                  # HTTP 502 abroad, network, etc.
            return {"error": f"{path}: {ex}"}
        if isinstance(res, list):
            return res
        if attempt == 0 and "session" in str(res.get("emsg", "")).lower():
            continue
        return []                                # {"stat":"Not_Ok","emsg":"no data"}
    return []


def trim(rows, keys):
    if isinstance(rows, dict):                   # error
        return rows
    return [{k: r.get(k) for k in keys if k in r} for r in rows]


@server.tool()
def status() -> str:
    """Is the Shoonya connection alive? Logs in and reports client id (masked) and time."""
    try:
        uid, _ = login(force=True)
    except SystemExit as ex:
        return json.dumps({"connected": False, "error": str(ex)})
    return json.dumps({"connected": True, "client": uid[:2] + "***" + uid[-2:],
                       "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})


@server.tool()
def tradebook() -> str:
    """Today's fills (Shoonya TradeBook): symbol, side, fill qty/price/time. Read-only."""
    return json.dumps(trim(call("TradeBook", with_actid=True),
                           ["tsym", "trantype", "flqty", "flprc", "fltm", "prd", "norenordno"]))


@server.tool()
def orderbook() -> str:
    """Today's orders (Shoonya OrderBook) incl. REJECTED with the broker's reason. Read-only."""
    return json.dumps(trim(call("OrderBook"),
                           ["tsym", "trantype", "qty", "prc", "prctyp", "status",
                            "rejreason", "norentm", "prd", "norenordno"]))


@server.tool()
def positions() -> str:
    """Today's net positions (Shoonya PositionBook): qty, realised P&L, MTM. Read-only."""
    return json.dumps(trim(call("PositionBook", with_actid=True),
                           ["tsym", "netqty", "daybuyqty", "daysellqty", "netavgprc",
                            "rpnl", "urmtom", "lp", "prd"]))


@server.tool()
def report(flat_by: str = "15:00") -> str:
    """Run the desk's post-mortem on today's fills: win rate, R:R, taxes and
    charges by component (Shoonya rate card), rule breaches, every trade."""
    fills = call("TradeBook", with_actid=True)
    if isinstance(fills, dict):
        return fills["error"]
    if not fills:
        return "No fills today."
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(fills, f)
    cmd = [sys.executable, str(HERE / "analyze_trades.py"), f.name, "--flat-by", flat_by]
    n500 = HERE / "data" / "nifty500.txt"
    if n500.exists():
        cmd += ["--n500", str(n500)]
    e = env()
    if e.get("CAPITAL_PER_STOCK"):
        cmd += ["--capital", e["CAPITAL_PER_STOCK"]]
    r = subprocess.run(cmd, capture_output=True, text=True)
    Path(f.name).unlink(missing_ok=True)
    return (r.stdout + r.stderr).strip()


def secret_path():
    e = env()
    if e.get("MCP_SECRET"):
        return e["MCP_SECRET"]
    s = secrets.token_urlsafe(24)
    with open(HERE / ".env", "a") as f:
        f.write(f"\n# Path secret for shoonya_mcp.py — the URL is a credential\nMCP_SECRET={s}\n")
    return s


def main():
    missing = [k for k in dr.SHOONYA_KEYS if not env().get(k)]
    if missing:
        sys.exit(f"Missing {', '.join(missing)} in .env. Run: python3 connect.py")
    path = f"/{secret_path()}/mcp"
    app = server.streamable_http_app(
        streamable_http_path=path, stateless_http=True, json_response=True,
        # Requests arrive through a tunnel with its own Host header.
        transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False))
    print(f"Shoonya connector on http://127.0.0.1:{PORT}{path}\n"
          f"Tunnel it, then add https://<tunnel-host>{path} in claude.ai as a custom connector.")
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")


if __name__ == "__main__":
    main()
