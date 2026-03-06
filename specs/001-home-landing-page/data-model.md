# Data Model: Home Landing Page Foundation

This feature does not introduce persistent business entities or database tables.
The model below defines the view/data contract needed to satisfy rendering and validation requirements.

## Entity: LandingPageView
- Purpose: Represents all content required to render the landing page hero/branding surface.
- Fields:
  - `page_title` (string, required): Must equal `SCRUMMDidliumpcious`.
  - `logo_asset_path` (string, required): Must equal `images/scrumm_logo.svg`.
  - `logo_vertical_size` (string, required): Must equal `100em`.
  - `logo_anchor` (enum, required): `top-left`.
- Validation rules:
  - `page_title` must be non-empty and case-sensitive exact match.
  - `logo_asset_path` must reference an SVG asset path.
  - `logo_vertical_size` must include `em` unit and equal `100em`.
  - `logo_anchor` must be one of allowed layout anchors; this feature allows only `top-left`.

## Entity: LogoRenderConstraint
- Purpose: Encodes visual invariants for logo rendering.
- Fields:
  - `preserve_aspect_ratio` (boolean, required): Must be `true`.
  - `allow_distortion` (boolean, required): Must be `false`.
  - `responsive_visibility` (enum, required): `desktop-and-mobile`.
- Validation rules:
  - Distortion must never be enabled.
  - Constraint must remain true across supported viewport classes.

## Relationships
- `LandingPageView` references one `LogoRenderConstraint`.

## State Transitions
- Initial render state:
  - `LandingPageView` is constructed from static configuration and request context.
  - `LogoRenderConstraint` is applied during template render.
- Error state (missing logo asset):
  - Page remains renderable with title visible.
  - Logo region degrades gracefully without breaking page structure.
