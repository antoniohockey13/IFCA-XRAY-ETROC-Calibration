import ROOT
import click
import sifca_utils
import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Utils import utils as u

sifca_utils.plotting.set_sifca_style()

@click.command()
@click.option('--outdir', default="Plots", type=str)
@click.argument('inputfiles', nargs=-1)
def main(inputfiles, outdir):
    os.makedirs(outdir, exist_ok=True)

    keep = {"canv": [], "objs": []}

    ROOT.gStyle.SetOptStat(1110)

    for inputfile in inputfiles:
        if not inputfile.endswith(".root"):
            raise ValueError(f"Input file must be .root: {inputfile}")

        run_name = os.path.basename(inputfile).replace(".root", "")
        parent = os.path.basename(os.path.dirname(inputfile))
        name = f"{parent}_{run_name}"

        df0 = ROOT.RDataFrame("Hits", inputfile)

        c_cal = ROOT.TCanvas(f"c_cal_{name}", f"cal_{name}", 900, 750)
        hcal_ptr = df0.Histo1D((f"hcal_{name}", f"{name};cal;Counts", 400, 0, 2000), "cal")
        hcal = hcal_ptr.GetValue()
        hcal.SetDirectory(0)
        hcal.Draw()
        c_cal.Update()
        c_cal.SaveAs(os.path.join(outdir, f"cal_{name}.png"))

        keep["canv"].append(c_cal)
        keep["objs"].append(hcal)

        max_cal = u.get_max_cal(df0)
        rel01, rel0m1, rel01m1 = u.get_Cal_relation(df0)
        mean_cal, sigma_cal = u.get_mean_cal(df0)

        print(f"\n[CAL] {name}")
        print(f"  max_cal (modo)  = {max_cal}")
        print(f"  mean_cal (fit)  = {mean_cal:.4f}")
        print(f"  sigma_cal (fit) = {sigma_cal:.4f}")
        print(f"  rel01   = {rel01:.4f}")
        print(f"  rel0m1  = {rel0m1:.4f}")
        print(f"  rel01m1 = {rel01m1:.4f}")

        # cut
        cal_cut = f"abs(cal - {max_cal}) < 2.5 && cal > 0 && toa_code > 0"
        base_cut = "cal > 0 && toa_code > 0"
        print(f"  base_cut: {base_cut}")
        print(f"  cal_cut : {cal_cut}")


        # ------------- ToA 1D  -------------
        df_all = ROOT.RDataFrame("Hits", inputfile).Filter(base_cut)
        df_all = u.compute_tbin(df_all)
        df_all = u.compute_ToA(df_all)

        c_toa_all = ROOT.TCanvas(f"c_toa_all_{name}", f"ToA_1D_all_{name}", 900, 750)
        htoa_all_ptr = df_all.Histo1D(
            (f"htoa_all_{name}", f"{name} (all);ToA [ns];Counts", 250, 0, 12.5),
            "ToA"
        )
        htoa_all = htoa_all_ptr.GetValue()
        htoa_all.SetDirectory(0)
        htoa_all.Draw("HIST")
        c_toa_all.Update()
        c_toa_all.SaveAs(os.path.join(outdir, f"ToA_1D_all_{name}.png"))

        keep["canv"].append(c_toa_all)
        keep["objs"].append(htoa_all)

        # -------------ToA 1D cut -------------
        df_peak = ROOT.RDataFrame("Hits", inputfile).Filter(cal_cut)
        df_peak = u.compute_tbin(df_peak)
        df_peak = u.compute_ToA(df_peak)

        c_toa_peak = ROOT.TCanvas(f"c_toa_peak_{name}", f"ToA_1D_calpeak_{name}", 900, 750)
        htoa_peak_ptr = df_peak.Histo1D(
            (f"htoa_peak_{name}", f"{name} (cal peak);ToA [ns];Counts", 250, 0, 12.5),
            "ToA"
        )
        htoa_peak = htoa_peak_ptr.GetValue()
        htoa_peak.SetDirectory(0)
        htoa_peak.Draw("HIST")
        c_toa_peak.Update()
        c_toa_peak.SaveAs(os.path.join(outdir, f"ToA_1D_calpeak_{name}.png"))

        keep["canv"].append(c_toa_peak)
        keep["objs"].append(htoa_peak)

        print(f"[OK] Saved:")
        print(f"  {outdir}/cal_{name}.png")
        print(f"  {outdir}/ToA_1D_all_{name}.png")
        print(f"  {outdir}/ToA_1D_calpeak_{name}.png\n")

        input("Press Enter to continue...")

        # ------------- ToA vs ToT (2D) --------------
        df = ROOT.RDataFrame("Hits", inputfile)
        #df = df.Filter(cal_cut)

        df = u.compute_tbin(df)
        df = u.compute_ToA(df)
        df = u.compute_ToT(df)

        c = ROOT.TCanvas(f"c_{name}", name, 900, 750)
        c.SetRightMargin(0.15)
        ROOT.gStyle.SetOptStat(0)

        h2_ptr = df.Histo2D(
            (f"h2_{name}", f"{name};ToA [ns];cal [ns]", 200, 0, 12.5, 2000, 0, 2000),
            "ToA", "cal"
        )
        h2 = h2_ptr.GetValue()
        h2.SetDirectory(0)
        h2.Draw("COLZ")
        c.Update()
        #c.SaveAs(os.path.join(outdir, f"ToA_vs_csl_{name}_cut.png"))

        keep["canv"].append(c)
        keep["objs"].append(h2)

    input("Done. Press Enter to exit...")

if __name__ == "__main__":
    main()