"""
Music Assistant MCP Server
==========================
A FastMCP server that exposes the full Music Assistant API as MCP tools.
Connects to a Music Assistant server via its REST/JSON API.
"""

import json
import os
from typing import Any

import httpx
from fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Configuration – all sourced from environment variables
# ---------------------------------------------------------------------------
MA_URL = os.environ.get("MA_URL", "http://localhost:8095")
MA_TOKEN = os.environ.get("MA_TOKEN", "")

mcp = FastMCP(
    "Music Assistant",
    instructions=(
        "Control and query a Music Assistant server. "
        "Use these tools to search music, manage playlists, control players, "
        "manage playback queues, and configure the system."
    ),
)

# ---------------------------------------------------------------------------
# Helpers
async def _call_ma(command: str, args: dict[str, Any] | None = None) -> Any:
    """Send a command to the Music Assistant JSON API and return the result."""
    payload: dict[str, Any] = {"command": command, "args": args or {}}

    headers: dict[str, str] = {"Content-Type": "application/json"}
    if MA_TOKEN:
        headers["Authorization"] = f"Bearer {MA_TOKEN}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(f"{MA_URL}/api", json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    # The MA API may wrap results; return the inner result when present
    if isinstance(data, dict):
        if "error" in data:
            raise RuntimeError(f"Music Assistant error: {data['error']}")
        if "result" in data:
            return data["result"]
    return data


def _compact(obj: Any, max_items: int = 50) -> Any:
    """Trim large lists so MCP responses stay manageable."""
    if isinstance(obj, list) and len(obj) > max_items:
        return obj[:max_items]
    return obj


# =========================================================================
#  MUSIC LIBRARY — Tracks
# =========================================================================


@mcp.tool
async def get_library_tracks(
    favorite: bool | None = None,
    search: str | None = None,
    limit: int = 25,
    offset: int = 0,
    order_by: str = "sort_name",
) -> str:
    """Get tracks from the music library.

    Args:
        favorite: Filter by favorite status (True/False/None for all).
        search: Text search query to filter tracks.
        limit: Maximum number of results (default 25).
        offset: Pagination offset.
        order_by: Sort field (e.g. sort_name, timestamp_added, name).
    """
    args: dict[str, Any] = {"limit": limit, "offset": offset, "order_by": order_by}
    if favorite is not None:
        args["favorite"] = favorite
    if search:
        args["search"] = search
    result = await _call_ma("music/tracks/library_items", args)
    return json.dumps(_compact(result), default=str)


@mcp.tool
async def get_track(
    item_id: str,
    provider_instance_id_or_domain: str = "library",
) -> str:
    """Get full details for a single track.

    Args:
        item_id: The track ID.
        provider_instance_id_or_domain: Provider instance or 'library'.
    """
    result = await _call_ma(
        "music/tracks/get_track",
        {"item_id": item_id, "provider_instance_id_or_domain": provider_instance_id_or_domain},
    )
    return json.dumps(result, default=str)


@mcp.tool
async def get_track_versions(
    item_id: str,
    provider_instance_id_or_domain: str = "library",
) -> str:
    """Get all versions/variants of a track across providers.

    Args:
        item_id: The track ID.
        provider_instance_id_or_domain: Provider instance or 'library'.
    """
    result = await _call_ma(
        "music/tracks/track_versions",
        {"item_id": item_id, "provider_instance_id_or_domain": provider_instance_id_or_domain},
    )
    return json.dumps(_compact(result), default=str)


@mcp.tool
async def get_track_albums(
    item_id: str,
    provider_instance_id_or_domain: str = "library",
) -> str:
    """Get albums that contain a given track.

    Args:
        item_id: The track ID.
        provider_instance_id_or_domain: Provider instance or 'library'.
    """
    result = await _call_ma(
        "music/tracks/track_albums",
        {"item_id": item_id, "provider_instance_id_or_domain": provider_instance_id_or_domain},
    )
    return json.dumps(_compact(result), default=str)


@mcp.tool
async def get_track_preview_url(
    item_id: str,
    provider_instance_id_or_domain: str = "library",
) -> str:
    """Get a short preview URL for a track.

    Args:
        item_id: The track ID.
        provider_instance_id_or_domain: Provider instance or 'library'.
    """
    result = await _call_ma(
        "music/tracks/preview",
        {"item_id": item_id, "provider_instance_id_or_domain": provider_instance_id_or_domain},
    )
    return json.dumps(result, default=str)


# =========================================================================
#  MUSIC LIBRARY — Albums
# =========================================================================


@mcp.tool
async def get_library_albums(
    favorite: bool | None = None,
    search: str | None = None,
    limit: int = 25,
    offset: int = 0,
    order_by: str = "sort_name",
) -> str:
    """Get albums from the music library.

    Args:
        favorite: Filter by favorite status.
        search: Text search query.
        limit: Max results (default 25).
        offset: Pagination offset.
        order_by: Sort field.
    """
    args: dict[str, Any] = {"limit": limit, "offset": offset, "order_by": order_by}
    if favorite is not None:
        args["favorite"] = favorite
    if search:
        args["search"] = search
    result = await _call_ma("music/albums/library_items", args)
    return json.dumps(_compact(result), default=str)


@mcp.tool
async def get_album(
    item_id: str,
    provider_instance_id_or_domain: str = "library",
) -> str:
    """Get full details for a single album.

    Args:
        item_id: The album ID.
        provider_instance_id_or_domain: Provider instance or 'library'.
    """
    result = await _call_ma(
        "music/albums/get_album",
        {"item_id": item_id, "provider_instance_id_or_domain": provider_instance_id_or_domain},
    )
    return json.dumps(result, default=str)


