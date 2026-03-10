import os
import sys
import click
import ROOT
import sifca_utils

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Utils import utils as u
from Utils import plot_functions as pf
from Resolution_study import correlation_2ETROC as corr

sifca_utils.plotting.set_sifca_style()
ROOT.gROOT.SetBatch(False)

@click.command()
@click.argument("k3", type=click.Path(exists=True))
@click.argument("k2", type=click.Path(exists=True))
@click.option("--outdir", default="Resolution_Plots", help="Output directory.", type=str)
@click.option("--apply-cal-cut/--no-apply-cal-cut", default=True, show_default=True, help="Apply per-pixel cal cut using the most frequent cal in each pixel.")
@click.option("--choose-nhits-ev", default="unique", type=click.Choice(["max_tot", "first", "unique"]), show_default=True)
@click.option("--beam-pix-k2", type=(float, float), default=None, help="Beam center pixel for K2 as (col,row)")
@click.option("--beam-pix-k3", type=(float, float), default=None,help="Beam center pixel for K3 as (col,row)")
def main(k3, k2, outdir, apply_cal_cut, choose_nhits_ev, beam_pix_k2, beam_pix_k3):

    run_name_k3 = os.path.splitext(os.path.basename(k3))[0]
    run_name_k2 = os.path.splitext(os.path.basename(k2))[0]

    if run_name_k2 != run_name_k3:
        raise ValueError("K2 and K3 files do not correspond to the same run")

    run_name = run_name_k3

    run_outdir = os.path.join(outdir, run_name)
    os.makedirs(run_outdir, exist_ok=True)

    k2_outdir = os.path.join(outdir, "K2", run_name)
    k3_outdir = os.path.join(outdir, "K3", run_name)
    os.makedirs(k2_outdir, exist_ok=True)
    os.makedirs(k3_outdir, exist_ok=True)

    out_root = os.path.join(run_outdir, "ResolutionPlots.root")
    matched_root = os.path.join(run_outdir, "MatchedHits.root")

    fout = ROOT.TFile(out_root, "RECREATE")

    print(f"[INFO] Reading K2: {k2}")
    df_k2 = ROOT.RDataFrame("Hits", k2)

    if apply_cal_cut:
        cut_k2 = u.get_cal_pixel_cut(df_k2)
        print("[INFO] Applying per-pixel CAL cut based on most frequent CAL for K2")
        if cut_k2:
            df_k2 = df_k2.Filter(cut_k2)

    df_k2 = u.compute_t(df_k2)

    print(f"[INFO] Reading K3: {k3}")
    df_k3 = ROOT.RDataFrame("Hits", k3)
    if apply_cal_cut:
        cut_k3 = u.get_cal_pixel_cut(df_k3)
        print("[INFO] Applying per-pixel CAL cut based on most frequent CAL for K3")
        if cut_k3:
            df_k3 = df_k3.Filter(cut_k3)

    df_k3 = u.compute_t(df_k3)

    if beam_pix_k2 is None:
        col_k2, row_k2 = u.beam_center_from_gaussian(df_k2, "K2")
    else:
        col_k2, row_k2 = beam_pix_k2

    if beam_pix_k3 is None:
        col_k3, row_k3 = u.beam_center_from_gaussian(df_k3, "K3")
    else:
        col_k3, row_k3 = beam_pix_k3

    pix_k2 = (col_k2, row_k2)
    pix_k3 = (col_k3, row_k3)

    print(f"[INFO] Beam center pixel K2: {pix_k2}")
    print(f"[INFO] Beam center pixel K3: {pix_k3}")

    print(f"[INFO] Building hit map K2 with choose='{choose_nhits_ev}'")
    map_k2 = corr.build_hit_map(df_k2, choose=choose_nhits_ev)

    print(f"[INFO] Building hit map K3 with choose='{choose_nhits_ev}'")
    map_k3 = corr.build_hit_map(df_k3, choose=choose_nhits_ev)

    dcol0 = int(round(pix_k2[0] - pix_k3[0]))
    drow0 = int(round(pix_k2[1] - pix_k3[1]))
    print(f"[ALIGN] dcol0={dcol0} drow0={drow0}")

    map_k2_aligned = u.apply_pixel_alignment_to_map(map_k2, dcol0, drow0)

    name_k2 = os.path.splitext(os.path.basename(k2))[0]
    name_k3 = os.path.splitext(os.path.basename(k3))[0]

    cut_label = "calcut" if apply_cal_cut else "nocut"

    # pf.plot_cal_1d(df_k2, f"{name_k2}_{cut_label}", k2_outdir)
    # pf.plot_toa_1d(df_k2, f"{name_k2}_{cut_label}", k2_outdir)
    # pf.plot_tot_1d(df_k2, f"{name_k2}_{cut_label}", k2_outdir)
    # pf.plot_ToA_vs_CAL(df_k2, f"{name_k2}_toa_vs_cal_{cut_label}", k2_outdir)
    # pf.plot_toa_vs_tot(df_k2, f"{name_k2}_cal_{cut_label}", k2_outdir)

    # pf.plot_cal_1d(df_k3, f"{name_k3}_{cut_label}", k3_outdir)
    # pf.plot_toa_1d(df_k3, f"{name_k3}_{cut_label}", k3_outdir)
    # pf.plot_tot_1d(df_k3, f"{name_k3}_{cut_label}", k3_outdir)
    # pf.plot_ToA_vs_CAL(df_k3, f"{name_k3}_toa_vs_cal_{cut_label}", k3_outdir)
    # pf.plot_toa_vs_tot(df_k3, f"{name_k3}_cal_{cut_label}", k3_outdir)

    common_ids = corr.join_maps_by_event_id(map_k3, map_k2_aligned)
    print(f"[INFO] Matched events: {len(common_ids)}")

    corr.build_matched_tree(common_ids, map_k3, map_k2_aligned, matched_root)

    df_match = ROOT.RDataFrame("MatchedHits", matched_root)

    corr.plot_tot_correlation(df_match, run_outdir, name="ToT_corr", fout=fout)
    corr.plot_toa_correlation(df_match, run_outdir, name="ToA_corr", fout=fout)
    corr.plot_delta_toa(df_match, run_outdir, name="deltaToA", fout=fout)
    corr.plot_colrow_corr(df_match, run_outdir, name="colrow_corr", fout=fout)

    corr.plot_tot_overlay(df_match, run_outdir, name="ToT_overlay", fout=fout)
    corr.plot_event_by_event_pixel_shift(df_match, run_outdir, name="pixel_shift_evt", fout=fout)

    # corr.compute_costheta_hist(df_match, dz_mm=90.0, pitch_mm=1.3, outdir=run_outdir, name="costheta_after_alignment", fout=fout)
    corr.compare_theta_methods(df_match, pitch_mm=1.3, z_cm=9.0, outdir=run_outdir, name="angles", fout=fout)

    input("Done. Press Enter to exit...")

    fout.Close()
    print(f"[INFO] ROOT saved in: {out_root}")
    print(f"[INFO] Matched ROOT saved in: {matched_root}")


if __name__ == "__main__":
    main()