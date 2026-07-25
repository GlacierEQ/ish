# APEX Sovereign MCP Hookup & Integration Guide (v9.0)

**Target Server:** APEX Omniversal Forensic MCP Engine v9.0  
**Device:** iPhone 16 Pro Max (iSH / Termux)  
**Port:** `9876`  
**Protocol:** MCP v1.0 / JSON-RPC 2.0  
**Security Key:** `2cc2286bc64cd1cc748fe43bc568b2d4f143181d5fe8563c`  

---

## ⚡ 1. Live Hookup Commands (Termux / iSH CLI)

To check status or force-start the self-healing MCP daemon anytime:
```bash
# Check status / auto-heal MCP supervisor
bash ~/bin/apex-mcp-supervisor.sh

# Verify live health probe
curl -s http://127.0.0.1:9876/health
```

---

## 📱 2. Connecting ChatGPT (Custom Actions / My GPTs)

### Step A: Enter Action Configuration
1. Open ChatGPT -> **My GPTs** -> **Create / Edit GPT** -> **Actions**.
2. **Authentication:** Select **API Key** -> **Bearer**.
3. **API Key:** Paste `2cc2286bc64cd1cc748fe43bc568b2d4f143181d5fe8563c`.

### Step B: Paste OpenAPI Hookup Schema
```json
{
  "openapi": "3.0.0",
  "info": { "title": "iPhone 16 Pro Max APEX MCP Server", "version": "9.0.0" },
  "servers": [{ "url": "http://YOUR_TAILSCALE_IP:9876" }],
  "paths": {
    "/": {
      "post": {
        "summary": "Execute MCP Tool Call",
        "operationId": "executeMcpTool",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "jsonrpc": { "type": "string", "example": "2.0" },
                  "id": { "type": "integer", "example": 1 },
                  "method": { "type": "string", "example": "tools/call" },
                  "params": {
                    "type": "object",
                    "properties": {
                      "name": { 
                        "type": "string", 
                        "enum": ["get_court_metadata", "read_file", "write_file", "list_dir"],
                        "example": "get_court_metadata" 
                      },
                      "arguments": { "type": "object" }
                    },
                    "required": ["name", "arguments"]
                  }
                },
                "required": ["jsonrpc", "method", "params"]
              }
            }
          }
        },
        "responses": { "200": { "description": "FRE 902 Self-Authenticating Result" } }
      }
    }
  }
}
```

---

## 🛠️ 3. Direct MCP Tools Hookup Manifest

| Tool Name | Direct Hookup Function | FRE 902 Certificate Output |
| :--- | :--- | :--- |
| **`get_court_metadata`** | Extract full court-prep metadata certificate | SHA-256 + Blake2b + MD5 + POSIX + Custody GUID |
| **`read_file`** | Read file with FRE 902 cryptographic verification | File content + Court Metadata JSON |
| **`write_file`** | Write/update file with automated court certification | Status WRITTEN + Court Metadata JSON |
| **`list_dir`** | Browse directories and examine storage trees | File listing with size & type metadata |
