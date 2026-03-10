import math
from Resolution_study import correlation_2ETROC as crr



def debug_alignment(m1, m2, delta, n=10):
    """
    Print first n aligned events between K3 (m1) and K2 (m2).
    Shows event numbers and some hit info.
    """

    common = matched_events_shifted(m1, m2, delta)

    print("\n[DEBUG] ---- Alignment preview ----")
    print(f"[DEBUG] delta = {delta}")
    print(f"[DEBUG] total matched = {len(common)}")
    print(f"[DEBUG] showing first {n} matches\n")

    for ev in common[:n]:

        ev2 = ev + delta

        toa1, tot1, cal1, col1, row1, *_ = m1[ev]
        toa2, tot2, cal2, col2, row2, *_ = m2[ev2]

        print(
            f"K3 ev={ev:8d}  col,row=({col1},{row1})  tot={tot1:6.2f} | "
            f"K2 ev={ev2:8d}  col,row=({col2},{row2})  tot={tot2:6.2f}"
        )

    print("[DEBUG] --------------------------------\n")


def debug_spot_distance(common, m1, m2, label1="K3", label2="K2"):
    """
    Determine the most frequent (col,row) spot in matched events for each map
    and print pixel distance between the two spots.
    m1/m2: dict ev -> (toa, tot, cal, col, row)
    """
    if len(common) == 0:
        print("[WARN] No common events for spot debug.")
        return None

    def most_common_pixel(m, keys):
        counts = {}
        for ev in keys:
            col = int(m[ev][3])
            row = int(m[ev][4])
            key = (col, row)
            counts[key] = counts.get(key, 0) + 1
        best = max(counts, key=counts.get)
        return best, counts[best], counts

    p1, n1, _ = most_common_pixel(m1, common)
    p2, n2, _ = most_common_pixel(m2, common)

    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dr = math.sqrt(dx * dx + dy * dy)

    print("[DEBUG] Spot (most frequent pixel) from matched events")
    print(f"  {label1}: col={p1[0]} row={p1[1]}  counts={n1}")
    print(f"  {label2}: col={p2[0]} row={p2[1]}  counts={n2}")
    print(f"  Pixel shift: dx={dx}, dy={dy}, distance={dr:.3f} px")

    return {"spot1": p1, "spot2": p2, "dx": dx, "dy": dy, "dr": dr}


def debug_matched_events(m1, m2, n=10):
    k1 = sorted(m1.keys())
    k2 = sorted(m2.keys())
    common = sorted(set(k1) & set(k2))

    print("========== DEBUG matched_events ==========")
    print(f"[DBG] m1 events: {len(k1)}")
    print(f"[DBG] m2 events: {len(k2)}")
    print(f"[DBG] common   : {len(common)}")

    if k1:
        print(f"[DBG] m1 range: {k1[0]} .. {k1[-1]}")
        print(f"[DBG] m1 first {n}: {k1[:n]}")
        print(f"[DBG] m1 last  {n}: {k1[-n:]}")
    else:
        print("[DBG] m1 is EMPTY")

    if k2:
        print(f"[DBG] m2 range: {k2[0]} .. {k2[-1]}")
        print(f"[DBG] m2 first {n}: {k2[:n]}")
        print(f"[DBG] m2 last  {n}: {k2[-n:]}")
    else:
        print("[DBG] m2 is EMPTY")

    if common:
        print(f"[DBG] common range: {common[0]} .. {common[-1]}")
        print(f"[DBG] common first {n}: {common[:n]}")
        print(f"[DBG] common last  {n}: {common[-n:]}")
    else:
        print("[DBG] common is EMPTY")

    only1 = sorted(set(k1) - set(k2))
    only2 = sorted(set(k2) - set(k1))

    print(f"[DBG] in m1 not in m2: {len(only1)}")
    print(f"[DBG] in m2 not in m1: {len(only2)}")
    if only1:
        print(f"[DBG] m1-only first {n}: {only1[:n]}")
    if only2:
        print(f"[DBG] m2-only first {n}: {only2[:n]}")

    if k1:
        hit = sum(1 for x in k1[:n] if x in set(common))
        print(f"[DBG] of first {n} m1 events, {hit} are in common")
    if k2:
        hit = sum(1 for x in k2[:n] if x in set(common))
        print(f"[DBG] of first {n} m2 events, {hit} are in common")

    print("=========================================")
    return common


