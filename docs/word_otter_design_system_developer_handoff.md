# WordOtter — Design System & Developer Handoff

> Complete package to hand to engineering so they can build WordOtter’s web app with the earthy-pastel otter aesthetic.

---

## What’s included in this document

1. Executive summary & scope
2. Brand identity (logo, mascot, tone)
3. Color system (swatches + usage rules)
4. Typography system
5. Key UI components (specs + variants)
6. Screen designs (list + behavior notes)
7. Micro-interactions & animation specs
8. Sound design notes
9. Accessibility checklist
10. Assets & export guidelines (naming, formats)
11. Handoff package (what to give devs)
12. Prototype & testing plan
13. Implementation notes & engineering recommendations
14. QA checklist
15. Next steps & timeline

---

# 1. Executive summary & scope

**Goal.** Deliver a delightful, whimsical, earthy-pastel vocabulary builder with a friendly otter mascot. The MVP covers: Landing/Home, Dictionary, Study/Flashcards, Daily Challenge, Profile/Achievements, Onboarding, and basic settings.

**Scope for handoff.** Complete design system, component library, pixel-perfect screen specs, animation & sound specs, and an exported assets pack (SVGs, PNGs, Lottie JSON where applicable) ready for a front-end implementation team.

---

# 2. Brand identity

**Name:** WordOtter (wordotter.com)

**Mascot:** Otter — full-body & head-only variants. Expression set: neutral, happy, proud, curious, confused, sleepy, celebratory, reading-glasses.

**Tone of voice (copy):** Warm, playful, slightly literary. Examples:
- Empty state: “This pond is still calm… add some words to make waves.”
- Success: “You’ve otter be proud!”
- Loading: “Fetching your next pearl of wisdom…”

**Logo usage:** primary horizontal logo (wordmark + otter head), icon-only circular badge for small sizes.

---

# 3. Color system (earthy pastels)

> Use tokens (CSS variables or design tokens) for all colors.

| Token name | Hex | Role |
|---|---:|---|
| `--otter-brown` | `#A47864` | Primary brand / mascot fur |
| `--river-teal` | `#7FB8A7` | Primary accent / CTA secondary |
| `--pebble-beige` | `#E7D9C4` | Page background / cards |
| `--reed-green` | `#A3B18A` | Accent, success states |
| `--sunset-coral` | `#E6A299` | Primary CTA / highlights |
| `--shell-white` | `#FDF8F4` | Main content background / surface |
| `--text-dark` | `#4A372E` | Headings / primary text |
| `--muted` | `#8A7D74` | Secondary text / placeholder |

**Usage rules**
- Backgrounds: `--shell-white` or `--pebble-beige` for larger areas.
- Primary CTA: `--sunset-coral` (button text in shell-white).
- Secondary CTA/Accents: `--river-teal` or `--reed-green`.
- Errors: use a warm reddish accent derived from sunset coral (provide dev a token `--error` = `#D96E5A`).
- Keep 3–4 colors present on any single screen to avoid visual clutter.

---

# 4. Typography

**Primary heading:** Serif/Display with friendly curves (e.g., "Merriweather" or "Playfair Display" family) — heavier weight for large headings.
**UI / Body:** Rounded sans (e.g., "Inter", "Nunito", or "Poppins") for readability.

**Hierarchy (tokens)**
- `h1` 48 / 56px — 700 (desktop)
- `h2` 32 / 40px — 600
- `h3` 24 / 32px — 600
- `body` 16px — 400
- `small` 14px — 400

**Line-height and spacing**
- Body line height: 1.45. Headings: 1.2–1.3.
- Use consistent 8pt spacing scale (8 / 16 / 24 / 32 / 40 etc.).

---

# 5. Key UI components

> Each component must include: states, spacing, color tokens, typography, iconography, and accessible labels.

### Primary Button (CTA)
- Variants: Primary (`--sunset-coral`), Secondary (`--river-teal` outline), Disabled (pebble beige, low contrast).
- Corner radius: 20px (pill)
- Padding: 12px 20px
- Shadow: subtle soft shadow (e.g., `0 2px 6px rgba(74,55,46,0.08)`)

