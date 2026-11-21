"""Idea2World 7.0 pluggable generation engines.

Each engine wraps one of the user's chosen tools (BloxMaps, Meshy, BloxUI, plus the local
procedural builder that 6.0 already ships). An engine either did real work or it did not, and it
always says which. The orchestrator picks an engine per concern (world, assets, UI) and reports
it; nothing here fakes a result it did not produce.
"""
