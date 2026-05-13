# Music Assistant MCP Server

A [FastMCP](https://gofastmcp.com/) server that exposes the full [Music Assistant](https://www.music-assistant.io/) API as **95 MCP tools** — giving any MCP-compatible AI client (Claude, Cursor, Claude Code, etc.) complete control over your music library, players, queues, and configuration.

## Features

**95 tools** organized across 7 categories:

| Category | Tools | Examples |
|---|---|---|
| **Tracks** | 5 | Library listing, details, versions, albums, preview URLs |
| **Albums** | 4 | Library listing, details, track lists, versions |
| **Artists** | 4 | Library listing, details, top tracks, discography |
| **Playlists** | 6 | List, create, get tracks, add/remove tracks |
| **Podcasts & Audiobooks** | 5 | Library listing, details, episodes |
| **Radio** | 3 | Library listing, details, versions |
| **Search & Discovery** | 5 | Global search, browse, recently played, in-progress, recommendations |
| **Item Management** | 8 | Get by URI, favorites, library add/remove, mark played/unplayed, refresh |
| **Sync** | 2 | Start sync, get running tasks |
| **Players** | 18 | List, play/pause/stop, volume, power, mute, seek, grouping, announcements |
| **Player Queues** | 16 | List items, play/pause/stop/resume, next/prev, seek, shuffle, repeat, clear, move, delete, play media, transfer |
| **Configuration** | 9 | Player config, provider config, core config (get/save/reload/remove) |

## Prerequisites

- A running **Music Assistant** server (v2.7+ recommended for full API support)
- An **authentication token** (create one in MA web UI → Profile → Long-Lived Tokens)

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/music-assistant-mcp.git
cd music-assistant-mcp
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your Music Assistant server URL and token
```

| Variable | Required | Description |
|---|---|---|
| `MA_URL` | Yes | Music Assistant server URL (e.g. `http://192.168.1.100:8095` or `https://ma.example.com`) |
| `MA_TOKEN` | Yes* | Long-lived auth token (*required for MA server schema ≥ 28) |

### 3. Run with Docker Compose

```bash
docker compose up -d
```

## Installation Methods

### Docker (recommended)

```bash
# Build
docker build -t music-assistant-mcp .

# Run with stdio transport (default — for MCP clients)
docker run --rm \
  -e MA_URL=http://192.168.1.100:8095 \
  -e MA_TOKEN=your_token_here \
  music-assistant-mcp

# Run with HTTP transport (for remote access)
docker run --rm \
  -e MA_URL=http://192.168.1.100:8095 \
  -e MA_TOKEN=your_token_here \
  -p 8000:8000 \
  music-assistant-mcp \
  fastmcp run server.py:mcp --transport http --host 0.0.0.0 --port 8000
```

### Python (local)

```bash
pip install fastmcp httpx

# Set environment variables
export MA_URL="http://192.168.1.100:8095"
export MA_TOKEN="your_token_here"

# Run with stdio (for MCP clients like Claude Desktop)
python server.py

# Or with HTTP transport
fastmcp run server.py:mcp --transport http --port 8000
```

## Connecting to MCP Clients

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "music-assistant": {
      "command": "python",
      "args": ["/path/to/music-assistant-mcp/server.py"],
      "env": {
        "MA_URL": "http://192.168.1.100:8095",
        "MA_TOKEN": "your_token_here"
      }
    }
  }
}
```

### Claude Desktop (Docker)

```json
{
  "mcpServers": {
    "music-assistant": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-e", "MA_URL=http://host.docker.internal:8095",
        "-e", "MA_TOKEN=your_token_here",
        "music-assistant-mcp"
      ]
    }
  }
}
```

### Claude Code

```bash
fastmcp install claude-code server.py:mcp \
  --env MA_URL=http://192.168.1.100:8095 \
  --env MA_TOKEN=your_token_here
```

### HTTP Transport (any MCP client)

Start the server with HTTP transport, then point your client at the URL:

```bash
fastmcp run server.py:mcp --transport http --port 8000
# Server available at http://localhost:8000/mcp
```

## Reverse Proxy Support

The `MA_URL` variable accepts any URL, so it works seamlessly behind a reverse proxy:

```bash
# Direct connection
MA_URL=http://192.168.1.100:8095

# Behind nginx/caddy/traefik
MA_URL=https://music.example.com