### Search / Periscope Bar
- Shape: rounded rectangle with tiny notch/periscope accent icon on left.
- Placeholder copy: "Search words, e.g. 'serendipity'"
- Results: card list with part-of-speech, short defs, and tags (tone: stepping-stone chips).

### Flashcard
- Size: responsive center card (max-width 640px on desktop, full width mobile).
- Front: Word + part of speech + pronunciation button (speaker icon).
- Back: Definition, example sentence, synonyms (chips), add-to-list button.
- Flip animation: vertical axis 3D flip with slight wobble. Duration: 420ms.

### Progress Tracker (Swimming Otter)
- Bar: rounded pill track (height 12–16px), track color `--pebble-beige`, fill `--reed-green`.
- Indicator: otter head icon floating at progress percentage. Provide 3 sizes (mobile/tablet/desktop).

### Badges Grid
- Shape: circular shells with small label beneath.
- States: locked (muted), unlocked (full color with small sparkle).

### Toast / Notification
- Small speech-bubble card with otter peeking. Auto-dismiss 3.5s. Must be dismissible.

---

# 6. Screen designs (list + behavior notes)

**A. Landing / Home**
- Hero area with otter illustration, Word of the Day card, CTA buttons.
- Quick links to Study, Dictionary, Achievements.

**B. Dictionary Search & Word Detail**
- Search at top. Results list with pagination or infinite scroll.
- Word detail modal or page: word, pronunciation, senses, etymology (collapsed), synonyms, example sentences, add-to-study buttons.

**C. Study / Flashcard Mode**
- Centered flashcard, answer reveal, multiple-choice or typed input (configurable).
- Bottom bar: progress (otter), skip button, next button.

**D. Daily Challenge**
- 3–5 quick questions, one-word reveal reward (badge or shell). Animation on completion.

**E. Profile / Achievements**
- Streak display, progress history chart (sparse), badges gallery, settings link.

**F. Onboarding**
- Short 3-screen tour: mascot intro, how study works, permissions (notifications), choose default study list.

**G. Settings & Lists**
- Manage saved lists, import/export words (CSV), notification preferences, accessibility toggles (reduce motion).

---

# 7. Micro-interactions & animation specs

**General rules**
- Use easing: cubic-bezier(.22,.9,.28,1) for primary motions.
- Durations: small 150–220ms, medium 350–500ms, long 700–900ms.
- Reduce motion toggle: all non-essential motion must be disable-able.

**Key animations**
- Flashcard flip: 420ms 3D flip with subtle shadow. On reveal, otter nods.
- Correct answer: otter claps (1000ms) + water-splash particles (6–12 small circles).
- Incorrect: otter scratches head (500ms) + gentle shake of card (220ms).
- Progress fill: otter swims across track (600–900ms) when progress increments.
- Loaders: otter swims in loop carrying a scroll (SVG animation / Lottie). Keep ~2–3s loops.

**Animation assets**
- Provide Lottie JSON for loaders and milestone confetti.
- Provide GIF or PNG sprite fallback for older browsers.

---

# 8. Sound design notes

- Keep sounds minimal and optional in settings.
- Small splash on correct answers (short, soft), polite error chime (muted), soft page-turn when flipping a card.
- Provide both ON/OFF and volume slider in settings.
- Export audio as 44.1kHz mono .mp3 and .wav for fallback.

---

# 9. Accessibility

- Color contrast: ensure primary text vs background meets WCAG AA (4.5:1) where possible. For decorative text, OK to be lower but avoid for primary content.
- Keyboard navigable: all interactive elements focusable, visible focus states.
- ARIA labels: provide aria-labels for buttons (play pronunciation, flip card, add word).
- Screen reader copy: concise alt text for mascot states (e.g., "Otter smiling"), avoid redundant verbose descriptions.
- Reduce motion toggle for users who prefer no animation.

