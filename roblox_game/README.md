# Bunker Lobby

Rojo source for the lobby Place in the BunkerGame universe.

## Place mapping

- Lobby (`ori game zombie`): `129695090105158`
- Gameplay destination (`BunkerGame`): `72688245649120`

Only sync this project into the lobby Place. Syncing it into `BunkerGame` adds the
lobby builder and lobby UI to gameplay. The accidental copy from 2026-07-19 is
preserved, disabled, under `ServerStorage.RojoAccidentalLobbyBackup` in that Place.

## Getting Started
To build the place from scratch, use:

```bash
rojo build -o "roblox_game.rbxlx"
```

Next, open the lobby Place (`129695090105158`) in Roblox Studio and start the Rojo server:

```bash
rojo serve
```

For more help, check out [the Rojo documentation](https://rojo.space/docs).
