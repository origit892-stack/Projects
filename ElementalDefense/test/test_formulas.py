#!/usr/bin/env python3
"""Formula anchor tests — GDD v3 §9/§27.2 numbers must hold exactly."""
import sys, math

def close(a, b, tol=0.01): return abs(a - b) <= tol * max(1, abs(b))

fails = []
def check(name, got, want, tol=0.01):
    if isinstance(want, (list, tuple)):
        ok = list(got) == list(want)
    else:
        ok = close(got, want, tol)
    print(f"{'PASS' if ok else 'FAIL'} {name}: got={got} want={want}")
    if not ok: fails.append(name)

# §9.1 / §9.2 — chassis cost C(N) = 100 * 1.15^N (N = floor(w/2))
for n, want in [(0,100),(1,115),(5,201),(10,405),(17,1076),(25,3292)]:
    check(f"chassisCost N={n}", round(100 * 1.15 ** n), want, tol=0.005)

# §9.1 — wave income G(w) = 150 + 35w
check("G(1)", 150 + 35, 185)
check("G(20)", 150 + 35 * 20, 850)
check("G(50)", 150 + 35 * 50, 1900)
check("cumulative G(1..50)", sum(150 + 35 * w for w in range(1, 51)), 52125)

# §2.4 / §27.2 — HP curve anchors
hp1, hp20 = 22 * 1.12 ** 0, 22 * 1.12 ** 19
hp21, hp35 = 192 * 1.2159 ** 0, 192 * 1.2159 ** 15
hp36, hp50 = 3606 * 1.16 ** 0, 3606 * 1.16 ** 15
check("HP(1)", round(hp1), 22)
check("HP(20)", round(hp20), 189, tol=0.01)
check("HP(21)", round(hp21), 192, tol=0.01)
check("HP(35)", round(hp35), 3604, tol=0.01)
check("HP(50)", round(hp50), 33411, tol=0.01)

# §8.3 — budget & count formulas
check("budget(1)", 10 + 2.4, 12.4)
check("budget(50)", 10 + 2.4 * 50, 130)
check("count(10) formula", 12 + 0.6 * 10, 18)
check("count(20) formula", 12 + 0.6 * 20, 24)
check("count(35) formula", 24 - 0.4 * 15, 18)
check("count(50) formula", 18 - 0.4 * 15, 12)

# §10.1 — deck slots
check("deck slots", 12*3 + 5*2 + 2*2 + 1*1, 51)

# §10.3 — reroll cost sequence 25 x 1.5^n
seq = [round(25 * 1.5 ** n) for n in range(4)]
check("reroll sequence", seq, [25, 38, 56, 84])

# §12.3 — tree economics
check("shards full run approx", 5*50 + 100*3 + 250 + 150, 950)  # waves + act bonuses + run complete + daily first win
check("tree total cost", (100+250+600+1200+2500) * 5, 23250)

# §7.5 — DPS model caps
check("synergy cap", min(1.75, 1 + 0.15*10 + 0.25*10), 1.75)
check("status cap", min(1.80, 1 + 0.30*10 + 0.20*10 + 0.15*10), 1.80)

# §6.3/§6.4 — corrode max 48% (4 stacks x 12%), overall armor reduction capped at 75%
check("corrode max contribution", 0.12 * 4, 0.48)
check("armorReduction overall cap", min(0.75, 0.30 + 0.12 * 4), 0.75)

# §9.4 — Reference Build feasibility anchors
check("refbuild wave50 spend < income", 49819 < 52125, 1, tol=0)  # GDD table values

if fails:
    print(f"\n{len(fails)} FORMULA FAILURES: {fails}"); sys.exit(1)
print("\nall formula anchors PASS")