@mcp.tool
async def get_album_tracks(
    item_id: str,
    provider_instance_id_or_domain: str = "library",
    in_library_only: bool = False,
) -> str:
    """Get all tracks in an album.

    Args:
        item_id: The album ID.
        provider_instance_id_or_domain: Provider instance or 'library'.
        in_library_only: Only return tracks already in your library.
    """
    result = await _call_ma(
        "music/albums/album_tracks",
        {
            "item_id": item_id,
            "provider_instance_id_or_domain": provider_instance_id_or_domain,
            "in_library_only": in_library_only,
        },
    )
    return json.dumps(_compact(result), default=str)


@mcp.tool
async def get_album_versions(
    item_id: str,
    provider_instance_id_or_domain: str = "library",
) -> str:
    """Get all versions/variants of an album across providers.

    Args:
        item_id: The album ID.
        provider_instance_id_or_domain: Provider instance or 'library'.
    """
    result = await _call_ma(
        "music/albums/album_versions",
        {"item_id": item_id, "provider_instance_id_or_domain": provider_instance_id_or_domain},
    )
    return json.dumps(_compact(result), default=str)


# =========================================================================
#  MUSIC LIBRARY — Artists
# =========================================================================


@mcp.tool
async def get_library_artists(
    favorite: bool | None = None,
    search: str | None = None,
    limit: int = 25,
    offset: int = 0,
    order_by: str = "sort_name",
    album_artists_only: bool = False,
) -> str:
    """Get artists from the music library.

    Args:
        favorite: Filter by favorite status.
        search: Text search query.
        limit: Max results.
        offset: Pagination offset.
        order_by: Sort field.
        album_artists_only: Only return album artists (not featured).
    """
    args: dict[str, Any] = {
        "limit": limit,
        "offset": offset,
        "order_by": order_by,
        "album_artists_only": album_artists_only,
    }
    if favorite is not None:
        args["favorite"] = favorite
    if search:
        args["search"] = search
    result = await _call_ma("music/artists/library_items", args)
    return json.dumps(_compact(result), default=str)


@mcp.tool
async def get_artist(
    item_id: str,
    provider_instance_id_or_domain: str = "library",
) -> str:
    """Get full details for a single artist.

    Args:
        item_id: The artist ID.
        provider_instance_id_or_domain: Provider instance or 'library'.
    """
    result = await _call_ma(
        "music/artists/get_artist",
        {"item_id": item_id, "provider_instance_id_or_domain": provider_instance_id_or_domain},
    )
    return json.dumps(result, default=str)


@mcp.tool
async def get_artist_tracks(
    item_id: str,
    provider_instance_id_or_domain: str = "library",
) -> str:
    """Get the top / popular tracks by an artist.

    Args:
        item_id: The artist ID.
        provider_instance_id_or_domain: Provider instance or 'library'.
    """
    result = await _call_ma(
        "music/artists/artist_tracks",
        {"item_id": item_id, "provider_instance_id_or_domain": provider_instance_id_or_domain},
    )
    return json.dumps(_compact(result), default=str)


@mcp.tool
async def get_artist_albums(
    item_id: str,
    provider_instance_id_or_domain: str = "library",
) -> str:
    """Get albums by an artist.

    Args:
        item_id: The artist ID.
        provider_instance_id_or_domain: Provider instance or 'library'.
    """
    result = await _call_ma(
        "music/artists/artist_albums",
        {"item_id": item_id, "provider_instance_id_or_domain": provider_instance_id_or_domain},
    )
    return json.dumps(_compact(result), default=str)


# =========================================================================
#  MUSIC LIBRARY — Playlists
# =========================================================================


@mcp.tool
async def get_library_playlists(
    favorite: bool | None = None,
    search: str | None = None,
    limit: int = 25,
    offset: int = 0,
    order_by: str = "sort_name",
) -> str:
    """Get playlists from the music library.

    Args:
        favorite: Filter by favorite status.
        search: Text search query.
        limit: Max results.
        offset: Pagination offset.
        order_by: Sort field.
    """
    args: dict[str, Any] = {"limit": limit, "offset": offset, "order_by": order_by}
    if favorite is not None:
        args["favorite"] = favorite
    if search:
        args["search"] = search
    result = await _call_ma("music/playlists/library_items", args)
    return json.dumps(_compact(result), default=str)


@mcp.tool
async def get_playlist(
    item_id: str,
    provider_instance_id_or_domain: str = "library",
) -> str:
    """Get full details for a single playlist.

    Args:
        item_id: The playlist ID.
        provider_instance_id_or_domain: Provider instance or 'library'.
    """
    result = await _call_ma(
        "music/playlists/get_playlist",
        {"item_id": item_id, "provider_instance_id_or_domain": provider_instance_id_or_domain},
    )
    return json.dumps(result, default=str)


@mcp.tool
async def get_playlist_tracks(
    item_id: str,
    provider_instance_id_or_domain: str = "library",
    force_refresh: bool = False,
) -> str:
    """Get all tracks in a playlist.

    Args:
        item_id: The playlist ID.
        provider_instance_id_or_domain: Provider instance or 'library'.
        force_refresh: Force a fresh fetch from the provider.
    """
    args: dict[str, Any] = {
        "item_id": item_id,
        "provider_instance_id_or_domain": provider_instance_id_or_domain,
    }
    if force_refresh:
        args["force_refresh"] = True
    result = await _call_ma("music/playlists/playlist_tracks", args)
    return json.dumps(_compact(result), default=str)


@mcp.tool
async def create_playlist(
    name: str,
    provider_instance_or_domain: str | None = None,
) -> str:
    """Create a new empty playlist.

    Args:
        name: Name for the new playlist.
        provider_instance_or_domain: Provider to create on (uses default if omitted).
    """
    args: dict[str, Any] = {"name": name}
    if provider_instance_or_domain:
        args["provider_instance_or_domain"] = provider_instance_or_domain
    result = await _call_ma("music/playlists/create_playlist", args)
    return json.dumps(result, default=str)


