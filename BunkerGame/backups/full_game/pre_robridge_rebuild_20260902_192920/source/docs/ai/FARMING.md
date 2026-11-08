# Farming System

## Evidence status

Partially confirmed. Requires a full server and client protocol analysis.

## Known source files

- `src/server/FarmingSystem.server.lua`
- `src/client/FarmingUI.client.lua`

## Confirmed server observations

A previous inspection reported:

- Source length: 245 lines
- No `require()` calls found
- No `RemoteFunction` found
- RemoteEvents:
  - `UpdateUI`
  - `Notify`
  - `UpdateProgress`
- Reported top-level functions:
  - `setupPlayer`
  - `ensurePlots`
  - `ensureProcessor`
  - `getState`
  - `setState`
  - `pushUI`
  - `notify`

These observations must be revalidated against the current source before being treated as current truth.

## Client behavior

Unknown pending full inspection of `src/client/FarmingUI.client.lua`.

## State model

Unknown pending evidence-based analysis.

## Networking contract

Document confirmed payload schemas in `NETWORKING.md`.

## Risks

Unknown pending review.

## Tests

See `TESTING.md`.
