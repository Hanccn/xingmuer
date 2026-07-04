# 行木儿 (Xingmuer) — Product Context

## Register
- **Register**: product (design SERVES the product)
- **Surface**: travel planning web app + PWA
- **Primary task**: search city → browse POIs → collect → analyze hotel location → generate route → export to phone

## Users & Purpose
- **Who**: Chinese free-travel users, 20-35, planning domestic trips
- **Context**: PC for deep planning (searching, collecting, route generation); mobile PWA for on-the-go viewing
- **Jobs to be done**:
  1. Discover attractions beyond the obvious hotspots
  2. Optimize hotel location based on selected attractions' geography
  3. Generate a sensible day-by-day route
  4. Export to phone for offline access during the trip
  5. Agent pre-departure check (weather, attraction status)

## Brand & Personality
- **3 words**: calm, efficient, trustworthy
- **Tone**: Not playful, not luxury. Clean utility with warmth. Like Notion/Linear — minimal but human.
- **Anti-references**: No Inter-default SaaS templates, no purple-blue gradients, no glassmorphism, no hero metrics, no section eyebrow numbers

## Visual Identity (from existing style.css + PRD)
- **Palette**: Accent `#2563EB`, Amber `#F59E0B`, Ink `#1E1E1C`, BG `#FBFAF8`, Surface `#FFFFFF`, Border `#E8E6E1`
- **Color strategy**: Restrained (tinted neutrals + one accent ≤10%)
- **Font**: Inter, system-ui fallback
- **Radius**: 8px
- **Shadow**: `0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.06)` — very light
- **No gradients, no heavy shadows**

## Accessibility
- Touch targets ≥ 44×44px on mobile
- Contrast: body text ≥4.5:1 on bg
- PWA offline support with degraded UI