@mcp.tool
async def add_playlist_tracks(
    db_playlist_id: str,
    uris: list[str],
) -> str:
    """Add tracks to a playlist.

    Args:
        db_playlist_id: The database playlist ID.
        uris: List of track URIs to add (e.g. ['spotify://track/abc123']).
    """
    await _call_ma(
        "music/playlists/add_playlist_tracks",
        {"db_playlist_id": db_playlist_id, "uris": uris},
    )
    return json.dumps({"status": "ok", "added": len(uris)})


@mcp.tool
async def remove_playlist_tracks(
    db_playlist_id: str,
    positions_to_remove: list[int],
) -> str:
    """Remove tracks from a playlist by position.

    Args:
        db_playlist_id: The database playlist ID.
        positions_to_remove: List of track positions (0-based) to remove.
    """
    await _call_ma(
        "music/playlists/remove_playlist_tracks",
        {"db_playlist_id": db_playlist_id, "positions_to_remove": positions_to_remove},
    )
    return json.dumps({"status": "ok", "removed": len(positions_to_remove)})


# =========================================================================
#  MUSIC LIBRARY — Podcasts
# =========================================================================


@mcp.tool
async def get_library_podcasts(
    favorite: bool | None = None,
    search: str | None = None,
    limit: int = 25,
    offset: int = 0,
    order_by: str = "sort_name",
) -> str:
    """Get podcasts from the music library.

    Args:
        favorite: Filter by favorite status.
        search: Text search query.
        limit: Max results.
        offset: Pagination offset.
        order_by: Sort field.
    """
    args: dict[str, Any] = {"limit": limit, "offset": offset, "order_by": order_by}
    if favorite is not None:
        args["favorite"] = favorite
    if search:
        args["search"] = search
    result = await _call_ma("music/podcasts/library_items", args)
    return json.dumps(_compact(result), default=str)


@mcp.tool
async def get_podcast(
    item_id: str,
    provider_instance_id_or_domain: str = "library",
) -> str:
    """Get full details for a single podcast.

    Args:
        item_id: The podcast ID.
        provider_instance_id_or_domain: Provider instance or 'library'.
    """
    result = await _call_ma(
        "music/podcasts/get_podcast",
        {"item_id": item_id, "provider_instance_id_or_domain": provider_instance_id_or_domain},
    )
    return json.dumps(result, default=str)


@mcp.tool
async def get_podcast_episodes(
    item_id: str,
    provider_instance_id_or_domain: str = "library",
) -> str:
    """Get episodes for a podcast.

    Args:
        item_id: The podcast ID.
        provider_instance_id_or_domain: Provider instance or 'library'.
    """
    result = await _call_ma(
        "music/podcasts/podcast_episodes",
        {"item_id": item_id, "provider_instance_id_or_domain": provider_instance_id_or_domain},
    )
    return json.dumps(_compact(result), default=str)


# =========================================================================
#  MUSIC LIBRARY — Audiobooks
# =========================================================================


@mcp.tool
async def get_library_audiobooks(
    favorite: bool | None = None,
    search: str | None = None,
    limit: int = 25,
    offset: int = 0,
    order_by: str = "sort_name",
) -> str:
    """Get audiobooks from the music library.

    Args:
        favorite: Filter by favorite status.
        search: Text search query.
        limit: Max results.
        offset: Pagination offset.
        order_by: Sort field.
    """
    args: dict[str, Any] = {"limit": limit, "offset": offset, "order_by": order_by}
    if favorite is not None:
        args["favorite"] = favorite
    if search:
        args["search"] = search
    result = await _call_ma("music/audiobooks/library_items", args)
    return json.dumps(_compact(result), default=str)


@mcp.tool
async def get_audiobook(
    item_id: str,
    provider_instance_id_or_domain: str = "library",
) -> str:
    """Get full details for a single audiobook.

    Args:
        item_id: The audiobook ID.
        provider_instance_id_or_domain: Provider instance or 'library'.
    """
    result = await _call_ma(
        "music/audiobooks/get_audiobook",
        {"item_id": item_id, "provider_instance_id_or_domain": provider_instance_id_or_domain},
    )
    return json.dumps(result, default=str)


# =========================================================================
#  MUSIC LIBRARY — Radio
# =========================================================================


@mcp.tool
async def get_library_radios(
    favorite: bool | None = None,
    search: str | None = None,
    limit: int = 25,
    offset: int = 0,
    order_by: str = "sort_name",
) -> str:
    """Get radio stations from the music library.

    Args:
        favorite: Filter by favorite status.
        search: Text search query.
        limit: Max results.
        offset: Pagination offset.
        order_by: Sort field.
    """
    args: dict[str, Any] = {"limit": limit, "offset": offset, "order_by": order_by}
    if favorite is not None:
        args["favorite"] = favorite
    if search:
        args["search"] = search
    result = await _call_ma("music/radios/library_items", args)
    return json.dumps(_compact(result), default=str)


@mcp.tool
async def get_radio(
    item_id: str,
    provider_instance_id_or_domain: str = "library",
) -> str:
    """Get full details for a single radio station.

    Args:
        item_id: The radio station ID.
        provider_instance_id_or_domain: Provider instance or 'library'.
    """
    result = await _call_ma(
        "music/radios/get_radio",
        {"item_id": item_id, "provider_instance_id_or_domain": provider_instance_id_or_domain},
    )
    return json.dumps(result, default=str)


