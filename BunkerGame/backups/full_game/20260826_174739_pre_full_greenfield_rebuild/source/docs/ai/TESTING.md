# Testing Strategy

## Automated validation

Where practical, validate:

- Luau syntax
- Static diagnostics
- Rojo mapping integrity
- Module require paths
- Remote payload validation
- State transitions

## Manual Roblox Studio checks

### Farming

- Player initialization
- Planting
- Growth
- Harvesting
- Processing
- UI synchronization
- Progress updates
- Player reset and rejoin
- Multiple-player isolation

### Networking

- Invalid types
- Missing arguments
- Out-of-range values
- Spam
- Invalid Instance arguments
- Requests from incorrect state
- Requests from excessive distance

### Lifecycle

- Player leaves during an operation
- Character respawns
- Relevant Instance is destroyed
- Server shutdown
- Multiple simultaneous players

## Regression template

For each code change record:

1. Changed behavior
2. Expected result
3. Test setup
4. Test steps
5. Observed result
6. Remaining risks
