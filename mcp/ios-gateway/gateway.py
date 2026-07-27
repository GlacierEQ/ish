#!/usr/bin/env python3
"""Read-only local MCP sidecar. JSON-RPC 2.0, one request/object per stdin line.
Do not expose stdin/stdout directly to a network socket without mTLS and a reviewed
pairing layer. Export records are local JSON files written by a trusted ingestion path.
"""
from __future__ import annotations
import argparse, hashlib, hmac, json, os, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROTOCOL_VERSION = "2024-11-05"
KINDS = ("photos", "documents", "contacts", "calendar", "health", "imports")

class Gateway:
    def __init__(self, data_dir: Path, config: dict[str, Any]) -> None:
        self.data_dir, self.config = data_dir, config
        self.scopes = set(config.get("allowed_scopes", []))
        self.max_results = min(int(config.get("max_results", 100)), 500)

    def records(self, kind: str) -> list[dict[str, Any]]:
        if kind not in KINDS or kind not in self.scopes:
            raise PermissionError(f"scope not granted: {kind}")
        path = self.data_dir / f"{kind}.json"
        if not path.exists(): return []
        # Reject oversized data rather than consuming unlimited memory.
        if path.stat().st_size > 10 * 1024 * 1024: raise ValueError("dataset exceeds 10 MiB limit")
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, list) or not all(isinstance(x, dict) for x in value):
            raise ValueError("dataset must be a JSON array of objects")
        return value

    def list_records(self, args: dict[str, Any]) -> dict[str, Any]:
        kind = args.get("kind")
        if not isinstance(kind, str): raise ValueError("kind is required")
        limit = args.get("limit", self.max_results)
        if not isinstance(limit, int) or not 1 <= limit <= self.max_results: raise ValueError("invalid limit")
        query = args.get("query", "")
        if not isinstance(query, str) or len(query) > 256: raise ValueError("invalid query")
        rows = self.records(kind)
        # Simple local text filter; clients should not assume every field is searchable.
        needle = query.casefold()
        if needle: rows = [r for r in rows if needle in json.dumps(r, ensure_ascii=False).casefold()]
        return {"kind": kind, "records": rows[:limit], "truncated": len(rows) > limit}

    def get_record(self, args: dict[str, Any]) -> dict[str, Any]:
        kind, record_id = args.get("kind"), args.get("id")
        if not isinstance(kind, str) or not isinstance(record_id, str): raise ValueError("kind and id are required")
        for record in self.records(kind):
            if hmac.compare_digest(str(record.get("id", "")), record_id): return {"kind": kind, "record": record}
        raise LookupError("record not found")

    def handle(self, req: dict[str, Any]) -> dict[str, Any] | None:
        request_id = req.get("id")
        if req.get("jsonrpc") != "2.0" or not isinstance(req.get("method"), str):
            return error(request_id, -32600, "invalid request")
        method, params = req["method"], req.get("params", {})
        if not isinstance(params, dict): return error(request_id, -32602, "params must be an object")
        try:
            if method == "initialize": result = {"protocolVersion": PROTOCOL_VERSION, "capabilities": {"tools": {}, "resources": {}}, "serverInfo": {"name": "iphone-consent-sidecar", "version": "0.1.0"}}
            elif method == "tools/list": result = {"tools": tools()}
            elif method == "tools/call": result = tool_call(self, params)
            elif method == "resources/list": result = {"resources": [{"uri": f"iphone://{k}", "name": f"Authorized {k}", "mimeType": "application/json"} for k in sorted(self.scopes & set(KINDS))]}
            elif method == "resources/read":
                uri = params.get("uri", ""); kind = uri.removeprefix("iphone://") if isinstance(uri, str) else ""
                result = {"contents": [{"uri": uri, "mimeType": "application/json", "text": json.dumps(self.records(kind), ensure_ascii=False)}]}
            elif method.startswith("notifications/"): return None
            else: return error(request_id, -32601, "method not found")
            return {"jsonrpc": "2.0", "id": request_id, "result": result} if "id" in req else None
        except PermissionError as e: return error(request_id, -32001, str(e))
        except (ValueError, LookupError, json.JSONDecodeError) as e: return error(request_id, -32602, str(e))
        except Exception: return error(request_id, -32603, "internal error")

def tools() -> list[dict[str, Any]]:
    schema = {"type":"object", "properties":{"kind":{"type":"string","enum":list(KINDS)}, "limit":{"type":"integer","minimum":1,"maximum":500}, "query":{"type":"string","maxLength":256}}, "required":["kind"], "additionalProperties":False}
    return [{"name":"iphone_list_authorized_records", "description":"Lists user-authorized, locally exported iPhone records. Scope controls access; it cannot read device filesystem, calls, or voicemail.", "inputSchema":schema}, {"name":"iphone_get_authorized_record", "description":"Gets one previously exported record by opaque ID.", "inputSchema":{"type":"object","properties":{"kind":{"type":"string","enum":list(KINDS)},"id":{"type":"string","maxLength":256}},"required":["kind","id"],"additionalProperties":False}}]

def tool_call(gateway: Gateway, params: dict[str, Any]) -> dict[str, Any]:
    name, arguments = params.get("name"), params.get("arguments", {})
    if not isinstance(arguments, dict): raise ValueError("arguments must be object")
    if name == "iphone_list_authorized_records": value = gateway.list_records(arguments)
    elif name == "iphone_get_authorized_record": value = gateway.get_record(arguments)
    else: raise ValueError("unknown tool")
    return {"content": [{"type":"text", "text": json.dumps(value, ensure_ascii=False)}], "isError": False}

def error(request_id: Any, code: int, message: str) -> dict[str, Any]: return {"jsonrpc":"2.0", "id":request_id, "error":{"code":code,"message":message}}

def main() -> int:
    p = argparse.ArgumentParser(); p.add_argument("--data-dir", required=True); p.add_argument("--config", required=True); args = p.parse_args()
    try:
        config = json.loads(Path(args.config).read_text(encoding="utf-8"))
        # Fail closed: a pairing secret proves config was deliberately initialized.
        secret = config.get("pairing_secret")
        if not isinstance(secret, str) or len(secret) < 32: raise ValueError("pairing_secret must be at least 32 characters")
    except Exception as e: print(f"configuration error: {e}", file=sys.stderr); return 2
    gateway = Gateway(Path(args.data_dir), config)
    for line in sys.stdin:
        if len(line) > 1_100_000: print(json.dumps(error(None, -32700, "request too large")), flush=True); continue
        try: req = json.loads(line); response = gateway.handle(req) if isinstance(req, dict) else error(None, -32600, "invalid request")
        except json.JSONDecodeError: response = error(None, -32700, "parse error")
        if response is not None: print(json.dumps(response, ensure_ascii=False, separators=(",", ":")), flush=True)
    return 0
if __name__ == "__main__": raise SystemExit(main())