@mcp.tool
async def get_radio_versions(
    item_id: str,
    provider_instance_id_or_domain: str = "library",
) -> str:
    """Get all versions/variants of a radio station across providers.

    Args:
        item_id: The radio station ID.
        provider_instance_id_or_domain: Provider instance or 'library'.
    """
    result = await _call_ma(
        "music/radios/radio_versions",
        {"item_id": item_id, "provider_instance_id_or_domain": provider_instance_id_or_domain},
    )
    return json.dumps(_compact(result), default=str)


# =========================================================================
#  MUSIC LIBRARY — Search & Discovery
# =========================================================================


@mcp.tool
async def search(
    search_query: str,
    media_types: list[str] | None = None,
    limit: int = 10,
    library_only: bool = False,
) -> str:
    """Search across all music providers and library.

    Args:
        search_query: The text to search for.
        media_types: List of types to search (track, album, artist, playlist, radio, podcast, audiobook). None = all.
        limit: Max results per media type.
        library_only: Only search items already in the library.
    """
    args: dict[str, Any] = {"search_query": search_query, "limit": limit, "library_only": library_only}
    if media_types:
        args["media_types"] = media_types
    result = await _call_ma("music/search", args)
    return json.dumps(result, default=str)


@mcp.tool
async def browse(path: str | None = None) -> str:
    """Browse music provider content hierarchically.

    Args:
        path: Provider path to browse (e.g. 'spotify://playlists'). None for root.
    """
    args: dict[str, Any] = {}
    if path:
        args["path"] = path
    result = await _call_ma("music/browse", args)
    return json.dumps(_compact(result), default=str)


@mcp.tool
async def recently_played(limit: int = 10, media_types: list[str] | None = None) -> str:
    """Get recently played items.

    Args:
        limit: Max results.
        media_types: Filter by type (track, album, etc.). None for all.
    """
    args: dict[str, Any] = {"limit": limit}
    if media_types:
        args["media_types"] = media_types
    result = await _call_ma("music/recently_played_items", args)
    return json.dumps(_compact(result), default=str)


@mcp.tool
async def in_progress_items(limit: int = 10) -> str:
    """Get audiobooks and podcast episodes that are in progress.

    Args:
        limit: Max results.
    """
    result = await _call_ma("music/in_progress_items", {"limit": limit})
    return json.dumps(_compact(result), default=str)


@mcp.tool
async def recommendations() -> str:
    """Get personalized music recommendations from all providers."""
    result = await _call_ma("music/recommendations")
    return json.dumps(_compact(result), default=str)


# =========================================================================
#  MUSIC LIBRARY — Item Management
# =========================================================================


@mcp.tool
async def get_item_by_uri(uri: str) -> str:
    """Get a media item by its Music Assistant URI or share URL.

    Args:
        uri: The URI (e.g. 'spotify://track/123' or a share URL).
    """
    result = await _call_ma("music/item_by_uri", {"uri": uri})
    return json.dumps(result, default=str)


@mcp.tool
async def get_item(
    media_type: str,
    item_id: str,
    provider_instance_id_or_domain: str = "library",
) -> str:
    """Get a media item by type and ID.

    Args:
        media_type: One of: track, album, artist, playlist, radio, podcast, audiobook.
        item_id: The item ID.
        provider_instance_id_or_domain: Provider or 'library'.
    """
    result = await _call_ma(
        f"music/{media_type}s/get_{media_type}",
        {"item_id": item_id, "provider_instance_id_or_domain": provider_instance_id_or_domain},
    )
    return json.dumps(result, default=str)


@mcp.tool
async def add_item_to_favorites(item: str) -> str:
    """Add a media item to favorites.

    Args:
        item: URI or share URL of the item.
    """
    await _call_ma("music/favorites/add_item", {"item": item})
    return json.dumps({"status": "ok", "item": item})


@mcp.tool
async def remove_item_from_favorites(
    media_type: str,
    item_id: str,
    provider_instance_id_or_domain: str = "library",
) -> str:
    """Remove a media item from favorites.

    Args:
        media_type: One of: track, album, artist, playlist, radio, podcast, audiobook.
        item_id: The item ID.
        provider_instance_id_or_domain: Provider or 'library'.
    """
    await _call_ma(
        "music/favorites/remove_item",
        {
            "media_type": media_type,
            "item_id": item_id,
            "provider_instance_id_or_domain": provider_instance_id_or_domain,
        },
    )
    return json.dumps({"status": "ok"})


@mcp.tool
async def add_item_to_library(uri: str) -> str:
    """Add a media item to the library.

    Args:
        uri: URI of the item to add.
    """
    result = await _call_ma("music/library/add_item", {"item": uri})
    return json.dumps(result, default=str)


@mcp.tool
async def remove_item_from_library(
    media_type: str,
    item_id: str,
    provider_instance_id_or_domain: str = "library",
) -> str:
    """Remove a media item from the library.

    Args:
        media_type: One of: track, album, artist, playlist, radio, podcast, audiobook.
        item_id: The item ID.
        provider_instance_id_or_domain: Provider or 'library'.
    """
    await _call_ma(
        "music/library/remove_item",
        {
            "media_type": media_type,
            "item_id": item_id,
            "provider_instance_id_or_domain": provider_instance_id_or_domain,
        },
    )
    return json.dumps({"status": "ok"})


@mcp.tool
async def refresh_item(
    media_type: str,
    item_id: str,
    provider_instance_id_or_domain: str = "library",
) -> str:
    """Refresh the metadata for a media item.

    Args:
        media_type: One of: track, album, artist, playlist, radio, podcast, audiobook.
        item_id: The item ID.
        provider_instance_id_or_domain: Provider or 'library'.
    """
    result = await _call_ma(
        f"music/{media_type}s/refresh_item",
        {"item_id": item_id, "provider_instance_id_or_domain": provider_instance_id_or_domain},
    )
    return json.dumps(result, default=str)


