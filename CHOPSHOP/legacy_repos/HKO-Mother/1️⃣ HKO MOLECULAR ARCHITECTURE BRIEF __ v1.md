## **1️⃣ HKO MOLECULAR ARCHITECTURE BRIEF // v1**

**Title:** HKO Metaverse – Molecular Architecture & Core DNA Standard  
 **Status:** Foundational. Non-optional for all future HKO modules.

### **1\. Purpose**

This brief defines:

* What “molecular” means in the context of HKO code.

* The **standard DNA** (HKO\_CORE) that all tools and engines must use.

* How engines and tools stack on top of shared molecules.

* The rules for composability, compatibility, and future scale.

This is the **architectural constitution** for the HKO Metaverse.  
 Any new code that ignores this is non-compliant by default.

---

### **2\. Design Principles**

1. **Molecular, not monolithic**  
    All logic is composed from small, well-defined molecules (modules), not giant scripts.

2. **One job per molecule**  
    Each component has **one clear responsibility**. Anything doing more must be split.

3. **Contracts over guts**  
    Components talk through **contracts** (input/output shapes), not through internal details.

4. **Core first, tools second**  
    Shared logic lives in **HKO\_CORE**, not inside individual tools.

5. **AI-agnostic by design**  
    No tool binds itself to Claude/GPT/Gemini directly. All providers sit behind `HKO_Agent`.

6. **Replaceable organs**  
    Any engine or tool can be swapped out as long as it respects contracts with HKO\_CORE.

7. **Scale and survival**  
    All design choices consider future growth, multi-tool interoperability, and token efficiency.

---

### **3\. Layered Structure of the Metaverse**

Top-down stack:

1. **HKO Hub / Sandbox (Command Center)**

   * Orchestrates tools, engines, and AI providers.

   * Exposes a unified UX for the user.

2. **Engines & Domain Modules**

   * File Engine, Duplicate Engine, Organizer Engine, Layout Engine, Outplacement Engine, ESL Engine, Utilities Engine, etc.

   * Encapsulate domain logic (e.g., organizing files, building layouts, generating CVs).

3. **HKO\_CORE (Super-Molecule Library)**

   * Shared DNA: config, logging, file ops, safety, routing, UI, AI, export, tokens, metrics.

   * No tool-specific logic allowed.

4. **Infrastructure & System Environment**

   * OS, file system, CLIs, API keys, local Python, etc.

All tools sit **above** HKO\_CORE.  
 HKO\_CORE sits on **nothing but the platform**.

---

### **4\. The HKO\_CORE Super Molecules**

**HKO\_CORE** is a flat, minimal, high-value library. Target structure:

`HKO_CORE/`  
    `__init__.py`

    `config.py        # HKO_Config`  
    `logger.py        # HKO_Logger`  
    `files.py         # HKO_Files`  
    `safety.py        # HKO_Safety`  
    `router.py        # HKO_Router`  
    `ui.py            # HKO_UI`  
    `agent.py         # HKO_Agent (LLM abstraction)`  
    `export.py        # HKO_Export`  
    `tokens.py        # HKO_Tokens`  
    `metrics.py       # HKO_Metrics`

    `models/          # Shared dataclasses / schemas (optional)`  
        `__init__.py`  
        `common.py`

Each file \= one “super molecule”.

---

#### **4.1 HKO\_Config (`config.py`)**

**Mandate:** Central authority for configuration and paths.

* Loads `.env`, JSON/YAML configs.

* Provides consistent path resolution (Desktop, HKO root, Logs, Temp, etc.).

* Exposes typed access to settings (no raw magic strings scattered across tools).

* Validates expected directories exist.

**Any tool needing settings or paths MUST go through HKO\_Config.**

---

#### **4.2 HKO\_Logger (`logger.py`)**

**Mandate:** Single logging standard for all HKO tools.

* Timestamps, module name, severity levels.

* Console \+ file logging with consistent format.

* Helpers for error logging and exceptions.

All engines/tools use `get_logger("Tool.Component")` style access.

---

#### **4.3 HKO\_Files (`files.py`)**

**Mandate:** File system DNA for the Metaverse.

* Scans folders, filters files, reads/writes files.

* Extracts metadata (size, dates, hashes).

* Abstracts OS quirks into one place.

No tool directly manipulates paths or low-level file ops outside HKO\_Files.

---

#### **4.4 HKO\_Safety (`safety.py`)**

**Mandate:** Guardrails and safe execution wrappers.

* Validates read/write permissions.

* Provides “dry run” wrappers for destructive actions.

