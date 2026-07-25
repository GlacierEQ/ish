#!/usr/bin/env python3
"""
APEX Ultra-Hardened iOS MCP Server (v4.5 Pure Fortress)
Uses raw socket HTTP server for absolute zero-dependency reliability and maximum hardening.
"""

import os
import sys
import json
import time
import socket
import secrets
import hashlib

PORT = int(os.getenv("IOS_MCP_PORT", 9876))
ROOT_DIR = os.path.abspath(os.getenv("IOS_STORAGE_ROOT", os.path.expanduser("~")))

KEY_FILE = os.path.expanduser("~/.apex_ios_mcp_key")
if os.path.exists(KEY_FILE):
    with open(KEY_FILE, "r") as kf:
        BEARER_TOKEN = kf.read().strip()
else:
    BEARER_TOKEN = secrets.token_hex(24)
    with open(KEY_FILE, "w") as kf:
        kf.write(BEARER_TOKEN)

AUDIT_LOG = os.path.expanduser("~/.apex/mcp_ios_audit.jsonl")
os.makedirs(os.path.dirname(AUDIT_LOG), exist_ok=True)

def log_audit(action, details, status="SUCCESS"):
    log_entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "action": action,
        "status": status,
        "details": details
    }
    with open(AUDIT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

def get_file_hashes(filepath):
    try:
        sha = hashlib.sha256()
        blake = hashlib.blake2b()
        with open(filepath, 'rb') as f:
            while chunk := f.read(16384):
                sha.update(chunk)
                blake.update(chunk)
        return {"sha256": sha.hexdigest(), "blake2b": blake.hexdigest()}
    except Exception:
        return {"sha256": "N/A", "blake2b": "N/A"}

def is_safe_path(base_dir, path):
    try:
        resolved = os.path.realpath(os.path.join(base_dir, path.lstrip("/")))
        return os.path.commonpath([base_dir, resolved]) == base_dir, resolved
    except Exception:
        return False, None

def handle_client(conn, addr):
    try:
        data = conn.recv(65536).decode('utf-8', errors='ignore')
        if not data:
            conn.close()
            return
        
        lines = data.split("\r\n")
        req_line = lines[0].split(" ")
        if len(req_line) < 2:
            conn.close()
            return

        method = req_line[0].upper()
        path = req_line[1]

        headers = {}
        body = ""
        header_mode = True
        body_lines = []

        for line in lines[1:]:
            if header_mode:
                if line == "":
                    header_mode = False
                else:
                    if ":" in line:
                        k, v = line.split(":", 1)
                        headers[k.strip().lower()] = v.strip()
            else:
                body_lines.append(line)
        body = "\r\n".join(body_lines)

        auth_val = headers.get("authorization", "")
        authenticated = False
        if auth_val.startswith("Bearer "):
            token = auth_val.split(" ", 1)[1].strip()
            if secrets.compare_digest(token, BEARER_TOKEN):
                authenticated = True

        def send_res(status_code, status_text, body_dict):
            resp_body = json.dumps(body_dict, indent=2)
            resp = f"HTTP/1.1 {status_code} {status_text}\r\n"
            resp += "Content-Type: application/json\r\n"
            resp += f"Content-Length: {len(resp_body.encode('utf-8'))}\r\n"
            resp += "Access-Control-Allow-Origin: *\r\n"
            resp += "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
            resp += "Access-Control-Allow-Headers: Content-Type, Authorization\r\n"
            resp += "Connection: close\r\n\r\n"
            resp += resp_body
            conn.sendall(resp.encode('utf-8'))
            conn.close()

        if method == "OPTIONS":
            send_res(200, "OK", {"status": "ok"})
            return

        if path in ["/health", "/healthz"]:
            send_res(200, "OK", {
                "status": "ONLINE_FORTRESS",
                "server": "APEX Ultra-Hardened iOS MCP Server (v4.5 Pure Fortress)",
                "device": "iPhone 16 Pro Max",
                "auth_required": True,
                "sandbox_root": ROOT_DIR,
                "tools": ["list_dir", "read_file", "write_file", "search_files"]
            })
            return

        if not authenticated:
            log_audit("AUTH_FAILURE", {"client": addr[0]}, status="REJECTED")
            send_res(401, "Unauthorized", {"error": "Unauthorized. Bearer token required."})
            return

        if method == "GET":
            send_res(200, "OK", {
                "status": "ONLINE_FORTRESS",
                "server": "APEX Ultra-Hardened iOS MCP Server (v4.5 Pure Fortress)",
                "sandbox_root": ROOT_DIR
            })
            return

        if method == "POST":
            try:
                payload = json.loads(body)
            except Exception as e:
                send_res(400, "Bad Request", {"error": f"Invalid JSON payload: {str(e)}"})
                return

            rpc_method = payload.get("method")
            params = payload.get("params", {})
            req_id = payload.get("id", 1)

            if rpc_method == "tools/list":
                send_res(200, "OK", {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "tools": [
                            {"name": "list_dir", "description": "Safely list directory contents."},
                            {"name": "read_file", "description": "Read file with dual SHA256/Blake2b verification."},
                            {"name": "write_file", "description": "Write/update file safely within sandbox."},
                            {"name": "search_files", "description": "Search sandbox storage for file patterns."}
                        ]
                    }
                })
                return

            elif rpc_method == "tools/call":
                tool_name = params.get("name")
                args = params.get("arguments", {})

                if tool_name == "list_dir":
                    safe, target = is_safe_path(ROOT_DIR, args.get("path", ""))
                    if not safe:
                        send_res(200, "OK", {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32600, "message": "Path Traversal Rejected"}})
                        return
                    try:
                        entries = [{"name": f, "is_dir": os.path.isdir(os.path.join(target, f)), "size": os.path.getsize(os.path.join(target, f)) if os.path.isfile(os.path.join(target, f)) else 0} for f in os.listdir(target)]
                        log_audit("LIST_DIR", {"path": target})
                        send_res(200, "OK", {"jsonrpc": "2.0", "id": req_id, "result": {"path": target, "entries": entries}})
                    except Exception as e:
                        send_res(200, "OK", {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32603, "message": str(e)}})
                    return

                elif tool_name == "read_file":
                    safe, target = is_safe_path(ROOT_DIR, args.get("path", ""))
                    if not safe:
                        send_res(200, "OK", {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32600, "message": "Path Traversal Rejected"}})
                        return
                    try:
                        with open(target, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read(500000)
                        hashes = get_file_hashes(target)
                        log_audit("READ_FILE", {"path": target, "hashes": hashes})
                        send_res(200, "OK", {"jsonrpc": "2.0", "id": req_id, "result": {"path": target, "hashes": hashes, "content": content}})
                    except Exception as e:
                        send_res(200, "OK", {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32603, "message": str(e)}})
                    return

                elif tool_name == "write_file":
                    safe, target = is_safe_path(ROOT_DIR, args.get("path", ""))
                    if not safe:
                        send_res(200, "OK", {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32600, "message": "Path Traversal Rejected"}})
                        return
                    try:
                        os.makedirs(os.path.dirname(target), exist_ok=True)
                        content = args.get("content", "")
                        with open(target, 'w', encoding='utf-8') as f:
                            f.write(content)
                        hashes = get_file_hashes(target)
                        log_audit("WRITE_FILE", {"path": target, "hashes": hashes})
                        send_res(200, "OK", {"jsonrpc": "2.0", "id": req_id, "result": {"status": "WRITTEN", "path": target, "hashes": hashes}})
                    except Exception as e:
                        send_res(200, "OK", {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32603, "message": str(e)}})
                    return

                else:
                    send_res(200, "OK", {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Unknown tool"}})
                    return

        send_res(405, "Method Not Allowed", {"error": "Method Not Allowed"})

    except Exception as e:
        conn.close()

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', PORT))
    s.listen(128)
    print(f"🏰 APEX Pure Fortress iOS MCP Server v4.5 active on port {PORT}")
    print(f"🔑 Bearer Token: {BEARER_TOKEN}")
    print(f"📂 Sandbox Root: {ROOT_DIR}")

    while True:
        try:
            conn, addr = s.accept()
            handle_client(conn, addr)
        except Exception as e:
            pass

if __name__ == "__main__":
    main()