@mcp.tool
async def mark_item_played(
    media_type: str,
    item_id: str,
    provider_instance_id_or_domain: str = "library",
) -> str:
    """Mark a media item as played.

    Args:
        media_type: One of: track, album, artist, playlist, radio, podcast, audiobook.
        item_id: The item ID.
        provider_instance_id_or_domain: Provider or 'library'.
    """
    await _call_ma(
        "music/mark_item_played",
        {
            "media_type": media_type,
            "item_id": item_id,
            "provider_instance_id_or_domain": provider_instance_id_or_domain,
        },
    )
    return json.dumps({"status": "ok"})


@mcp.tool
async def mark_item_unplayed(
    media_type: str,
    item_id: str,
    provider_instance_id_or_domain: str = "library",
) -> str:
    """Mark a media item as unplayed.

    Args:
        media_type: One of: track, album, artist, playlist, radio, podcast, audiobook.
        item_id: The item ID.
        provider_instance_id_or_domain: Provider or 'library'.
    """
    await _call_ma(
        "music/mark_item_unplayed",
        {
            "media_type": media_type,
            "item_id": item_id,
            "provider_instance_id_or_domain": provider_instance_id_or_domain,
        },
    )
    return json.dumps({"status": "ok"})


# =========================================================================
#  MUSIC LIBRARY — Sync
# =========================================================================


@mcp.tool
async def start_sync(
    media_types: list[str] | None = None,
    providers: list[str] | None = None,
) -> str:
    """Start syncing music providers to the library.

    Args:
        media_types: Sync only these types (track, album, artist, playlist, radio, podcast, audiobook). None = all.
        providers: Sync only these provider instance IDs. None = all.
    """
    args: dict[str, Any] = {}
    if media_types:
        args["media_types"] = media_types
    if providers:
        args["providers"] = providers
    await _call_ma("music/sync", args)
    return json.dumps({"status": "sync_started"})


@mcp.tool
async def get_running_sync_tasks() -> str:
    """Get the currently running sync tasks and their status."""
    result = await _call_ma("music/synctasks")
    return json.dumps(result, default=str)


# =========================================================================
#  PLAYERS — Listing & Info
# =========================================================================


@mcp.tool
async def get_players() -> str:
    """Get all available players and their current state."""
    result = await _call_ma("players/all")
    return json.dumps(_compact(result), default=str)


@mcp.tool
async def get_player(player_id: str) -> str:
    """Get full details for a single player.

    Args:
        player_id: The player ID.
    """
    result = await _call_ma("players/get", {"player_id": player_id})
    return json.dumps(result, default=str)


# =========================================================================
#  PLAYERS — Playback Control
# =========================================================================


@mcp.tool
async def player_command_play(player_id: str) -> str:
    """Start playback on a player.

    Args:
        player_id: The player ID.
    """
    await _call_ma("players/cmd/play", {"player_id": player_id})
    return json.dumps({"status": "ok", "player_id": player_id, "action": "play"})


@mcp.tool
async def player_command_pause(player_id: str) -> str:
    """Pause playback on a player.

    Args:
        player_id: The player ID.
    """
    await _call_ma("players/cmd/pause", {"player_id": player_id})
    return json.dumps({"status": "ok", "player_id": player_id, "action": "pause"})


@mcp.tool
async def player_command_stop(player_id: str) -> str:
    """Stop playback on a player.

    Args:
        player_id: The player ID.
    """
    await _call_ma("players/cmd/stop", {"player_id": player_id})
    return json.dumps({"status": "ok", "player_id": player_id, "action": "stop"})


@mcp.tool
async def player_command_play_pause(player_id: str) -> str:
    """Toggle play/pause on a player.

    Args:
        player_id: The player ID.
    """
    await _call_ma("players/cmd/play_pause", {"player_id": player_id})
    return json.dumps({"status": "ok", "player_id": player_id, "action": "play_pause"})


@mcp.tool
async def player_command_next_track(player_id: str) -> str:
    """Skip to the next track on a player.

    Args:
        player_id: The player ID.
    """
    await _call_ma("players/cmd/next", {"player_id": player_id})
    return json.dumps({"status": "ok", "player_id": player_id, "action": "next"})


@mcp.tool
async def player_command_previous_track(player_id: str) -> str:
    """Go to the previous track on a player.

    Args:
        player_id: The player ID.
    """
    await _call_ma("players/cmd/previous", {"player_id": player_id})
    return json.dumps({"status": "ok", "player_id": player_id, "action": "previous"})


@mcp.tool
async def player_command_seek(player_id: str, position: int) -> str:
    """Seek to a position in the current track.

    Args:
        player_id: The player ID.
        position: Target position in seconds.
    """
    await _call_ma("players/cmd/seek", {"player_id": player_id, "position": position})
    return json.dumps({"status": "ok", "player_id": player_id, "position": position})


# =========================================================================
#  PLAYERS — Volume & Power
# =========================================================================


@mcp.tool
async def player_command_volume_set(player_id: str, volume_level: int) -> str:
    """Set the volume of a player.

    Args:
        player_id: The player ID.
        volume_level: Volume level 0-100.
    """
    await _call_ma("players/cmd/volume_set", {"player_id": player_id, "volume_level": volume_level})
    return json.dumps({"status": "ok", "player_id": player_id, "volume": volume_level})


@mcp.tool
async def player_command_volume_up(player_id: str) -> str:
    """Increase the volume of a player by one step.

    Args:
        player_id: The player ID.
    """
    await _call_ma("players/cmd/volume_up", {"player_id": player_id})
    return json.dumps({"status": "ok", "player_id": player_id, "action": "volume_up"})