* Wraps risky operations with controlled logging and error capture.

Destructive operations (delete, move, rename) must go through Safety.

---

#### **4.5 HKO\_Router (`router.py`)**

**Mandate:** Generic task-dispatch layer.

* Defines a standard `Task` object (name, payload, options).

* Registers handlers by name.

* Runs tasks and returns structured results (success, data, errors).

The Hub and Sandbox rely on this for orchestrating engines and tools.

---

#### **4.6 HKO\_UI (`ui.py`)**

**Mandate:** Minimal, consistent interaction layer.

* Text prompts, yes/no confirmations, list selectors, progress messages.

* CLI-first, but framework-neutral (can later be swapped for GUI).

All CLI interactions go through HKO\_UI for consistent UX.

---

#### **4.7 HKO\_Agent (`agent.py`)**

**Mandate:** AI abstraction layer.

* Wraps calls to Claude, GPT, Gemini, etc.

* Handles provider choice, retries, and error mapping.

* Integrates with HKO\_Tokens for usage tracking \+ tier selection.

Engines **never** call providers directly. They only know HKO\_Agent.

---

#### **4.8 HKO\_Export (`export.py`)**

**Mandate:** Standard output/export behavior.

* Writes outputs in standard formats (text, markdown, JSON, HTML; later PDF, etc.).

* Enforces consistent naming conventions (timestamps, slugs).

* Ensures all tools store exports in discoverable folder structures.

LayoutLab, Outplacement, ESL all use this for final artifacts.

---

#### **4.9 HKO\_Tokens (`tokens.py`)**

**Mandate:** Token accounting and tier decision helper.

* Tracks token usage per provider and per tool.

* Supports daily/monthly budgeting.

* Offers helper to choose an appropriate tier/model for task type.

HKO\_Agent calls into this to select providers and log costs.

---

#### **4.10 HKO\_Metrics (`metrics.py`)**

**Mandate:** Lightweight telemetry.

* Records counts (runs per task, errors).

* Times durations of key operations.

* Exposes snapshots for debugging and performance tuning.

The Hub and Sandbox use this for “health dashboard” and debugging.

---

### **5\. Engines & Tools on Top of HKO\_CORE**

Engines (Grunt, LayoutLab, Outplacement, ESL, Utilities) are built like this:

* They **import** from HKO\_CORE only (no cross-tool hidden dependencies).

* They define domain-specific logic (organizing files, generating CVs, etc.).

* They expose clean, testable functions or classes the Hub can call via HKO\_Router.

Example: Grunt’s Organizer Engine might rely on:

* `HKO_Files` for scanning/moving.

* `HKO_Safety` for guarded actions.

* `HKO_Config` for schema selection.

* `HKO_Logger` for logs.

* `HKO_UI` for user options (like dry-run vs live).

---

### **6\. Compatibility & Contracts**

Two modules are considered compatible if:

* Input/output shapes match (e.g. “list of file paths”, “dict of hashes”, “structured CV data”).

* They only interact via HKO\_CORE or documented contracts.

* They do not reach into each other’s internals or private data.

Any new module must answer:

1. Which HKO\_CORE molecules does it use?

2. What is its contract: input, output, failure behavior?

3. Can it be replaced without changing callers, as long as the contract remains?

If the answer to 3 is “no”, design must be revisited.

---

## **2️⃣ GITHUB → SANDBOX → HUB AUTOMATION FLOW // v1**

Now: how this becomes a **living system** with GitHub \+ CLIs (Claude, Gemini, OpenAI, etc.).

Goal:

* GitHub hosts the **source of truth**.

* Sandbox is your **local dev \+ AI playground**.

* Hub is your **running command center**.

* CLIs bridge AIs ↔ local repo ↔ GitHub.

### **1\. Repositories and Local Layout**

**Recommended structure:**

`GitHub`  
`└── HKO_Metaverse/                 # single mono-repo (v1)`  
    `├── HKO_CORE/                  # shared DNA`  
    `├── ENGINES/`  
    `│   ├── grunt_engine/`  
    `│   ├── layout_engine/`  
    `│   ├── outplacement_engine/`  
    `│   ├── esl_engine/`  
    `│   └── utilities_engine/`  
    `├── TOOLS/`  
    `│   ├── grunt_app/`  
    `│   ├── layoutlab_app/`  
    `│   ├── outplacement_app/`  
    `│   └── esl_app/`  
    `├── HUB/`  
    `│   └── hko_hub/`  
    `└── docs/`  
        `└── architecture/`

On your machine, the **Sandbox** is simply the local clone:

`C:\Users\harmk\Desktop\HKO_SANDBOX\HKO_Metaverse\`

The **Hub app** runs from `HUB/hko_hub/`.

---

### **2\. Branch \+ Workflow Strategy**

Minimal but sane:

* `main`

  * Stable. Only working, validated code.

* `dev`

  * Integration and active work. AI-generated changes land here first.

* `feature/*`

  * For specific experiments or modules (`feature/grunt-dna-refactor`, etc.).

AIs primarily work against `dev` or a `feature/*` branch.  
 You promote to `main` when you’re happy.

---

### **3\. CLIs and Their Roles**

You mentioned CLI-style integrations that can hit:

* GitHub (via local repo operations and/or their tooling)

* Local files

* APIs

The high-level roles:

* **Claude CLI**

  * Refactor modules, generate code, run local analysis on repo.

* **Gemini CLI**

  * Broad pattern analysis, doc generation, cross-file refactoring.

* **OpenAI / other CLI**

  * Targeted utilities, code completions, tests.

All of them operate on **the same local repo** in the Sandbox.

---

### **4\. Core Flow: GitHub ↔ Sandbox ↔ Hub**

Think in 3 loops:

#### **4.1. Sync Loop (GitHub ↔ Sandbox)**

1. Pull latest from GitHub into Sandbox:

   * `git checkout dev`

   * `git pull origin dev`

2. AIs (via CLIs) operate on this repo locally (not on GitHub directly).

3. Once happy, you commit and push:

   * `git add .`

   * `git commit -m "Refactor: [module]"`

   * `git push origin dev`

4. Human review / merge to `main` when ready.

---

#### **4.2. Build & Run Loop (Sandbox → Hub)**

1. Hub is just a Python app (for now) in `HUB/hko_hub/` that imports:

   * `HKO_CORE`

   * relevant engines in `ENGINES/`

   * tools in `TOOLS/`

2. After code changes, you restart the Hub app (or have it reload modules).

3. Hub exposes:

   * CLI interface (first version)

   * Later: GUI or tray icon

4. When the Hub receives a request (e.g. “Organize Desktop”):

   * It creates an `HKOTask`.

   * It uses `HKO_Router` to dispatch to the relevant Engine/Tool.

   * Engines rely on `HKO_CORE` molecules underneath.

---

#### **4.3. AI Automation Loop (CLIs → Repo → Hub)**

The idea:

1. You or the Hub creates a **task for an AI**:  
    “Refactor `HKO_CORE/files.py` to add hashing utilities and better safety wrappers.”

2. You invoke a CLI (Claude/Gemini/OpenAI) with:

   * Working directory set to `HKO_SANDBOX\HKO_Metaverse\`

   * File(s) to edit or glob patterns

   * System prompt referencing the **Molecular Architecture Brief** (this doc).

3. CLI edits files locally in the Sandbox:

   * The AI updates e.g. `HKO_CORE/files.py` and `ENGINES/grunt_engine/`.

4. You run local tests / quick smoke checks via:

   * `python -m HUB.hko_hub` in dev mode

   * Or a `scripts/run_checks.py` that imports modules and does basic validation.

5. If things are green, you `git diff`, `git commit`, `git push`.

6. Hub (optionally) can later have a **“self-update” command** to pull from `dev` or `main`.

---

### **5\. Concrete Flow: From Idea → AI → GitHub → Hub**

**Use case: Improve Grunt’s file-organizer DNA.**

1. You define the ask in human language:

   * “Create a new `HKO_CORE/files.py` method for scanning with filters \+ hash support, and update Grunt’s Organizer Engine to use it. No hardcoded paths. Log everything via HKO\_Logger.”

2. You run (example, conceptual):

   * Claude CLI:

     * Working dir: `HKO_SANDBOX\HKO_Metaverse\`

     * Context: `HKO_Molecular_Architecture_Brief.md` \+ `HKO_CORE/files.py` \+ `ENGINES/grunt_engine/*`

   * Prompt: your ask.

3. Claude edits code locally.

4. You in Sandbox:

   * `git status` → verify changed files.

   * `python -m HUB.hko_hub --dev` → run Hub, test Grunt function from Hub UI/CLI.

5. If broken → fix or re-prompt AI.  
    If OK → `git add`, `commit`, `push` to `dev`.

6. Once stable, merge `dev` → `main`.

7. Hub, if configured, can have an “Update from main” command to pull, restart, and load new modules.

---

### **6\. Automation Hooks (Later Phases)**

You can later add:

* **Script: `scripts/ai_task.py`**  
   Wraps CLI calls so Hub can say:  
   “Call Claude to refactor X according to Brief Y.”

* **Script: `scripts/self_update.py`**

  * `git fetch`

  * `git pull`

  * run tests

  * restart Hub

* **Token Monitoring** via HKO\_Tokens:

  * All AI-related flows report usage centrally.

  * Hub can block high-cost tasks if budget exceeded.

---

### **7\. Safety & Governance**

* All AI code changes go through **Sandbox first**, never directly to `main`.

* Use `dev` / `feature/*` for experimental AI work.

* Keep this Molecular Brief in `docs/architecture/` and feed it consistently as context to all CLIs so the architecture doesn’t drift.

---

Done.  
 You now have:

* A **Molecular Architecture Brief** you can hand to any model as reference.

* A **GitHub → Sandbox → Hub flow** that defines how CLIs and APIs will loop code through your system.

Whenever you’re ready, we can turn this into:

* `HKO_Molecular_Architecture_Brief.md` and

* a `HKO_FLOW_GitHub_Sandbox_Hub.md`  
   that you can drop straight into the repo.

##### **You said:**

do both and give me claude desktop instruction to set up workflow

###### **ChatGPT said:**

Alright Harm — here’s everything in one clean, usable bundle:

1. **HKO\_Molecular\_Architecture\_Brief.md**

2. **HKO\_Flow\_GitHub\_Sandbox\_Hub.md**

3. **Claude Desktop: Full Setup \+ Workflow Instructions** (copy-paste ready)

All delivered **in-chat** as complete assets — no placeholders, no half files.

Let’s go.

---

# **✅ 1\. HKO\_Molecular\_Architecture\_Brief.md**

*(Copy/paste directly into your repo under `docs/architecture/`)*

`# HKO MOLECULAR ARCHITECTURE BRIEF`    
`### Version: 1.0`    
`### Status: Foundational – Mandatory for All HKO Modules`

`---`

`## 1. Purpose`

`This document defines the molecular architecture of the HKO Metaverse.`    
`It establishes:`

`- What “molecular code” means within HKO.`  
`- The shared DNA every module must build upon.`  
`- The structure of HKO_CORE (the super-molecule library).`  
`- How Engines and Tools are layered above the core.`  
`- The rules for composability, compatibility, and survival.`

`This brief is the architectural constitution.`    
`All new code must comply.`

`---`

`## 2. Architectural Principles`

`1. **Molecular, not monolithic**`    
   `Systems are composed from small, self-contained components.`

`2. **One responsibility per molecule**`    
   `A component that performs multiple unrelated jobs must be split.`

`3. **Contracts over internals**`    
   `Modules communicate through defined input/output shapes.`

`4. **Core-first design**`    
   ``Shared logic belongs in `HKO_CORE`, never inside tools.``

`5. **AI-agnostic integration**`    
   `Providers (Claude, GPT, Gemini, etc.) sit behind abstraction layers.`

`6. **Replaceable organs**`    
   `Any module can be swapped without breaking callers as long as contracts remain.`

`7. **Future-proofing**`    
   `Designs must anticipate growth, multi-tool interoperability, and token efficiency.`

`---`

`## 3. Layered Architecture of the HKO Metaverse`

HKO HUB / SANDBOX (Command Center)  
 │  
 ▼  
 ENGINES & DOMAIN MODULES  
 │  
 ▼  
 HKO\_CORE  
 │  
 ▼  
 System/Platform

`### Layer Roles`

`- **Hub / Sandbox**: User interface, orchestration, task dispatch.`    
`- **Engines**: Domain logic (Grunt, LayoutLab, Outplacement, ESL, Utilities).`    
`- **HKO_CORE**: Shared DNA — config, logs, file ops, safety, UI, AI abstraction, export, token tracking, metrics.`    
`- **System**: OS, local filesystem, CLIs, API keys, Python environment.`

`---`

`## 4. HKO_CORE Super-Molecule Library`

`### Directory Structure (Required)`

HKO\_CORE/  
 **init**.py

`config.py`  
`logger.py`  
`files.py`  
`safety.py`  
`router.py`  
`ui.py`  
`agent.py`  
`export.py`  
`tokens.py`  
`metrics.py`

`models/`  
    `__init__.py`  
    `common.py`

`Each file = a molecular unit.`

``### 4.1 HKO_Config (`config.py`)``

`**Mandate:** Source of truth for settings and filesystem locations.`

``- Loads `.env`, JSON, YAML.``  
`- Exposes typed access to configuration values.`  
`- Resolves Desktop, HKO root, Logs, Temp, Project folders.`  
`- Prevents hardcoded paths anywhere else.`

``### 4.2 HKO_Logger (`logger.py`)``

`**Mandate:** Standardized logging.`

`- Timestamped messages, severity levels, module names.`  
`- Writes to console + log files.`  
`- Unified formatting across all tools.`

``### 4.3 HKO_Files (`files.py`)``

`**Mandate:** All file/folder operations.`

`- Scan folders, filter files, recurse, pattern match.`  
`- Read/write files.`  
`- Extract metadata and compute hashes.`  
`- Operates as the filesystem backbone.`

``### 4.4 HKO_Safety (`safety.py`)``

`**Mandate:** Guardrails.`

`- Read/write validation.`  
``- `dry_run` mechanisms.``  
``- `guarded_action()` wrappers for risky operations.``

``### 4.5 HKO_Router (`router.py`)``

`**Mandate:** Generic task dispatch.`

`- Defines HKOTask → payload + options.`  
`- Registers handlers.`  
`- Executes and returns structured HKOTaskResult.`

``### 4.6 HKO_UI (`ui.py`)``

`**Mandate:** Consistent CLI interaction.`

`- Menus, prompts, confirmations, progress messages.`

``### 4.7 HKO_Agent (`agent.py`)``

`**Mandate:** AI abstraction.`

`- Wraps Claude, GPT, Gemini, OpenRouter.`  
`- Handles retries, provider selection, errors.`  
`- Integrates with HKO_Tokens.`

``### 4.8 HKO_Export (`export.py`)``

`**Mandate:** Standard output/export.`

`- Writes text, markdown, JSON, HTML.`  
`- Enforces folder structure and naming conventions.`

``### 4.9 HKO_Tokens (`tokens.py`)``

`**Mandate:** Token accounting.`

`- Tracks usage per provider and per tool.`  
`- Suggests the cheapest viable model for the task.`  
`- Logs to HKO_Logger.`

``### 4.10 HKO_Metrics (`metrics.py`)``

`**Mandate:** Lightweight telemetry.`

`- Track durations, counts, health snapshots.`  
`- Used by Hub diagnostics.`

`---`

`## 5. Engines & Tools`

`Engines (e.g., File Engine, Duplicate Engine, Layout Engine, Outplacement Engine, ESL Engine) must:`

`- Depend only on HKO_CORE, never on each other’s internals.`  
`- Expose clean, documented input/output contracts.`  
`- Be replaceable without breaking Hub or Tools.`

`Tools (Grunt, LayoutLab, Outplacement, ESL) are thin wrappers that:`

`- Import Engines + HKO_CORE.`    
`- Provide user flows.`    
`- Never duplicate DNA logic.`

`---`

`## 6. Compatibility Contracts`

`Two modules are compatible when:`

`1. Input/output shapes match.`    
`2. They only call HKO_CORE and stable APIs.`    
`3. They do not reach into each other's guts.`    
`4. They are replaceable with zero upstream breakage.`

`---`

`## 7. Compliance Rules`

`- No hardcoded paths.`    
`- No direct provider calls (Claude/GPT/Gemini) outside HKO_Agent.`    
`- No mixing UI with logic.`    
`- No “god functions” or multi-responsibility modules.`    
`- Engines may extend, but never bypass, HKO_CORE.`    
`- All exports use HKO_Export.`    
`- All actions are logged through HKO_Logger.`    
`- All dangerous operations must go through HKO_Safety.`    
`- All AI tasks must reflect token limits via HKO_Tokens.`

`---`

`## 8. Future-Proofing`

`HKO_CORE evolves slowly, intentionally.`    
`Engines and Tools evolve rapidly on top of it.`

`This architecture ensures:`

`- Stability`    
`- Replaceability`    
`- Rapid development`    
`- Multi-AI compatibility`    
`- Long-term maintainability`  

---

# **✅ 2\. HKO\_Flow\_GitHub\_Sandbox\_Hub.md**

*(Place in `docs/architecture/` too)*

`# HKO FLOW: GITHUB → SANDBOX → HUB`    
`### Version: 1.0`    
`### Status: Operational Standard`

`---`

`## 1. Purpose`

`This document defines the system flow for:`

`- GitHub (source of truth)`  
`- Sandbox (local AI development)`  
`- Hub (runtime orchestrator)`  
`- AI CLIs (Claude, Gemini, OpenAI)`

`It ensures that:`  
`- Code flows safely from AIs → Sandbox → GitHub → Hub.`  
`- No AI commits directly to production branches.`  
`- The Metaverse evolves predictably.`

`---`

`## 2. Repository Layout (Mono-repo)`

HKO\_Metaverse/  
 HKO\_CORE/  
 ENGINES/  
 grunt\_engine/  
 layout\_engine/  
 outplacement\_engine/  
 esl\_engine/  
 utilities\_engine/  
 TOOLS/  
 grunt\_app/  
 layoutlab\_app/  
 outplacement\_app/  
 esl\_app/  
 HUB/  
 hko\_hub/  
 docs/  
 architecture/

`---`

`## 3. Branch Strategy`

``- `main` → stable, production-ready code.``  
``- `dev` → active development, AI edits land here.``  
``- `feature/*` → isolated tasks for significant changes.``

``AIs always target `dev` or `feature/*`.``

`---`

`## 4. Sandbox`

`Local clone of the repo:`

C:\\Users\\harmk\\Desktop\\HKO\_SANDBOX\\HKO\_Metaverse\\

`AIs operate **only** inside this directory.`

`Sandbox also contains:`  
`- AI context notes`    
`- Logs`    
`- Local tests`    
`- Temporary branches`  

`---`

`## 5. Edit Flow (AI → Sandbox)`

`Example cycle:`

`1. You define the change:`    
   ``“Refactor `HKO_CORE/files.py` to use safer path checks.”``

`2. You run CLI (Claude/Gemini/OpenAI) in Sandbox folder.`

`3. AI applies edits locally.`

`4. You run Hub in dev mode:`  

python \-m HUB.hko\_hub \--dev

`5. If good:`  

git add .  
 git commit \-m "Refactor files.py for safety"  
 git push origin dev

``6. You merge `dev` → `main` when stable.``

`---`

`## 6. Runtime Flow (Sandbox → Hub)`

`Hub loads code directly from:`

HUB/hko\_hub/  
 ENGINES/  
 HKO\_CORE/

`Hub tasks use:`

`- HKORouter`    
`- Engines`    
`- HKO_CORE molecules`    
`- HKO_Agent for AI delegation`    
`- HKO_Tokens for model selection`  

`---`

`## 7. Automation (Later)`

`Scripts:`

``- `scripts/ai_task.py` – Standardized AI prompts``    
``- `scripts/self_update.py` – Pull latest code & restart Hub``    
``- `scripts/run_checks.py` – Sanity tests (imports, signatures, dry-run ops)``  

`---`

`## 8. Token-Aware AI Routing`

`HKO_Agent + HKO_Tokens ensure:`

`- Cheap models for simple tasks`    
`- Claude/GPT premium only for architecture or deep analysis`    
`- Token usage logging for each task`  

`---`

`## 9. Safety`

``- No AI pushes directly to `main`.``    
``- Use `dev` or `feature/*` branches.``    
`- All commits reviewed before promotion.`  

---

# **✅ 3\. CLAUDE DESKTOP WORKFLOW SETUP (FULL INSTRUCTIONS)**

Copy/paste this straight into Claude Desktop.

`You are now being integrated into the HKO Metaverse development workflow.`

`Your environment is:`  
`C:\Users\harmk\Desktop\HKO_SANDBOX\HKO_Metaverse\`

`Follow these rules:`

`1. Never write or modify code anywhere outside this directory.`  
`2. Always work inside the active branch:`  
   `- Usually "dev"`  
   `- Or a "feature/*" branch when specified`  
`3. All code must comply with the HKO Molecular Architecture Brief located at:`  
   `docs/architecture/HKO_Molecular_Architecture_Brief.md`  
`4. You must NEVER write monolithic scripts. Use HKO_CORE for:`  
   `- config`  
   `- logging`  
   `- file operations`  
   `- safety`  
   `- routing`  
   `- ui`  
   `- ai provider abstraction`  
   `- export`  
   `- token accounting`  
   `- metrics`  
`5. When rewriting or creating modules, you MUST:`  
   `- Identify which HKO_CORE molecules they depend on`  
   `- Define clear input/output contracts`  
   `- Ensure replaceability and modular compatibility`  
`6. All provider-specific logic (Claude, GPT, Gemini, etc.) MUST go through HKO_Agent.`  
`7. After making changes:`  
   `- Provide a summary`    
   `- Provide a diff-style explanation`    
   `- DO NOT commit automatically`    
   `- Wait for user confirmation`  
`8. When asked to refactor, rewrite from scratch unless user explicitly asks for a patch.`  
`9. Validate imports and run local style checks before generating code.`  
`10. Never generate hardcoded paths. Always use HKO_Config for locations.`  
`11. Always respect token constraints and recommend cheaper models when possible.`  
`12. You are allowed to read multiple files in the repo at once to understand context.`  
`13. You can propose structural improvements but NEVER execute them without instructions.`  
`14. If working on a new module:`  
   `- Start with a skeleton following molecular design`  
   `- Scaffold API signatures`  
   `- Add docstrings explaining contracts`  
`15. When asked for a full module, deliver consolidated code blocks in one piece.`

`Your primary responsibilities:`  
`- Generate, refactor, and correct code inside the repo`  
`- Maintain strict compliance with the Molecular Architecture`  
`- Ensure module-level replaceability`  
`- Strengthen the HKO Metaverse with robust, standardised code blocks`

`Now acknowledge the brief and wait for the first task.`

---

You’re set.

Want me to also prepare:

* the **Gemini CLI** instructions

* the **OpenAI CLI** instructions

* or convert the briefs into `.md` files with headers, table of contents, etc.?

##### **You said:**

all 3

###### **ChatGPT said:**

Alright Harm — here are **all three** instruction bundles, ready to drop into Claude Desktop, Gemini CLI, and OpenAI CLI.  
 They match the HKO Molecular Architecture and keep everything tight and consistent across all AIs.

I’m giving you **copy-paste blocks**, no filler.

---

# **✅ 1\. CLAUDE DESKTOP — FULL WORKFLOW INTEGRATION INSTRUCTIONS**

*(Paste directly into Claude Desktop as its long-term system brief)*

`You are now operating as a core development agent inside the HKO Metaverse.`

`Your working directory:`  
`C:\Users\harmk\Desktop\HKO_SANDBOX\HKO_Metaverse\`

`Your rules:`

`1. Work ONLY inside this repo. Never modify files outside it.`

`2. You must always follow:`  
   `docs/architecture/HKO_Molecular_Architecture_Brief.md`  
   `docs/architecture/HKO_Flow_GitHub_Sandbox_Hub.md`

`3. All code must follow the molecular architecture:`  
   `- One responsibility per module`  
   `- Clean input/output contracts`  
   `- Zero cross-contamination between tools`  
   `- Stable replaceable modules`  
   `- All shared logic goes in HKO_CORE`  
   `- No hardcoded paths (always use HKO_Config)`  
   `- No monolithic or tangled structures`

`4. You are NOT allowed to call providers directly (Claude/GPT/Gemini).`  
   `All provider logic MUST go through HKO_Agent.`

`5. Before you generate or modify code:`  
   `- Inspect related modules`  
   `- Identify core molecules required`  
   `- Validate contract shapes`  
   `- Check what engines/tools will consume it`

`6. When producing code:`  
   `- Deliver full consolidated modules (no partial patches)`  
   `- Use idiomatic Python, typed where possible`  
   `- Include docstrings explaining contracts`  
   `- Ensure imports are correct and resolvable`  
   `- Use shared utilities: HKO_Files, HKO_Safety, HKO_Logger, etc.`

`7. After producing code:`  
   `- Provide a clear diff-style summary of changes`  
   `- Provide a validation checklist (imports, paths, flow)`  
   `- Wait for user confirmation before committing`

`8. You may propose improvements but must NEVER implement structural changes without explicit instruction.`

`9. You will always prioritise:`  
   `- Stability`  
   `- Token efficiency`  
   `- Replaceability`  
   `- Modularity`  
   `- Clarity`  
   `- Future HKO compatibility`

`Your mission:`  
`- Generate, improve, and refactor modules in alignment with HKO Molecular Architecture.`  
`- Maintain structural integrity and long-term survival of the HKO Metaverse.`  
`- Serve as a reliable, rule-bound engineering partner.`

`Acknowledge and wait for the first task.`

---

# **✅ 2\. GEMINI CLI — FULL WORKFLOW INSTRUCTIONS**

*(Paste this into your Gemini note or first message before coding tasks)*

`You are operating as a structural engineering agent for the HKO Metaverse ecosystem.`

`Your repo to operate on:`  
`C:\Users\harmk\Desktop\HKO_SANDBOX\HKO_Metaverse\`

`Your architectural constitution:`  
`- docs/architecture/HKO_Molecular_Architecture_Brief.md`  
`- docs/architecture/HKO_Flow_GitHub_Sandbox_Hub.md`

`MANDATORY RULES:`

`1. Follow the HKO molecular architecture strictly:`  
   `- Single responsibility modules`  
   `- Shared DNA in HKO_CORE only`  
   `- Engine logic above the core`  
   `- Tools are thin wrappers`  
   `- All AI calls must pass through HKO_Agent`  
   `- No filesystem access outside HKO_Files`  
   `- No unsafe operations outside HKO_Safety`  
   `- Consistent logs through HKO_Logger`  
   `- No hardcoded directories, ever`

`2. When editing or creating code:`  
   `- Inspect related files first`  
   `- Identify required HKO_CORE molecules`  
   `- Validate contract shapes`  
   `- Ensure module is replaceable`  
   `- Avoid circular dependencies`  
   `- Produce consolidated, ready-to-run modules`

`3. All exports must use HKO_Export.`  
`4. All token-related logic must use HKO_Tokens.`  
`5. All user interaction must use HKO_UI.`  
`6. All routing must use HKO_Router.`

`7. When delivering code:`  
   `- Provide full module code (never fragments)`  
   `- Provide an explanation of architecture decisions`  
   `- Provide test scenarios for validation`  
   `- Provide safety considerations`

``8. NEVER push directly to `main`. Work in:``  
   `` - `dev` ``  
   ``- or `feature/*` branches``

`9. Honor token-awareness:`  
   `- Prefer analysis over brute force`  
   `- Propose low-cost operations when appropriate`

`Your primary responsibilities:`  
`- Perform deeper structural analysis`  
`- Generate multi-file refactors`  
`- Validate entire architectures`  
`- Align tools and engines to the Molecular Brief`  
`- Strengthen the system’s long-term consistency`

`Await the first instruction.`

---

# **✅ 3\. OPENAI CLI / GPT DESKTOP — FULL WORKFLOW INSTRUCTIONS**

*(Use this as the long prompt before asking GPT to work on repo code)*

`You are now working as a modular systems engineer inside the HKO Metaverse.`

`Your active repo:`  
`C:\Users\harmk\Desktop\HKO_SANDBOX\HKO_Metaverse\`

`Reference standards:`  
`- docs/architecture/HKO_Molecular_Architecture_Brief.md`  
`- docs/architecture/HKO_Flow_GitHub_Sandbox_Hub.md`

`Your constraints:`

`1. ALL code must follow the HKO molecular architecture:`  
   `- Small, replaceable modules`  
   `- Clear input/output contracts`  
   `- Zero hidden coupling`  
   `- Use of HKO_CORE for shared DNA`  
   `- No hardcoded filesystem paths`  
   `- No direct LLM calls (use HKO_Agent)`  
   `- No logic outside appropriate engines`  
   `- Consistent logging via HKO_Logger`

`2. Before producing any code:`  
   `- Inspect all relevant files`  
   `- Identify needed core molecules`  
   `- Define correct boundaries`  
   `- Ensure compatibility with Hub + Engines`

`3. When generating code:`  
   `- Deliver ONE consolidated file per module`  
   `- Include complete, executable code`  
   `- Include docstrings for all classes/functions`  
   `- Ensure correct imports and module paths`  
   `- Maintain atomic, independent modules`

`4. When refactoring:`  
   `- Rewrite entire module if necessary`  
   `- Remove duplication`  
   `- Enforce clear boundaries`  
   `- Develop against contracts, not assumptions`

`5. Always produce:`  
   `- Change summary`  
   `- Architectural rationale`  
   `- Safety & sanity checks`  
   `- Suggested test cases`

`6. Operate only within:`  
   `C:\Users\harmk\Desktop\HKO_SANDBOX\HKO_Metaverse\`  
   `Never modify or reference external files.`

``7. Use `HKO_Config` for:``  
   `- Paths`  
   `- User directories`  
   `- Configuration loading`

``8. Use `HKO_Files` for:``  
   `- Scanning, reading, writing, moving, metadata`

``9. Use `HKO_Safety` for:``  
   `- Any destructive or high-risk action`

`10. All exports must use:`  
   `- HKO_Export (text, MD, JSON, HTML)`

`11. All token logic must use:`  
   `- HKO_Tokens`

`12. All UI flow must go through:`  
   `- HKO_UI`

`Your mission:`  
`Maintain absolute architectural alignment, modularity, token-efficiency, and integrity of the HKO Metaverse codebase.`

`Confirm readiness and wait for next task.`

---

# **🎯 Want the final touch?**

I can also generate:

* **`.md` versions with TOCs and headers**

* **GitHub `README` templates for each component**

* **A combined “ALL AIs” integration guide**

* **A bootstrap script for your repo to initialize HKO\_CORE scaffolding**

* **A Claude Desktop snippet that automatically loads the briefs into memory every session**

Just say the word.

