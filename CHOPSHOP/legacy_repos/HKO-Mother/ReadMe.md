# HKO Grunt v11 — Desktop Maintenance Agent (Threaded Edition)

HKO Grunt v11 is the core desktop maintenance and intelligence agent of the **HKO Metaverse**.  
It acts as a real-time assistant that keeps your workstation clean, structured, and ready for high-level work across all HKO modules.

The v11 edition is fully threaded, EXE-safe, and engineered for large environments with thousands of files.

---

# 🔥 Primary Functions of HKO Grunt

### 1. Organize & Maintain the HKO Folder Schema

Grunt enforces and works against a **standardized desktop working schema**, keeping everything in the right “bucket” so other HKO tools (LayoutLab, Outplacement engine, ESL modules, etc.) can plug in cleanly.

### 2. Extract Useful Code From Documents, Dumps & Logs

Grunt detects and extracts code or code-like content from:

- `.py`, `.js`, `.json`, `.html`, `.css`, `.md`, `.txt`, etc.  
- data dumps, logs, exports, or raw project folders

Extracted assets are copied into a central code library for later reuse and AI processing.

### 3. Maintain the Desktop Filing System

Grunt helps prevent entropy on your desktop by:

- scanning and classifying files  
- supporting schema-based organization  
- flagging duplicates  
- keeping working folders aligned with the HKO structure

### 4. Interact With LLMs on HKO Projects

Grunt prepares cleaner, structured input for LLMs (Claude, GPT, Gemini, etc.) by:

- extracting relevant code and context  
- logging origins and structure  
- keeping everything inside the HKO_METAVERSE hierarchy so it’s easy to hand off to AI tools and orchestration scripts.

---

# 🧱 Folder Schema (Working Model)

Grunt assumes (and/or helps reinforce) the following **desktop-level working schema**:

```text
C:\Users\<USER>\Desktop\
│
├── ESL\
├── OUTPLACEMENT\
├── COACHING\
├── PERSONAL\
├── HKO\
├── GOLDMINE\
└── HKO_METAVERSE\

DESKTOP/
│
├── ESL/
│   ├── Clients/{ClientName}/(Sessions/Materials…)
│   ├── General_Docs/
│   └── Resources/
│
├── OUTPLACEMENT/
│   ├── Clients/{ClientName}/(CV/LinkedIn…)
│   ├── General_Docs/
│   └── Resources/
│
├── COACHING/
│   ├── Clients/
│   ├── Templates/
│   └── Resources/
│
├── PERSONAL/
│   ├── Docs/
│   ├── Ideas/
│   └── Admin/
│
├── HKO/
│   ├── Brand/
│   ├── Pitch/
│   ├── Assets/
│   ├── Strategy/
│   └── General_Docs/
│
└── HKO_METAVERSE/
    ├── CORE_ENGINE/
    ├── MODULES/
    ├── METAVERSE_LIBRARY/
    └── _README.md

HKO_METAVERSE\
│
├── LOGS\
│   └── grunt_log.txt         # Grunt’s activity + debug log
│
└── METAVERSE_LIBRARY\
    ├── Code_Repository\      # Extracted code & reusable snippets
    └── grunt_config.json     # Persistent config (quarantine, paths, etc.)