@mcp.tool
async def player_command_volume_down(player_id: str) -> str:
    """Decrease the volume of a player by one step.

    Args:
        player_id: The player ID.
    """
    await _call_ma("players/cmd/volume_down", {"player_id": player_id})
    return json.dumps({"status": "ok", "player_id": player_id, "action": "volume_down"})


@mcp.tool
async def player_command_volume_mute(player_id: str, muted: bool) -> str:
    """Mute or unmute a player.

    Args:
        player_id: The player ID.
        muted: True to mute, False to unmute.
    """
    await _call_ma("players/cmd/volume_mute", {"player_id": player_id, "muted": muted})
    return json.dumps({"status": "ok", "player_id": player_id, "muted": muted})


@mcp.tool
async def player_command_power(player_id: str, powered: bool) -> str:
    """Power a player on or off.

    Args:
        player_id: The player ID.
        powered: True for on, False for off.
    """
    await _call_ma("players/cmd/power", {"player_id": player_id, "powered": powered})
    return json.dumps({"status": "ok", "player_id": player_id, "powered": powered})


@mcp.tool
async def set_player_group_volume(player_id: str, volume_level: int) -> str:
    """Set the average volume for all players in a group.

    Args:
        player_id: The group leader player ID.
        volume_level: Target average volume 0-100.
    """
    await _call_ma("players/cmd/group_volume", {"player_id": player_id, "volume_level": volume_level})
    return json.dumps({"status": "ok", "player_id": player_id, "group_volume": volume_level})


@mcp.tool
async def player_command_group_volume_up(player_id: str) -> str:
    """Increase the volume for all players in a group.

    Args:
        player_id: The group leader player ID.
    """
    await _call_ma("players/cmd/group_volume_up", {"player_id": player_id})
    return json.dumps({"status": "ok", "player_id": player_id, "action": "group_volume_up"})


@mcp.tool
async def player_command_group_volume_down(player_id: str) -> str:
    """Decrease the volume for all players in a group.

    Args:
        player_id: The group leader player ID.
    """
    await _call_ma("players/cmd/group_volume_down", {"player_id": player_id})
    return json.dumps({"status": "ok", "player_id": player_id, "action": "group_volume_down"})


# =========================================================================
#  PLAYERS — Grouping
# =========================================================================


@mcp.tool
async def player_command_group(player_id: str, target_player: str) -> str:
    """Join a player to a group led by target_player.

    Args:
        player_id: The player to join.
        target_player: The group leader player ID.
    """
    await _call_ma("players/cmd/group", {"player_id": player_id, "target_player": target_player})
    return json.dumps({"status": "ok", "player_id": player_id, "grouped_with": target_player})


@mcp.tool
async def player_command_ungroup(player_id: str) -> str:
    """Remove a player from its current group.

    Args:
        player_id: The player ID.
    """
    await _call_ma("players/cmd/ungroup", {"player_id": player_id})
    return json.dumps({"status": "ok", "player_id": player_id, "action": "ungrouped"})


@mcp.tool
async def player_command_group_many(target_player: str, child_player_ids: list[str]) -> str:
    """Join multiple players to a group.

    Args:
        target_player: The group leader player ID.
        child_player_ids: List of player IDs to join.
    """
    await _call_ma(
        "players/cmd/group_many",
        {"target_player": target_player, "child_player_ids": child_player_ids},
    )
    return json.dumps({"status": "ok", "leader": target_player, "members": child_player_ids})


@mcp.tool
async def player_command_ungroup_many(player_ids: list[str]) -> str:
    """Remove multiple players from their groups.

    Args:
        player_ids: List of player IDs to ungroup.
    """
    await _call_ma("players/cmd/ungroup_many", {"player_ids": player_ids})
    return json.dumps({"status": "ok", "ungrouped": player_ids})


# =========================================================================
#  PLAYERS — Advanced
# =========================================================================


@mcp.tool
async def play_announcement(
    player_id: str,
    url: str,
    use_pre_announce: bool | None = None,
    volume_level: int | None = None,
) -> str:
    """Play an audio announcement on a player. Pauses current playback, plays the announcement, then resumes.

    Args:
        player_id: The player ID.
        url: URL of the announcement audio.
        use_pre_announce: Play a pre-announcement tone first.
        volume_level: Override volume for the announcement.
    """
    args: dict[str, Any] = {"player_id": player_id, "url": url}
    if use_pre_announce is not None:
        args["use_pre_announce"] = use_pre_announce
    if volume_level is not None:
        args["volume_level"] = volume_level
    await _call_ma("players/cmd/play_announcement", args)
    return json.dumps({"status": "ok", "player_id": player_id, "action": "announcement"})


@mcp.tool
async def player_command_select_source(player_id: str, source: str) -> str:
    """Select an input source on a player (if supported).

    Args:
        player_id: The player ID.
        source: The source identifier.
    """
    await _call_ma("players/cmd/select_source", {"player_id": player_id, "source": source})
    return json.dumps({"status": "ok", "player_id": player_id, "source": source})


# =========================================================================
#  PLAYER QUEUES — Listing
# =========================================================================


@mcp.tool
async def get_player_queues() -> str:
    """Get all player queues and their current state."""
    result = await _call_ma("player_queues/all")
    return json.dumps(_compact(result), default=str)


@mcp.tool
async def get_player_queue_items(
    queue_id: str,
    limit: int = 50,
    offset: int = 0,
) -> str:
    """Get items in a player queue.

    Args:
        queue_id: The queue ID (usually same as player_id).
        limit: Max items to return (max 500).
        offset: Pagination offset.
    """
    result = await _call_ma(
        "player_queues/items",
        {"queue_id": queue_id, "limit": limit, "offset": offset},
    )
    return json.dumps(_compact(result), default=str)


