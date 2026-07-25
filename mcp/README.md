# APEX iOS MCP Server Deployment & Configuration Guide
**Device Target:** iPhone 16 Pro Max (iOS 17/18+)  
**Server Component:** `apex_ios_mcp_server.py`  
**Supported Models:** ChatGPT (Custom Actions / MCP), Grok, Perplexity, Claude, APEX Agents  

---

## 📱 1. Overview & Capability
The APEX iOS MCP Server transforms your iPhone 16 Pro Max into an active Model Context Protocol node. It provides remote AI models with full, authorized read/write access to files stored in the iOS Files app or iSH Linux container.

### Supported MCP Tools
- **`list_dir`**: Browse directories and examine file sizes.
- **`read_file`**: Read file content with automated SHA-256 evidentiary hashing.
- **`write_file`**: Create new files or modify existing documents on your iPhone.
- **`search_files`**: Search storage for target documents or case evidence.

---

## ⚡ 2. Quick Setup Instructions

### Step A: Deploy to iSH (on iPhone 16 Pro Max)
1. Install **iSH Terminal** from the iOS App Store.
2. Inside iSH, clone or copy `apex_ios_mcp_server.py`:
   ```bash
   python3 apex_ios_mcp_server.py &
   ```
3. To grant access to iOS Files app folders (e.g. iCloud Drive or On My iPhone):
   ```bash
   mount -t ios . /mnt/iphone_files
   ```

### Step B: Connect via Tailscale (Secure Mesh Networking)
1. Install **Tailscale** on your iPhone.
2. Enable Tailscale to assign an IP (e.g., `100.x.y.z`).
3. Your server will be securely reachable over your private tailnet at `http://100.x.y.z:8765`.

---

## 🔌 3. Connecting AI Clients

### ChatGPT / Custom GPT Integration
In your ChatGPT Custom GPT configuration, add a Custom Action pointing to your iPhone's endpoint:
```json
{
  "openapi": "3.0.0",
  "info": { "title": "iPhone 16 Pro Max MCP API", "version": "1.0.0" },
  "servers": [{ "url": "http://100.x.y.z:8765" }],
  "paths": {
    "/": {
      "post": {
        "summary": "Execute MCP Tool Call",
        "requestBody": {
          "required": true,
          "content": { "application/json": {} }
        }
      }
    }
  }
}
```

### Grok & Perplexity API Integration
In Grok or Perplexity tool configs, specify the MCP server URL:
- **Protocol:** JSON-RPC / MCP v1.0
- **Endpoint:** `http://100.x.y.z:8765/`

---

## 🛡️ 4. Keeping Server Alive in Background (iOS Persistent Execution)
To prevent iOS from closing the background process when the keyboard closes or app switches:
- Enable **Location / Audio Background Refresh** in iSH settings.
- Or use **Blink Shell** with background location/keep-alive enabled.
