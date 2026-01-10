

# **🧠 HKO USER INTERFACE — SYSTEM-WIDE UX SPEC**

**Version:** Final Draft  
 **Purpose:** Define the full UI behavior, interaction rules, layout logic, and visual identity for all HKO tools (HubbaHubba, Grunt, Sandbox, LayoutLab, ESL, Outplacement, Coaching, Pottery, Metaverse utilities).

This governs *every screen, dashboard, module, and card* in the entire system.

---

# **1\. UX PHILOSOPHY**

### **1.1. One Brain, Many Tools**

Every HKO product must feel like a **single operating system**.  
 Different tools, same cognition.

**Shared across ALL tools:**

* gunmetal palette

* card grid

* rounded 2xl corners

* inner shadows

* orange status highlights

* operation logs

* detail panels

* dry-run/preview-before-run pattern

* hover-lift interactions

* three-tier hierarchy (primary → secondary → tertiary)

---

### **1.2. Card-Based, Modular, LEGO UI**

Everything is a card.  
 If it exists, it exists as a block.

**Cards \= Super Molecules**:  
 Clients, tools, sessions, lessons, folders, buckets, jobs, logs, actions.

**Card states:**

* Rest

* Hover (slight lift \+ stronger border)

* Active (highlighted ring)

* Disabled (low contrast)

**Card capabilities:**

* Collapsible

* Rearrangeable

* Pinned

* Reused across modules

* Passed between buckets

**Card \= atom of the system.**

---

### **1.3. Always-Visible Status & Consequences**

HKO ≠ invisible automation.  
 If something happens, user sees it.

Every tool must expose:

* status pills

* progress

* success/failure toasts

* operation log messages

* before/after summaries

Example:  
 “455 moved • 27 dupes • 0 failed • 2 skipped”

---

### **1.4. One-Click With an Escape Hatch**

One-click ≠ blind execution.

Pattern for all “dangerous / heavy” actions:

1. Summary screen (“This is what will happen”)

2. Confirm → Execute

3. Result recap \+ interactive links (e.g. “Open DUPES folder”)

This applies to:

* Grunt sorting

* LayoutLab export

* Sandbox transformations

* Outplacement CV rewrites

* ESL lesson generation

* Pottery membership batch actions

* Metaverse cleaning

---

### **1.5. Gamified, But Professional**

Tone gradient across buckets:

**More playful:**  
 ESL, Coaching, Equine, Pottery  
 → fun progress bars • streaks • badges

**More serious:**  
 Outplacement, HKO Metaverse  
 → structured metrics • clean analytics • data-first cards

**But UI rules stay the same.**

---

### **1.6. Strong Visual Hierarchy**

Tri-tier structure:

**Primary:**  
 Current focus (selected card, opened module)

**Secondary:**  
 Panels with key metrics, preview actions, quick buttons

**Tertiary:**  
 Log feeds, system messages, token usage, debug info

Everything slots into one of these three visual layers.

---

# **2\. SYSTEM SURFACES**

These are the only allowed surface types across the entire ecosystem.

---

## **2.1. HKO Hub (Control Centre)**

This is the OS home screen.

**Sections:**

* Top nav (title \+ context)

* Bucket selector (ESL / Outplacement / Coaching / Personal / HKO / Metaverse)

* Main grid of cards (tools per bucket)

* Right rail (context panel)

* Bottom log (global operation feed)

**Behavior:**

* Switching buckets switches the card grid

* Selecting a card loads details in the right rail

* Every button that does something logs to the operation feed

This is the “brainstem” of HKO.

---

## **2.2. Module Screens (Grunt / LayoutLab / ESL / etc.)**

Every module uses the **same interior layout**:

┌──────── main grid ────────┐ ┌──────── context rail ───────┐  
│ cards / lists / tools      │ │ actions / logs / details    │  
└────────────────────────────┘ └─────────────────────────────┘

**Consistency requirement:**  
 No module gets its own exotic UI.  
 All tools conform to the system.

---

## **2.3. Operation Panel (Right Rail)**

Universal design:

* Appears in every module

* Shows detail of selected item

* Contains actions grouped by safe → dangerous

* Contains dry-run toggles

* Contains micro-previews

**Right rail is the system’s “action brain.”**

---

## **2.4. Operation Log (Bottom)**

Shared log for everything.

**Format:**

\[12:05:02\] \[MODULE\] Summary text with result

**Color code:**

* grey \= info

* green \= success

* amber \= warning

* red \= error

* blue \= AI action

Scrolling, persistent, global.

---

# **3\. CORE UI COMPONENTS**

These are the LEGO bricks.

---

### **3.1. HKO Card**

The universal tile.

**Contains:**

* Title

* Subtitle

* Status pill

* Metric line

* Micro CTA

**Interaction:**

* Hover lifts