@mcp.tool
async def get_active_queue(player_id: str) -> str:
    """Get the active queue for a player (resolves grouped players).

    Args:
        player_id: The player ID.
    """
    result = await _call_ma("player_queues/get_active_queue", {"player_id": player_id})
    return json.dumps(result, default=str)


# =========================================================================
#  PLAYER QUEUES — Playback Control
# =========================================================================


@mcp.tool
async def queue_command_play(queue_id: str) -> str:
    """Start playback on a queue.

    Args:
        queue_id: The queue ID.
    """
    await _call_ma("player_queues/play", {"queue_id": queue_id})
    return json.dumps({"status": "ok", "queue_id": queue_id, "action": "play"})


@mcp.tool
async def queue_command_pause(queue_id: str) -> str:
    """Pause playback on a queue.

    Args:
        queue_id: The queue ID.
    """
    await _call_ma("player_queues/pause", {"queue_id": queue_id})
    return json.dumps({"status": "ok", "queue_id": queue_id, "action": "pause"})


@mcp.tool
async def queue_command_stop(queue_id: str) -> str:
    """Stop playback on a queue.

    Args:
        queue_id: The queue ID.
    """
    await _call_ma("player_queues/stop", {"queue_id": queue_id})
    return json.dumps({"status": "ok", "queue_id": queue_id, "action": "stop"})


@mcp.tool
async def queue_command_resume(queue_id: str, fade_in: bool = False) -> str:
    """Resume playback on a queue with optional fade-in.

    Args:
        queue_id: The queue ID.
        fade_in: Whether to fade in when resuming.
    """
    await _call_ma("player_queues/resume", {"queue_id": queue_id, "fade_in": fade_in})
    return json.dumps({"status": "ok", "queue_id": queue_id, "action": "resume"})


@mcp.tool
async def queue_command_next(queue_id: str) -> str:
    """Skip to the next item in a queue.

    Args:
        queue_id: The queue ID.
    """
    await _call_ma("player_queues/next", {"queue_id": queue_id})
    return json.dumps({"status": "ok", "queue_id": queue_id, "action": "next"})


@mcp.tool
async def queue_command_previous(queue_id: str) -> str:
    """Go to the previous item in a queue.

    Args:
        queue_id: The queue ID.
    """
    await _call_ma("player_queues/previous", {"queue_id": queue_id})
    return json.dumps({"status": "ok", "queue_id": queue_id, "action": "previous"})


@mcp.tool
async def queue_command_seek(queue_id: str, position: int) -> str:
    """Seek to a position in the currently playing queue item.

    Args:
        queue_id: The queue ID.
        position: Target position in seconds.
    """
    await _call_ma("player_queues/seek", {"queue_id": queue_id, "position": position})
    return json.dumps({"status": "ok", "queue_id": queue_id, "position": position})


@mcp.tool
async def queue_command_skip(queue_id: str, seconds: int) -> str:
    """Skip forward or backward in the current queue item.

    Args:
        queue_id: The queue ID.
        seconds: Seconds to skip (positive = forward, negative = backward).
    """
    await _call_ma("player_queues/skip", {"queue_id": queue_id, "seconds": seconds})
    return json.dumps({"status": "ok", "queue_id": queue_id, "skipped": seconds})


# =========================================================================
#  PLAYER QUEUES — Queue Settings
# =========================================================================


@mcp.tool
async def queue_command_shuffle(queue_id: str, shuffle_enabled: bool) -> str:
    """Enable or disable shuffle on a queue.

    Args:
        queue_id: The queue ID.
        shuffle_enabled: True to shuffle, False for sequential playback.
    """
    await _call_ma("player_queues/shuffle", {"queue_id": queue_id, "shuffle_enabled": shuffle_enabled})
    return json.dumps({"status": "ok", "queue_id": queue_id, "shuffle": shuffle_enabled})


@mcp.tool
async def queue_command_repeat(queue_id: str, repeat_mode: str) -> str:
    """Set the repeat mode on a queue.

    Args:
        queue_id: The queue ID.
        repeat_mode: One of: 'off', 'one', 'all'.
    """
    await _call_ma("player_queues/repeat", {"queue_id": queue_id, "repeat_mode": repeat_mode})
    return json.dumps({"status": "ok", "queue_id": queue_id, "repeat": repeat_mode})


# =========================================================================
#  PLAYER QUEUES — Queue Manipulation
# =========================================================================


@mcp.tool
async def queue_command_clear(queue_id: str) -> str:
    """Clear all items from a queue.

    Args:
        queue_id: The queue ID.
    """
    await _call_ma("player_queues/clear", {"queue_id": queue_id})
    return json.dumps({"status": "ok", "queue_id": queue_id, "action": "cleared"})


@mcp.tool
async def queue_command_move_item(
    queue_id: str,
    queue_item_id: str,
    pos_shift: int = 0,
) -> str:
    """Move an item within a queue.

    Args:
        queue_id: The queue ID.
        queue_item_id: The queue item ID to move.
        pos_shift: Positions to move (positive=down, negative=up, 0=move to next).
    """
    await _call_ma(
        "player_queues/move_item",
        {"queue_id": queue_id, "queue_item_id": queue_item_id, "pos_shift": pos_shift},
    )
    return json.dumps({"status": "ok", "queue_id": queue_id, "moved": queue_item_id})


@mcp.tool
async def queue_command_delete(
    queue_id: str,
    item_id_or_index: str | int,
) -> str:
    """Delete an item from a queue by ID or index.

    Args:
        queue_id: The queue ID.
        item_id_or_index: Queue item ID (string) or index position (integer).
    """
    await _call_ma(
        "player_queues/delete_item",
        {"queue_id": queue_id, "item_id_or_index": item_id_or_index},
    )
    return json.dumps({"status": "ok", "queue_id": queue_id, "deleted": str(item_id_or_index)})


