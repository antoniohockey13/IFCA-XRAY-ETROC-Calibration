import os
import sys
import click
import ROOT
import sifca_utils

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Utils import utils as u
from Utils import plot_functions as pf

from Resolution_study import toa_vs_tot as ttv
from Resolution_study import correlation_event_num as corr

sifca_utils.plotting.set_sifca_style()
ROOT.gROOT.SetBatch(False)


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
    event_id_ (ToA, ToT, cal, col, row)
    """ 

    arr = df.AsNumpy(["event_id_", "ToA", "ToT", "cal", "col", "row"])

    m = {}
    n = len(arr["event_id_"])
    for i in range(n):
        ev = int(arr["event_id_"][i])
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
@click.argument("k3", type=click.Path(exists=True))
@click.argument("k2", type=click.Path(exists=True))
@click.option("--outdir", default="Resolution_Plots", type=str)
def main(k3, k2, outdir):
    os.makedirs(outdir, exist_ok=True)
    out_root = os.path.join(outdir, "ResolutionPlots.root")
    fout = ROOT.TFile(out_root, "RECREATE")
    #fout = None
    # ---- FILE 1 ----
    print(f"[INFO] Reading 1: {k3}")
    df1 = ROOT.RDataFrame("Hits", k3)
    pix1 = most_hit_pixel(df1)
    max_cal1, *_rest1, base_cut1, cal_cut1 = ttv.get_cuts_and_cal_info(df1)
    # cut1_pix = f"({cal_cut1}) && (col == {pix1[0]}) && (row == {pix1[1]})"
    cut1_pix = None
    df1 = ttv.compute_t(k3, cut=cut1_pix)

    m1 = build_hit_map(df1, choose="max_tot")
    print(f"[INFO] File1 entries (after cut): {len(m1)}")
    print(f"[INFO] File1 max_cal={max_cal1}  max-pixel={pix1}")

    name1 = os.path.basename(k3).replace(".root", "")

    # ttv.plot_cal_1d(df1, f"{name1}_{cut1_pix}", outdir)
    # ttv.plot_toa_1d(df1, f"{name1}_{cut1_pix}", outdir)
    # ttv.plot_tot_1d(df1, f"{name1}_{cut1_pix}", outdir)
    # ttv.plot_toa_vs_cal_2d(df1, f"{name1}_toa_vs_cal_{cut1_pix}", outdir)
    # ttv.plot_toa_vs_tot_2d(df1, f"{name1}_cal_{cut1_pix}", outdir)

    # ---- FILE 2 ----
    print(f"[INFO] ------------------------------")
    print(f"[INFO] Reading 2: {k2}")
    df2 = ROOT.RDataFrame("Hits", k2)
    pix2 = most_hit_pixel(df2)

    max_cal2, *_rest2, base_cut2, cal_cut2 = ttv.get_cuts_and_cal_info(df2)
    # cut2_pix = f"({cal_cut2}) && (col == {pix2[0]}) && (row == {pix2[1]})"
    cut2_pix = None
    df2 = ttv.compute_t(k2, cut=cut2_pix)

    m2 = build_hit_map(df2, choose="max_tot")
    print(f"[INFO] File2 entries (after cut): {len(m2)}")
    print(f"[INFO] File2 max_cal={max_cal2}  max-pixel={pix2}")

    name2 = os.path.basename(k2).replace(".root", "")

    # ttv.plot_cal_1d(df2, f"{name2}_{cut2_pix}", outdir)
    # ttv.plot_toa_1d(df2, f"{name2}_{cut2_pix}", outdir)
    # ttv.plot_tot_1d(df2, f"{name2}_{cut2_pix}", outdir)
    # ttv.plot_toa_vs_cal_2d(df2, f"{name2}_toa_vs_cal_{cut2_pix}", outdir)
    # ttv.plot_toa_vs_tot_2d(df2, f"{name2}_cal_{cut2_pix}", outdir)


    # ---- CORRELATIONS ----
    pf.hit_map(df1) 
    pf.hit_map(df2) 

    common = corr.matched_events(m1, m2)
    print(f"[INFO] Matched event_id_: {len(common)}")

    # corr.plot_tot_correlation_2d(common, m1, m2, outdir, name=f"ToT_run1_vs_run2_{cut1_pix}", fout = fout)
    # corr.plot_tot_overlay_1d(common, m1, m2, outdir, name=f"ToT_overlay_{cut1_pix}", fout = fout)
    # corr.plot_colrow_correlations_2d(common, m1, m2, outdir, name=f"colrow_corr_{cut1_pix}", fout = fout)
    # corr.plot_delta_toa_with_fit(common, m1, m2, outdir, base1=name1, base2=name2, name=f"deltaToA_{cut1_pix}", fout = fout)
    # input("Done. Press Enter to exit...")

    if fout is not None:
        fout.Close()
        print(f"[INFO] ROOT saved in: {out_root}")

if __name__ == "__main__":
    main()