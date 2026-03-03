import os
import sys
import click
import ROOT
import sifca_utils

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Utils import utils as u  # noqa

from Resolution_study import toa_vs_tot as ttv
from Resolution_study import correlation_event_num as corr

sifca_utils.plotting.set_sifca_style()
ROOT.gROOT.SetBatch(False)           # fuerza modo interactivo
ROOT.gStyle.SetOptStat(0)


def most_hit_pixel(df):
    arr = df.AsNumpy(["col", "row"])
    counts = {}
    for c, r in zip(arr["col"], arr["row"]):
        key = (int(c), int(r))
        counts[key] = counts.get(key, 0) + 1

    if not counts:
        raise RuntimeError("[ERROR] No hits in dataframe to determine most_hit_pixel().")

    max_pixel = max(counts, key=counts.get)
    print(f"[INFO] Max pixel: col={max_pixel[0]} row={max_pixel[1]} hits={counts[max_pixel]}")
    return max_pixel


def build_hit_map(df, choose="max_tot"):
    """
    Map: event_number -> (ToA, ToT, cal, col, row)
    """ 

    arr = df.AsNumpy(["event_number", "ToA", "ToT", "cal", "col", "row"])

    m = {}
    n = len(arr["event_number"])
    for i in range(n):
        ev = int(arr["event_number"][i])
        toa = float(arr["ToA"][i])
        tot = float(arr["ToT"][i])
        cal = int(arr["cal"][i])
        col = int(arr["col"][i])
        row = int(arr["row"][i])

        if ev not in m:
            m[ev] = (toa, tot, cal, col, row)
        else:
            if choose == "max_tot":
                if tot > m[ev][1]:
                    m[ev] = (toa, tot, cal, col, row)
            elif choose == "first":
                pass
            else:
                raise ValueError(f"Unknown choose mode: {choose}")

    return m


@click.command()
@click.argument("root1", type=click.Path(exists=True))
@click.argument("root2", type=click.Path(exists=True))
@click.option("--outdir", default="Resolution_Plots", type=str)
def main(root1, root2, outdir):
    os.makedirs(outdir, exist_ok=True)
    keep = {"canv": [], "objs": []}

    # ---- FILE 1 ----
    print(f"[INFO] Reading 1: {root1}")
    df1 = ROOT.RDataFrame("Hits", root1)
    pix1 = most_hit_pixel(df1)
    max_cal1, *_rest1, base_cut1, cal_cut1 = ttv.get_cuts_and_cal_info(df1)
    # cut1_pix = f"({cal_cut1}) && (col == {pix1[0]}) && (row == {pix1[1]})"
    cut1_pix = cal_cut1
    df1 = ttv.compute_t(root1, cut=cut1_pix)

    m1 = build_hit_map(df1, choose="max_tot")
    print(f"[INFO] File1 entries (after cut): {len(m1)}")
    print(f"[INFO] File1 max_cal={max_cal1}  max-pixel={pix1}")

    name1 = os.path.basename(root1).replace(".root", "")

    # ttv.plot_cal_1d(df1, name1, outdir)
    # input("Press Enter to continue...")

    # ttv.plot_toa_1d(df1, name1, outdir)
    # input("Press Enter to continue...")

    # ttv.plot_toa_vs_cal_2d(df1, f"{name1}_toa_vs_cal", outdir)
    # input("Press Enter to continue...")

    # ttv.plot_toa_vs_tot_2d(df1, f"{name1}_cal", outdir)
    # input("Press Enter to continue...")

    # ---- FILE 2 ----
    print(f"[INFO] ------------------------------")
    print(f"[INFO] Reading 2: {root2}")
    df2 = ROOT.RDataFrame("Hits", root2)
    pix2 = most_hit_pixel(df2)

    max_cal2, *_rest2, base_cut2, cal_cut2 = ttv.get_cuts_and_cal_info(df2)
    # cut2_pix = f"({cal_cut2}) && (col == {pix2[0]}) && (row == {pix2[1]})"
    cut2_pix = cal_cut2
    df2 = ttv.compute_t(root2, cut=cut2_pix)

    m2 = build_hit_map(df2, choose="max_tot")
    print(f"[INFO] File2 entries (after cut): {len(m2)}")
    print(f"[INFO] File2 max_cal={max_cal2}  max-pixel={pix2}")

    name2 = os.path.basename(root2).replace(".root", "")

    # ttv.plot_cal_1d(df2, name2, outdir)
    # input("Press Enter to continue...")

    # ttv.plot_toa_1d(df2, name2, outdir)
    # input("Press Enter to continue...")

    # ttv.plot_toa_vs_cal_2d(df2, f"{name2}_toa_vs_cal", outdir)
    # input("Press Enter to continue...")

    # ttv.plot_toa_vs_tot_2d(df2, f"{name2}_calpeak", outdir)
    # input("Press Enter to continue...")


    # -------------------------------
    # CORRELATIONS 
    # -------------------------------
    common = corr.matched_events(m1, m2)
    print(f"[INFO] Matched event_number: {len(common)}")

    corr.plot_tot_correlation_2d(common, m1, m2, outdir, name="ToT_run1_vs_run2")
    input("Press Enter to continue...")

    corr.plot_tot_overlay_1d(common, m1, m2, outdir, name="ToT_overlay")
    input("Press Enter to continue...")

    corr.plot_colrow_correlations_2d(common, m1, m2, outdir, name="colrow_corr")
    input("Press Enter to continue...")

    corr.plot_delta_toa_with_fit(
        common, m1, m2, outdir,
        base1=name1, base2=name2,
        name="deltaToA"
    )

    input("Done. Press Enter to exit...")


if __name__ == "__main__":
    main()