# =========================================================================
#  PLAYER QUEUES — Media Playback
# =========================================================================


@mcp.tool
async def play_media(
    queue_id: str,
    media: str | list[str],
    option: str = "play",
    radio_mode: bool = False,
    start_item: str | None = None,
) -> str:
    """Play media on a player queue. This is the main way to start playing music.

    Args:
        queue_id: The queue/player ID to play on.
        media: URI(s) to play. Can be a single URI string or list of URIs.
            Examples: 'spotify://track/abc', 'library://album/1', a share URL.
        option: Queue option - 'play' (replace queue), 'replace' (replace queue),
            'next' (play next), 'replace_next' (replace upcoming), 'add' (append to end).
        radio_mode: Enable radio mode (auto-generate similar tracks after queue ends).
        start_item: When playing a collection, start from this specific item URI.
    """
    args: dict[str, Any] = {
        "queue_id": queue_id,
        "media": media if isinstance(media, list) else [media],
        "option": option,
        "radio_mode": radio_mode,
    }
    if start_item:
        args["start_item"] = start_item
    await _call_ma("player_queues/play_media", args)
    return json.dumps({"status": "ok", "queue_id": queue_id, "media": media, "option": option})


@mcp.tool
async def play_index(
    queue_id: str,
    index: int | str,
) -> str:
    """Play a specific item in the queue by index or queue_item_id.

    Args:
        queue_id: The queue ID.
        index: Zero-based queue position (int) or a queue_item_id (string).
    """
    await _call_ma("player_queues/play_index", {"queue_id": queue_id, "index": index})
    return json.dumps({"status": "ok", "queue_id": queue_id, "index": index})


@mcp.tool
async def transfer_queue(
    source_queue_id: str,
    target_queue_id: str,
    auto_play: bool | None = None,
) -> str:
    """Transfer a playing queue from one player to another.

    Args:
        source_queue_id: The source queue/player ID.
        target_queue_id: The target queue/player ID.
        auto_play: Automatically start playing on target (default True).
    """
    args: dict[str, Any] = {
        "source_queue_id": source_queue_id,
        "target_queue_id": target_queue_id,
    }
    if auto_play is not None:
        args["auto_play"] = auto_play
    await _call_ma("player_queues/transfer", args)
    return json.dumps({"status": "ok", "from": source_queue_id, "to": target_queue_id})


# =========================================================================
#  CONFIGURATION — Players
# =========================================================================


@mcp.tool
async def get_player_config(player_id: str) -> str:
    """Get the configuration for a specific player.

    Args:
        player_id: The player ID.
    """
    result = await _call_ma("config/players/get", {"player_id": player_id})
    return json.dumps(result, default=str)


@mcp.tool
async def save_player_config(player_id: str, values: dict[str, Any]) -> str:
    """Save configuration values for a player.

    Args:
        player_id: The player ID.
        values: Dictionary of setting names to values (e.g. {'crossfade': true}).
    """
    result = await _call_ma(
        "config/players/save",
        {"player_id": player_id, "values": values},
    )
    return json.dumps(result, default=str)


@mcp.tool
async def get_player_configs() -> str:
    """Get configuration for all players."""
    result = await _call_ma("config/players/all")
    return json.dumps(_compact(result), default=str)


# =========================================================================
#  CONFIGURATION — Providers
# =========================================================================


@mcp.tool
async def get_provider_configs() -> str:
    """Get configuration for all music/player providers."""
    result = await _call_ma("config/providers")
    return json.dumps(_compact(result), default=str)


@mcp.tool
async def get_provider_config(instance_id: str) -> str:
    """Get configuration for a specific provider.

    Args:
        instance_id: The provider instance ID.
    """
    result = await _call_ma("config/providers/get", {"instance_id": instance_id})
    return json.dumps(result, default=str)


@mcp.tool
async def save_provider_config(
    instance_id: str,
    values: dict[str, Any],
) -> str:
    """Save configuration values for a provider.

    Args:
        instance_id: The provider instance ID.
        values: Dictionary of setting names to values.
    """
    result = await _call_ma(
        "config/providers/save",
        {"instance_id": instance_id, "values": values},
    )
    return json.dumps(result, default=str)


@mcp.tool
async def reload_provider(instance_id: str) -> str:
    """Reload a provider (restart it without changing config).

    Args:
        instance_id: The provider instance ID.
    """
    await _call_ma("config/providers/reload", {"instance_id": instance_id})
    return json.dumps({"status": "ok", "instance_id": instance_id, "action": "reloaded"})


@mcp.tool
async def remove_provider_config(instance_id: str) -> str:
    """Remove a provider configuration entirely.

    Args:
        instance_id: The provider instance ID.
    """
    await _call_ma("config/providers/remove", {"instance_id": instance_id})
    return json.dumps({"status": "ok", "instance_id": instance_id, "action": "removed"})


# =========================================================================
#  CONFIGURATION — Core
# =========================================================================


@mcp.tool
async def get_core_configs() -> str:
    """Get all core system configuration settings."""
    result = await _call_ma("config/core")
    return json.dumps(result, default=str)


@mcp.tool
async def save_core_config(domain: str, values: dict[str, Any]) -> str:
    """Save core system configuration values.

    Args:
        domain: The core config domain (e.g. 'streams', 'players', 'metadata').
        values: Dictionary of setting names to values.
    """
    result = await _call_ma("config/core/save", {"domain": domain, "values": values})
    return json.dumps(result, default=str)


# =========================================================================
#  Entrypoint
# =========================================================================

if __name__ == "__main__":
    mcp.run(transport="stdio")