* Active gets a highlighted ring

* Press \= soft compression

---

### **3.2. Status Pills**

Small rounded indicators with color semantics.

| Meaning | Color |
| ----- | ----- |
| Ready | Emerald |
| In Progress | Sky |
| Warning | Amber |
| Error | Red |
| Scheduled | Violet |

Always uppercased.

---

### **3.3. Mode Toggle**

Every system with risk uses:

\[ Dry Run \]  \[ Live \]

Live always has a confirm micro-step.

---

### **3.4. Schema Chips**

Used by Grunt, Sandbox, LayoutLab.

Small, rounded, tappable filters.

Example:

\[ Bucket Schema \] \[ Filetype Schema \] \[ AI Prep Schema \]

---

# **4\. UX FLOWS**

---

## **Flow 1: Execute Grunt Run**

Hub → METAVERSE → Grunt → Select source/dest → Preview → Dry-run → Live

Key rules:

* Summary must appear before running

* Both runs write to operation log

* Results card must include folder links

---

## **Flow 2: Jump Cross-Module**

Example: ESL → “See code in Metaverse”

Pattern:

* Selecting a CTA in one bucket automatically jumps the user

* Rail loads the same selected card, but from another bucket

* Keeps mental flow unified

---

## **Flow 3: Generate with AI**

Applies to: ESL, Outplacement, Pottery.

Pattern:

* Generators open in a **side panel**, NOT a new page

* User reviews output before accepting

* Acceptance logs action and updates the main card

---

# **5\. VISUAL IDENTITY**

---

### **Color Tokens**

* **Background primary:** `#1f1f1f`

* **Background secondary:** `#2b2b2b`

* **Card surface:** `#3a3a3a`

* **Accent:** `#f05a28`

* **Text primary:** `#f5f5f5`

* **Text secondary:** `#b3b3b3`

---

### **Shape Language**

* `border-radius: 1.25rem` (2xl)

* Subtle inner shadows

* Hover outer shadows

---

### **Typography**

* **Inter** for UI

* **Montserrat Black** for headings

* Tight tracking (`-0.02em`)

---

# **6\. EXAMPLE CODE (SYSTEM-WIDE UI PATTERNS)**

This block is the “UI DNA” for all HKO screens.

### **Base Layout (React \+ Tailwind)**

\<div className="min-h-screen bg-zinc-950 text-zinc-50 flex flex-col"\>  
  \<header className="px-6 py-4 border-b border-zinc-800"\>  
    \<h1 className="text-xl font-bold tracking-tight"\>HKO Hub // Control Centre\</h1\>  
  \</header\>

  \<nav className="px-4 py-2 border-b border-zinc-800 flex gap-2"\>  
    {/\* bucket chips \*/}  
  \</nav\>

  \<div className="flex flex-1 overflow-hidden"\>  
    \<main className="flex-1 overflow-auto p-4"\>  
      {/\* card grid \*/}  
    \</main\>

    \<aside className="w-80 border-l border-zinc-800 p-4 bg-zinc-900/50"\>  
      {/\* detail panel \*/}  
    \</aside\>  
  \</div\>

  \<footer className="border-t border-zinc-900 bg-zinc-950/90"\>  
    {/\* log \*/}  
  \</footer\>  
\</div\>

### **Card Pattern**

\<button className="rounded-2xl bg-zinc-900/60 border border-zinc-800 p-4 hover:border-zinc-600 hover:bg-zinc-900 transition shadow-sm hover:shadow-md"\>  
  \<div className="flex justify-between items-center"\>  
    \<h2 className="text-sm font-semibold"\>Card Title\</h2\>  
    \<span className="px-2 py-0.5 bg-emerald-600/20 text-emerald-300 text-\[10px\] rounded-full"\>  
      READY  
    \</span\>  
  \</div\>  
  \<p className="text-xs text-zinc-400"\>Subtitle\</p\>  
\</button\>

### **Operation Log**

\<section className="text-\[11px\] font-mono px-4 py-2 overflow-auto max-h-40 border-t border-zinc-800"\>  
  \<div\>\[12:01\] System initialized.\</div\>  
  \<div className="text-emerald-400"\>\[12:05\] SUCCESS: Grunt run completed.\</div\>  
\</section\>

---

# **7\. HOW TO APPLY THIS**

You now have:

* global UI laws

* global visual structure

* global interaction maps

* global card & log components

* system layout pattern

* example implementations

Everything you create next (screens, modules, apps, utilities) must use this exact UX template.

---

If you want, I can now generate a **ready-to-use design system package**:

### **✔ HKO UI Kit**

– Tailwind tokens  
 – Component library  
 – Status color map  
 – Motion library  
 – React wrappers  
 – Module router

Or I can deliver the **Figma blueprint** in code-ready format.

Just tell me.

