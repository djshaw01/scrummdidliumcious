"""Pydantic boundary model for the landing page view contract."""

from typing import Literal

from pydantic import BaseModel, field_validator


class LandingPageView(BaseModel):
    """Represents all content required to render the landing page hero/branding surface.

    :param page_title: Visible page title; must equal ``SCRUMMDidliumcious``.
    :param logo_asset_path: Relative path to the SVG logo asset.
    :param logo_vertical_size: CSS height value for the logo; must equal ``100em``.
    :param logo_anchor: Layout anchor for the logo; only ``top-left`` is allowed.
    :param logo_fallback_text: Alt text rendered when the logo asset cannot be loaded.
    :param preserve_aspect_ratio: Logo must not be distorted; always ``True``.
    """

    page_title: str = "SCRUMMDidliumcious"
    logo_asset_path: str = "images/scrumm_logo.svg"
    logo_vertical_size: str = "100em"
    logo_anchor: Literal["top-left"] = "top-left"
    logo_fallback_text: str = "SCRUMMDidliumcious logo"
    preserve_aspect_ratio: bool = True

    @field_validator("page_title")
    @classmethod
    def title_must_be_exact(cls, value: str) -> str:
        """Validate that the page title matches the required exact value.

        :param value: Candidate title string.
        :returns: Validated title string.
        :raises ValueError: If the title does not match ``SCRUMMDidliumcious``.
        """
        if value != "SCRUMMDidliumcious":
            raise ValueError(
                f"page_title must be exactly 'SCRUMMDidliumcious', got '{value}'"
            )
        return value

    @field_validator("logo_asset_path")
    @classmethod
    def path_must_be_svg(cls, value: str) -> str:
        """Validate that the logo asset path references an SVG file.

        :param value: Candidate asset path.
        :returns: Validated asset path.
        :raises ValueError: If the path does not end with ``.svg``.
        """
        if not value.endswith(".svg"):
            raise ValueError(
                f"logo_asset_path must reference an SVG asset, got '{value}'"
            )
        return value

    @field_validator("logo_vertical_size")
    @classmethod
    def size_must_be_100em(cls, value: str) -> str:
        """Validate that the logo vertical size equals '100em'.

        :param value: Candidate size string.
        :returns: Validated size string.
        :raises ValueError: If the size is not ``100em``.
        """
        if value != "100em":
            raise ValueError(f"logo_vertical_size must be '100em', got '{value}'")
        return value