def find_best_event_offset(m1, m2, delta_min=-5000, delta_max=5000, step=1, sample=200000):
    """
    Find delta that maximizes matches between event numbers:
      match if (ev in m1) and (ev+delta in m2)
    If K3 goes before K2, you expect delta > 0 (K2 = K3 + delta).
    """
    k1 = sorted(m1.keys())
    k2set = set(m2.keys())

    if sample is not None and len(k1) > sample:
        stride = max(1, len(k1) // sample)
        k1s = k1[::stride]
    else:
        k1s = k1

    best_delta = None
    best_count = -1
    counts = {}

    for d in range(delta_min, delta_max + 1, step):
        c = 0
        for ev in k1s:
            if (ev + d) in k2set:
                c += 1
        counts[d] = c
        if c > best_count:
            best_count = c
            best_delta = d

    print(f"[OFFSET] best delta = {best_delta} with {best_count} matches in sample (sample={len(k1s)})")

    top = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:10]
    print("[OFFSET] top deltas:", top)

    return best_delta, counts


def find_best_event_offset_by_toa(
    m1, m2,
    delta_min=-5000, delta_max=5000, step=1,
    sample=None,
    min_matches=5000,
    metric="mad",
    T_WINDOW=12.5,
    spot1=None, spot2=None, w=1,
    tot_min=None, tot_max=None,
    dtot_max=None
):
    """
    Busca delta que minimiza la dispersión de ΔToA (circular) entre eventos emparejados.
    m1/m2: ev -> (toa, tot, cal, col, row)
    """
    k2set = set(m2.keys())

    ev_candidates = []
    for ev, (toa1, tot1, cal1, col1, row1, *_rest_) in m1.items():
        if spot1 is not None:
            if abs(col1 - spot1[0]) > w or abs(row1 - spot1[1]) > w:
                continue

        if tot_min is not None and tot1 < tot_min:
            continue
        if tot_max is not None and tot1 > tot_max:
            continue

        ev_candidates.append(ev)

    if sample is not None and len(ev_candidates) > sample:
        ev_candidates = random.sample(ev_candidates, sample)

    best_delta = None
    best_score = float("inf")
    best_n = 0
    scores = {}

    for d in range(delta_min, delta_max + 1, step):
        diffs = []

        for ev in ev_candidates:
            ev2 = ev + d
            if ev2 not in k2set:
                continue

            toa1, tot1, _cal1, col1, row1, *_ = m1[ev]
            toa2, tot2, _cal2, col2, row2, *_ = m2[ev2]

            if spot2 is not None:
                if abs(col2 - spot2[0]) > w or abs(row2 - spot2[1]) > w:
                    continue

            if tot_min is not None and tot2 < tot_min:
                continue
            if tot_max is not None and tot2 > tot_max:
                continue

            if dtot_max is not None:
                if abs(tot1 - tot2) > dtot_max:
                    continue

            dt = circular_dt(toa1, toa2, T=T_WINDOW)
            diffs.append(dt)

        n = len(diffs)
        if n < min_matches:
            scores[d] = (float("inf"), n)
            continue

        if metric == "std":
            mu = sum(diffs) / n
            var = sum((x - mu) ** 2 for x in diffs) / n
            score = math.sqrt(var)
        elif metric == "mad":
            diffs_sorted = sorted(diffs)
            med = diffs_sorted[n // 2]
            absdev = sorted(abs(x - med) for x in diffs)
            mad = absdev[n // 2]
            score = 1.4826 * mad
        else:
            raise ValueError("metric must be 'std' or 'mad'")

        scores[d] = (score, n)

        if score < best_score:
            best_score = score
            best_delta = d
            best_n = n

    top = sorted(
        [(d, sc, n) for d, (sc, n) in scores.items() if math.isfinite(sc)],
        key=lambda x: x[1]
    )[:10]

    print(f"[OFFSET-TOA] best delta = {best_delta}  score={best_score:.6f} ns  matches={best_n}  (used={len(ev_candidates)})")
    print("[OFFSET-TOA] top deltas (delta, score_ns, matches):", top)

    return best_delta, scores

def filter_common_by_spot_and_tot(common, m1, m2,
                                 spot1, spot2,
                                 w=1,
                                 tot_min=None, tot_max=None,
                                 dtot_max=None):
    """
    common: lista de event_number presentes en ambos (o alineados)
    m1/m2: ev -> (toa, tot, cal, col, row)

    spot1/spot2: (col,row) esperados (K3/K2)
    w: ventana en pixeles (manhattan en col/row)
    tot_min/tot_max: cuts opcionales en ToT (en ns)
    dtot_max: cut opcional en |ToT1-ToT2|
    """
    out = []
    for ev in common:
        toa1, tot1, cal1, c1, r1, *_ = m1[ev]
        toa2, tot2, cal2, c2, r2, *_ = m2[ev]

        # --- spot gate ---
        if abs(int(c1) - spot1[0]) > w or abs(int(r1) - spot1[1]) > w:
            continue
        if abs(int(c2) - spot2[0]) > w or abs(int(r2) - spot2[1]) > w:
            continue

        # --- tot range gate ---
        if tot_min is not None and (tot1 < tot_min or tot2 < tot_min):
            continue
        if tot_max is not None and (tot1 > tot_max or tot2 > tot_max):
            continue

        # --- tot similarity gate ---
        if dtot_max is not None and abs(float(tot1) - float(tot2)) > dtot_max:
            continue

        out.append(ev)

    return sorted(out)

def debug_spot_distance(common, m1, m2, label1="K3", label2="K2"):
    """
    Determine the most frequent (col,row) spot in matched events for each map
    and print pixel distance between the two spots.
    m1/m2: dict ev -> (toa, tot, cal, col, row)
    """
    if len(common) == 0:
        print("[WARN] No common events for spot debug.")
        return None

    def most_common_pixel(m, keys):
        counts = {}
        for ev in keys:
            col = int(m[ev][3])
            row = int(m[ev][4])
            key = (col, row)
            counts[key] = counts.get(key, 0) + 1
        best = max(counts, key=counts.get)
        return best, counts[best], counts

    p1, n1, _ = most_common_pixel(m1, common)
    p2, n2, _ = most_common_pixel(m2, common)

    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dr = math.sqrt(dx*dx + dy*dy)

    print("[DEBUG] Spot (most frequent pixel) from matched events")
    print(f"  {label1}: col={p1[0]} row={p1[1]}  counts={n1}")
    print(f"  {label2}: col={p2[0]} row={p2[1]}  counts={n2}")
    print(f"  Pixel shift: dx={dx}, dy={dy}, distance={dr:.3f} px")

    return {"spot1": p1, "spot2": p2, "dx": dx, "dy": dy, "dr": dr}

import ROOT
import os
from Resolution_study import plot_functions_1ETROC as ttv

def plot_dtoa_vs_tot(common, m1, m2, outdir, name="dToA_vs_ToT", fout=None):
    os.makedirs(outdir, exist_ok=True)

    # X: ToT (por ejemplo K3), Y: ΔToA
    h2 = ROOT.TH2D(f"h2_{name}", f";ToT K3 [ns];#Delta ToA [ns]",
                   200, 0, 5, 200, -15, 15)
    h2.SetDirectory(0)

    for ev in common:
        toa1, tot1, *_ = m1[ev]
        toa2, tot2, *_ = m2[ev]
        dtoa = crr.circular_dt(float(toa1), float(toa2), T=12.5)
        h2.Fill(float(tot1), dtoa)

    c = ROOT.TCanvas(f"c_{name}", name)
    h2.Draw("COLZ")

    input("Press Enter to continue...")
    out_png = None
    if fout is not None:
        out_png = os.path.join(outdir, f"{name}.png")
        c.SaveAs(out_png)
        print(f"[INFO] Saved: {out_png}")

    ttv._write_to_fout(fout, h2, c)
    return out_png


def find_best_event_offset(m1, m2, delta_min=-5000, delta_max=5000, step=1, sample=200000):
    """
    Find delta that maximizes matches between event numbers:
      match if (ev in m1) and (ev+delta in m2)
    If K3 goes before K2, you expect delta > 0 (K2 = K3 + delta).
    """
    k1 = sorted(m1.keys())
    k2set = set(m2.keys())

    # sample keys from m1 to speed up
    if sample is not None and len(k1) > sample:
        stride = max(1, len(k1) // sample)
        k1s = k1[::stride]
    else:
        k1s = k1

    best_delta = None
    best_count = -1
    counts = {}

    for d in range(delta_min, delta_max + 1, step):
        c = 0
        for ev in k1s:
            if (ev + d) in k2set:
                c += 1
        counts[d] = c
        if c > best_count:
            best_count = c
            best_delta = d

    print(f"[OFFSET] best delta = {best_delta} with {best_count} matches in sample (sample={len(k1s)})")

    # show top 10 deltas
    top = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:10]
    print("[OFFSET] top deltas:", top)

    return best_delta, counts


import math
import random

def circular_dt(t1, t2, T=12.5):
    dt = t1 - t2
    return (dt + 0.5*T) % T - 0.5*T

def find_best_event_offset_by_toa(
    m1, m2,
    delta_min=-5000, delta_max=5000, step=1,
    sample=None,                 # None = usar todos
    min_matches=5000,
    metric="mad",                # "mad" recomendado
    T_WINDOW=12.5,
    # --- pre-cuts para que el offset se calcule con matches más "reales"
    spot1=None, spot2=None, w=1,
    tot_min=None, tot_max=None,
    dtot_max=None
):
    """
    Busca delta que minimiza la dispersión de ΔToA (circular) entre eventos emparejados.
    m1/m2: ev -> (toa, tot, cal, col, row)
    """

    k2set = set(m2.keys())

    # --- construir candidatos en m1 con cuts (si spot1/spot2 se dan)
    ev_candidates = []
    for ev, (toa1, tot1, cal1, col1, row1, *_rest_) in m1.items():

        # cut spot en K3
        if spot1 is not None:
            if abs(col1 - spot1[0]) > w or abs(row1 - spot1[1]) > w:
                continue

        # cut ToT K3
        if tot_min is not None and tot1 < tot_min:
            continue
        if tot_max is not None and tot1 > tot_max:
            continue

        ev_candidates.append(ev)

    # muestreo opcional
    if sample is not None and len(ev_candidates) > sample:
        ev_candidates = random.sample(ev_candidates, sample)

    best_delta = None
    best_score = float("inf")
    best_n = 0
    scores = {}

    for d in range(delta_min, delta_max + 1, step):
        diffs = []

        for ev in ev_candidates:
            ev2 = ev + d
            if ev2 not in k2set:
                continue

            toa1, tot1, _cal1, col1, row1, *_ = m1[ev]
            toa2, tot2, _cal2, col2, row2, *_ = m2[ev2]

            # cut spot en K2
            if spot2 is not None:
                if abs(col2 - spot2[0]) > w or abs(row2 - spot2[1]) > w:
                    continue

            # cut ToT K2
            if tot_min is not None and tot2 < tot_min:
                continue
            if tot_max is not None and tot2 > tot_max:
                continue

            # cut consistencia ToT
            if dtot_max is not None:
                if abs(tot1 - tot2) > dtot_max:
                    continue

            dt = circular_dt(toa1, toa2, T=T_WINDOW)
            diffs.append(dt)

        n = len(diffs)
        if n < min_matches:
            scores[d] = (float("inf"), n)
            continue

        if metric == "std":
            mu = sum(diffs) / n
            var = sum((x - mu) ** 2 for x in diffs) / n
            score = math.sqrt(var)
        elif metric == "mad":
            diffs_sorted = sorted(diffs)
            med = diffs_sorted[n // 2]
            absdev = sorted(abs(x - med) for x in diffs)
            mad = absdev[n // 2]
            score = 1.4826 * mad
        else:
            raise ValueError("metric must be 'std' or 'mad'")

        scores[d] = (score, n)

        if score < best_score:
            best_score = score
            best_delta = d
            best_n = n

    top = sorted(
        [(d, sc, n) for d, (sc, n) in scores.items() if math.isfinite(sc)],
        key=lambda x: x[1]
    )[:10]

    print(f"[OFFSET-TOA] best delta = {best_delta}  score={best_score:.6f} ns  matches={best_n}  (used={len(ev_candidates)})")
    print("[OFFSET-TOA] top deltas (delta, score_ns, matches):", top)

    return best_delta, scores
