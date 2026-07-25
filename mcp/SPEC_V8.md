# APEX Omniversal Apple & Cloud Engine v8.0 (Omni-Sovereign Supremacy)

**Target Hardware:** iPhone 16 Pro Max (iSH / Termux), iPad Pro, macOS Workstations  
**Active Port:** `9876`  
**Security Gateway:** Constant-time Bearer Token (`~/.apex_ios_mcp_key`)  
**Audit Ledger:** `~/.apex/mcp_ios_audit.jsonl` (SHA-256: `e4b28df129...`)  

---

## 🛠️ Complete 13-Tool Omni-Sovereign Toolbelt

| Category | MCP Tool | Purpose & Forensic Function | Hardening Guard |
| :--- | :--- | :--- | :--- |
| **Audio Evidence** | `voice_memos` | Index `.m4a` recordings, SHA-256 hash audio, trigger WhisperX pipeline. | Sandbox boundary check |
| **Legal Contacts** | `apple_contacts` | Manage legal counsel, process servers, and court clerk contact registers. | Persistence validation |
| **Safari Research** | `safari_research` | Auto-capture CourtListener dockets & legal research bookmarks. | Structured JSON store |
| **Health Telemetry**| `apple_health` | Monitor biometric stress, step count, and heart rate during trial prep. | Telemetry validation |
| **Notion Sync** | `notion_case_sync` | Sync 349 triaged PRIORITY legal chats into Notion workspace. | SQLite control query |
| **SQL Engine** | `motherduck_query` | Run instant SQL forensic queries over DuckDB/SQLite chat database. | Query safety check |
| **iMessage/SMS** | `imessage_store` | Log, send, or query iMessage/SMS communication evidence. | Immutable ledger |
| **Photos Vault** | `photos_vault` | Manage Photos & Media evidence vault with EXIF metadata & SHA-256. | Asset hashes |
| **Apple Mail** | `apple_mail` | Draft, archive, or list Apple Mail communications. | Mail store audit |
| **iCloud Drive** | `icloud_drive` | Inspect iCloud Drive sync status and cloud document storage. | Mobile documents index |
| **Filesystem** | `list_dir` | Safely list directory contents with size and metadata. | Realpath guard (`is_safe_path`) |
| **Filesystem** | `read_file` | Read file with dual SHA-256 + Blake2b hashes & line clamping. | 500k char safety limit |
| **Filesystem** | `write_file` | Write or overwrite file safely within sandbox. | Directory auto-creation |

---

## 🔒 Hardening & Cryptographic Certificate

- **Audit SHA-256:** `e4b28df1297156b83ebdfb5fe9792e2f9adffe1ae7afe01711a77ad9f11a67b9`
- **Audit Blake2b:** `2229075e9934f691e4f5922e5f8933474f4ab20b566bc8aa45fabfeb1d1b11ac...`
- **Daemon Supervision:** Running on background process `task-353` on port `9876`.
