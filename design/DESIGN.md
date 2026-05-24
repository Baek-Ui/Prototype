---
name: Baek-ui
colors:
  surface: '#13131b'
  surface-dim: '#13131b'
  surface-bright: '#393841'
  surface-container-lowest: '#0d0d15'
  surface-container-low: '#1b1b23'
  surface-container: '#1f1f27'
  surface-container-high: '#292932'
  surface-container-highest: '#34343d'
  on-surface: '#e4e1ed'
  on-surface-variant: '#c7c4d7'
  inverse-surface: '#e4e1ed'
  inverse-on-surface: '#303038'
  outline: '#908fa0'
  outline-variant: '#464554'
  surface-tint: '#c0c1ff'
  primary: '#c0c1ff'
  on-primary: '#1000a9'
  primary-container: '#8083ff'
  on-primary-container: '#0d0096'
  inverse-primary: '#494bd6'
  secondary: '#d0bcff'
  on-secondary: '#3c0091'
  secondary-container: '#571bc1'
  on-secondary-container: '#c4abff'
  tertiary: '#ffb783'
  on-tertiary: '#4f2500'
  tertiary-container: '#d97721'
  on-tertiary-container: '#452000'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#e1e0ff'
  primary-fixed-dim: '#c0c1ff'
  on-primary-fixed: '#07006c'
  on-primary-fixed-variant: '#2f2ebe'
  secondary-fixed: '#e9ddff'
  secondary-fixed-dim: '#d0bcff'
  on-secondary-fixed: '#23005c'
  on-secondary-fixed-variant: '#5516be'
  tertiary-fixed: '#ffdcc5'
  tertiary-fixed-dim: '#ffb783'
  on-tertiary-fixed: '#301400'
  on-tertiary-fixed-variant: '#703700'
  background: '#13131b'
  on-background: '#e4e1ed'
  surface-variant: '#34343d'
typography:
  display-xl:
    fontFamily: Geist
    fontSize: 72px
    fontWeight: '800'
    lineHeight: '1.1'
    letterSpacing: -0.04em
  display-lg:
    fontFamily: Geist
    fontSize: 56px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: -0.03em
  headline-md:
    fontFamily: Geist
    fontSize: 36px
    fontWeight: '600'
    lineHeight: '1.3'
    letterSpacing: -0.02em
  headline-md-mobile:
    fontFamily: Geist
    fontSize: 28px
    fontWeight: '600'
    lineHeight: '1.3'
    letterSpacing: -0.02em
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  label-mono:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: '1'
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  gutter: 24px
  margin-desktop: 80px
  margin-mobile: 20px
  container-max: 1280px
---

## Brand & Style

The design system is a high-performance visual framework tailored for cutting-edge SaaS platforms. It prioritizes extreme clarity through a "void-black" aesthetic, where the absence of background light allows content to achieve maximum prominence. 

The visual narrative is built on the contrast between vast, dark digital space and vibrant, bioluminescent-inspired accents. By blending structural minimalism with glassmorphism, the UI achieves a sense of physical depth and intellectual sophistication. It targets a professional audience that values precision, speed, and the futuristic nature of deep learning technologies. Use whitespace not as "empty" space, but as a structural element to group cognitive concepts and reduce density.

## Colors

The palette is anchored in an absolute black (`#000000`) to create an infinite canvas effect. Surfaces that require separation from the background use a slightly elevated charcoal (`#0A0A0B`). 

Accents are defined by a sophisticated gradient of Indigo and Purple, symbolizing the "neural" spark of AI. Use these accents sparingly for primary actions, progress indicators, and focal points. Secondary text uses a desaturated slate-blue to maintain hierarchy without sacrificing readability against the dark background. Border colors are kept extremely low-opacity to ensure a "borderless" feel while still providing necessary structural definition.

## Typography

Typography in this design system is engineered for a technical, high-contrast environment. **Geist** is used for display and headings to provide a precise, modern, and slightly aggressive geometric feel. **Inter** handles body copy to ensure maximum legibility and comfort during long reading sessions. **JetBrains Mono** is utilized for metadata, tags, and small labels to reinforce the "engineered" nature of the product.

For headlines, use tight letter-spacing and substantial line-height to create authoritative blocks of text. Body text should maintain generous tracking and leading to ensure white text doesn't "glow" or bleed into the black background for the user's eye.

## Layout & Spacing

This design system utilizes a 12-column fluid grid for desktop and a 4-column grid for mobile. The layout philosophy is "expansive," favoring large margins to give content breathing room. 

A 4px base unit drives all spacing increments. Use large vertical padding (e.g., 120px to 160px) between landing page sections to signal clear conceptual shifts. Elements should rarely feel crowded; if in doubt, increase the spacing. Content is centered in a maximum width container of 1280px, while background effects and glass containers may bleed to the edges of the viewport.

## Elevation & Depth

Elevation is achieved through **Backdrop Blurs** and **Tonal Layering** rather than heavy shadows. 

1.  **Level 0 (Base):** Absolute black (#000000).
2.  **Level 1 (Cards):** Subtle charcoal surface with a 1px inner border (10% white) to catch the light.
3.  **Level 2 (Overlays/Modals):** Glassmorphism surfaces using `backdrop-filter: blur(20px)` and a background opacity of 40%.
4.  **Level 3 (Interactive):** Use "subtle glow" effects—outer shadows with a high blur radius (40px+) and low opacity (15%) using the primary indigo color to simulate a light-emitting screen.

Avoid traditional drop shadows that look "muddy" on black; use "rim lighting" (1px top/left borders) to define edges.

## Shapes

The design system employs a **Rounded** shape language to soften the high-contrast technical aesthetic. This creates a more approachable, human-centric feel within a high-tech framework.

Standard components like input fields and small buttons use a 0.5rem radius. Feature cards and large containers use `rounded-xl` (1.5rem) to create a "contained" and modern look. Use perfectly circular radii for tags and status indicators to maintain a "pill" aesthetic where appropriate.

## Components

### Buttons
- **Primary:** Gradient background (Indigo to Purple), white text, subtle indigo glow on hover.
- **Secondary:** Ghost style with a 1px white border at 20% opacity. Becomes 100% white text on hover with a slight background lift.
- **Tertiary:** Text only with an arrow icon, using the primary indigo color.

### Feature Cards
- **Construction:** Elevated charcoal background, 1.5rem corner radius.
- **Detailing:** A subtle 1px border. On hover, the border color transitions to a purple/indigo gradient, and a soft glow appears behind the card.
- **Icons:** Glass-enclosed icons with a background blur and a vibrant accent color.

### Data Visualization
- **Line Charts:** Glowing neon lines with a gradient area fill below (10% opacity).
- **Progress Bars:** Thin, sleek tracks with the primary gradient used for the fill.

### Input Fields
- Dark backgrounds (slightly lighter than base) with a 1px border. The border glows indigo upon focus, and the label moves to a "floating" position using the mono font.

### Chips/Tags
- Small, pill-shaped elements with a low-opacity indigo background and high-saturation text. Use for categories or AI-status indicators.