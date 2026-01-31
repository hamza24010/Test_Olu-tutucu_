# Task: PyQt6 Desktop UI Modernization (Glassmorphism)

Modernize the Test Oluşturucu application with a premium Glassmorphism design, utilizing PyQt6 and native translucency effects.

## 1. Analysis & Requirements
- **Tech Stack**: Python, PyQt6
- **Design Style**: Glassmorphism (Backdrop blur imitation, high transparency, desktop wallpaper bleed-through)
- **Target Audience**: Teachers (Simplified, professional, focus on workflow)
- **Key Constraints**: 
    - Desktop wallpaper leakage (translucency)
    - No performance fallback
    - Native desktop feel

## 2. Design System (Applied from ui-ux-pro-max)
- **Primary Color**: `#2563EB` (Trust Blue)
- **Accent Color**: `#F97316` (CTA Orange)
- **Glass Base**: `rgba(255, 255, 255, 0.1)` (Dark mode feel) or `rgba(255, 255, 255, 0.7)` (Light mode feel)
- **Blur**: Simulated via semi-transparency and grain if native blur is unavailable.
- **Typography**: Poppins (Headings), Open Sans (Body)
- **Icons**: Lucide/Heroicons (SVG icons)

## 3. Architecture Changes
- Move UI logic from `main.py` to `src/ui/`
- Introduce `StyleManager` for QSS management
- Create `CustomWindow` class for frameless and translucent functionality

## 4. Implementation Steps

### Phase 1: Foundation & Styles
- [x] Create `src/ui/styles.py` with Glassmorphism QSS
- [x] Implement `src/ui/components/glass_widgets.py` (Buttons, Cards, Sidebar)

### Phase 2: Shell Implementation
- [x] Create `src/ui/main_window.py` (Frameless, Translucent)
- [x] Add custom Title Bar (Close, Minimize, Dragging logic)
- [x] Add Layout management (Sidebar + Content Stack)

### Phase 3: Feature Integration
- [x] Port "Soru Bankası" logic to the new layout
- [x] Port "Test Oluştur" logic to the new layout
- [ ] Update PDF processing feedback (Progress bars, modern alerts)

### Phase 4: Final Polish
- [x] Add micro-animations (Hover effects, smooth transitions)
- [x] Final testing on Linux desktop environment (Gnome/KDE)

## 5. Verification Criteria
- [ ] Application window is translucent and shows wallpaper background.
- [ ] All existing functionalities (PDF Analyze, DB operations, PDF Export) work correctly.
- [ ] No layout shifts during interactions.
- [ ] High contrast (4.5:1+) for text against glass backgrounds.