---

# 10. Assets & export guidelines

**File naming conventions**
- `otter-happy-v1.svg` / `otter-happy@2x.png`
- `icon-search.svg` / `btn-primary-filled.svg`
- `badge-shell-01.svg`

**Formats**
- Icons: SVG (optimized), plus 32/64 PNG fallbacks.
- Illustrations / Mascot: SVG for simple vector shapes; high-res PNG (2048px) for full scenes.
- Animations: Lottie JSON (preferred), MP4/GIF fallback for demos.
- Audio: `.wav` (master) + `.mp3` compressed.

**Export sizes**
- Mascot small: 48px, 72px, 128px (SVG recommended)
- Hero: 1200–1600px wide PNG for hero backgrounds.

**Deliver an `assets/` ZIP** with subfolders: `icons/`, `mascot/`, `illustrations/`, `animations/`, `audio/`, `figma-export/`.

---

# 11. Handoff package for devs (what to give)

1. Figma project (organized pages: Tokens, Components, Screens, Prototypes). Provide a Figma link and invite devs.
2. Exported assets ZIP (SVGs, PNGs, Lottie JSON, audio).
3. Style guide (this document plus a short 2–3 page PDF summary for quick reference).
4. Interaction spec sheet (timings, easings, triggers) as JSON or annotated Figma frames.
5. Accessibility notes & localization guide (how strings scale, right-to-left considerations).
6. API-ready copy file: CSV/JSON of Word of Day, word definitions, example sentences, pronunciations (URLs), tags.

---

# 12. Prototype & testing plan

**Prototype**
- Build interactive prototype in Figma linking: Landing → Study Flashcard → Word Detail → Profile → Onboarding.

**User testing**
- Round 1: 5–8 users (target: logophiles) — focus on emotional reaction & comprehension.
- Round 2: 10–15 users — test flows, time to complete 5-card study session, discoverability of dictionary.

**Metrics**
- Task completion (start study → finish 5 cards)
- SUS score (System Usability Scale)
- Emotional response (qualitative)

---

# 13. Implementation recommendations

**Frontend framework**
- React (or Next.js) recommended with component library (Tailwind / Styled Components / CSS variables).
- Use SVG + CSS animations for simple microinteractions; Lottie for complex ones.

**Performance**
- Lazy-load large mascot illustrations and Lottie files.
- Use responsive images and `srcset`.

**State & data**
- Keep study progress local-first (IndexedDB) and sync with server when online.
- Export grammar and pronunciation assets via CDN.

**Localization**
- Place all UI strings in i18n JSON. Provide dev with keys and default English copy.

---

# 14. QA checklist

- [ ] Colors match tokens across pages
- [ ] Buttons/links accessible by keyboard
- [ ] Flashcard flip accessible and has reduced-motion fallback
- [ ] Audio playback has controls and is optional
- [ ] Exported assets load and have correct filenames
- [ ] Prototype interactions match animation spec

---

# 15. Next steps & timeline

**Phase 1 (1 week)** — Complete components + landing + study screen (clickable prototype).
**Phase 2 (1–2 weeks)** — Dictionary, profile, onboarding, and assets export.
**Phase 3 (1 week)** — Finalize animations, accessibility pass, handoff ZIP and PDF.

---

## Deliverables I will prepare for you (if you want me to build them):
- Figma project with organized pages and component library.
- Pixel-perfect mockups for: Landing, Dictionary, Study (desktop + mobile), Profile, Onboarding, Daily Challenge.
- Lottie animations for loader and milestone confetti.
- Exported asset ZIP (SVGs / PNGs / Lottie / audio) and the handoff PDF.
- Developer handoff doc (this doc + short 2-page quick guide).

---

If you’d like me to produce the Figma files, mockups, and export the assets, reply **"build the handoff"** and I’ll start by creating the Figma project files and the landing + study screens. If there are any constraints (framework, exact fonts, or file-format preferences), say them now so I include them in the handoff.