# Custom port
MA_URL=http://my-server.local:9090
```

## Usage Examples

Once connected, your AI assistant can do things like:

- *"Search for Beatles albums and play Abbey Road on the living room speaker"*
- *"What's currently playing? Skip to the next track"*
- *"Create a playlist called 'Road Trip' and add my favorite rock tracks"*
- *"Set the bedroom speaker volume to 30% and turn on shuffle"*
- *"Transfer what's playing in the kitchen to the office speaker"*
- *"Show me my recently played items"*
- *"Group the living room and kitchen speakers together"*

## Tool Reference

<details>
<summary><strong>Music Library — Tracks (5 tools)</strong></summary>

| Tool | Description |
|---|---|
| `get_library_tracks` | Get tracks from library with filtering, search, pagination |
| `get_track` | Get full details for a single track |
| `get_track_versions` | Get alternate versions across providers |
| `get_track_albums` | Get albums containing a track |
| `get_track_preview_url` | Generate a preview URL |

</details>

<details>
<summary><strong>Music Library — Albums (4 tools)</strong></summary>

| Tool | Description |
|---|---|
| `get_library_albums` | Get albums from library with filtering |
| `get_album` | Get full album details |
| `get_album_tracks` | Get all tracks in an album |
| `get_album_versions` | Get alternate versions across providers |

</details>

<details>
<summary><strong>Music Library — Artists (4 tools)</strong></summary>

| Tool | Description |
|---|---|
| `get_library_artists` | Get artists from library |
| `get_artist` | Get full artist details |
| `get_artist_tracks` | Get top/popular tracks by artist |
| `get_artist_albums` | Get albums by artist |

</details>

<details>
<summary><strong>Music Library — Playlists (6 tools)</strong></summary>

| Tool | Description |
|---|---|
| `get_library_playlists` | Get playlists from library |
| `get_playlist` | Get full playlist details |
| `get_playlist_tracks` | Get all tracks in a playlist |
| `create_playlist` | Create a new empty playlist |
| `add_playlist_tracks` | Add tracks to a playlist |
| `remove_playlist_tracks` | Remove tracks from a playlist by position |

</details>

<details>
<summary><strong>Music Library — Podcasts & Audiobooks (5 tools)</strong></summary>

| Tool | Description |
|---|---|
| `get_library_podcasts` | Get podcasts from library |
| `get_podcast` | Get full podcast details |
| `get_podcast_episodes` | Get episodes for a podcast |
| `get_library_audiobooks` | Get audiobooks from library |
| `get_audiobook` | Get full audiobook details |

</details>

<details>
<summary><strong>Music Library — Radio (3 tools)</strong></summary>

| Tool | Description |
|---|---|
| `get_library_radios` | Get radio stations from library |
| `get_radio` | Get full radio station details |
| `get_radio_versions` | Get versions across providers |

</details>

<details>
<summary><strong>Search & Discovery (5 tools)</strong></summary>

| Tool | Description |
|---|---|
| `search` | Global search across all providers and library |
| `browse` | Browse provider content hierarchically |
| `recently_played` | Get recently played items |
| `in_progress_items` | Get in-progress audiobooks/podcasts |
| `recommendations` | Get personalized recommendations |

</details>

<details>
<summary><strong>Item Management (8 tools)</strong></summary>

| Tool | Description |
|---|---|
| `get_item_by_uri` | Get item by URI or share URL |
| `get_item` | Get item by type and ID |
| `add_item_to_favorites` | Add to favorites |
| `remove_item_from_favorites` | Remove from favorites |
| `add_item_to_library` | Add to library |
| `remove_item_from_library` | Remove from library |
| `refresh_item` | Refresh metadata |
| `mark_item_played` / `mark_item_unplayed` | Track play status |

</details>

<details>
<summary><strong>Player Control (18 tools)</strong></summary>

| Tool | Description |
|---|---|
| `get_players` / `get_player` | List or get player details |
| `player_command_play` / `pause` / `stop` / `play_pause` | Basic playback |
| `player_command_next_track` / `previous_track` / `seek` | Navigation |
| `player_command_volume_set` / `volume_up` / `volume_down` / `volume_mute` | Volume |
| `player_command_power` | Power on/off |
| `set_player_group_volume` / `group_volume_up` / `group_volume_down` | Group volume |
| `player_command_group` / `ungroup` / `group_many` / `ungroup_many` | Grouping |
| `play_announcement` | Announcement playback |
| `player_command_select_source` | Input source selection |

</details>

<details>
<summary><strong>Queue Management (16 tools)</strong></summary>

| Tool | Description |
|---|---|
| `get_player_queues` / `get_player_queue_items` / `get_active_queue` | Queue info |
| `queue_command_play` / `pause` / `stop` / `resume` | Queue playback |
| `queue_command_next` / `previous` / `seek` / `skip` | Queue navigation |
| `queue_command_shuffle` / `repeat` | Playback modes |
| `queue_command_clear` / `move_item` / `delete` | Queue manipulation |
| `play_media` | Play URIs on a queue (the main playback entry point) |
| `play_index` | Play specific queue item |
| `transfer_queue` | Transfer queue between players |

</details>

<details>
<summary><strong>Configuration (9 tools)</strong></summary>

| Tool | Description |
|---|---|
| `get_player_config` / `save_player_config` / `get_player_configs` | Player settings |
| `get_provider_configs` / `get_provider_config` / `save_provider_config` | Provider settings |
| `reload_provider` / `remove_provider_config` | Provider lifecycle |
| `get_core_configs` / `save_core_config` | Core system settings |

</details>

## Architecture

```
┌─────────────────────┐     HTTP/JSON      ┌──────────────────────┐
│   MCP Client        │◄──── stdio ────────│  FastMCP Server      │
│ (Claude, Cursor,    │      or http       │  (this project)      │
│  Claude Code, etc.) │                    │  95 tools            │
└─────────────────────┘                    └──────────┬───────────┘
                                                      │
                                                POST /api
                                                      │
                                           ┌──────────▼───────────┐
                                           │  Music Assistant     │
                                           │  Server              │
                                           │  (your instance)     │
                                           └──────────────────────┘
```

## License

MIT

## Acknowledgments

- [Music Assistant](https://www.music-assistant.io/) — Open-source music library manager
- [FastMCP](https://gofastmcp.com/) — Python framework for building MCP servers
- [Model Context Protocol](https://modelcontextprotocol.io/) — The protocol that connects LLMs to tools
