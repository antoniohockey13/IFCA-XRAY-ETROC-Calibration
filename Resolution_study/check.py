import os
import click
import ROOT

ROOT.gStyle.SetOptStat(1110)

def parse_sem_l1counter(sem_path, max_lines=None):
    """
    Lee un .sem y devuelve lista de l1counter y event_number (si aparece en EH).
    Estructura típica:
      EH version event_number hits_count num_words
      H channel L1Counter Type BCID
      ...
    """
    l1_list = []
    ev_list = []

    current_event = None

    with open(sem_path, "r") as f:
        for i, line in enumerate(f):
            if max_lines is not None and i >= max_lines:
                break

            line = line.strip()
            if not line:
                continue

            if line.startswith("EH"):
                parts = line.split()
                # EH version event_number hits_count num_words
                #      1       2           3          4
                if len(parts) >= 3:
                    try:
                        current_event = int(parts[2])
                    except Exception:
                        current_event = None

            elif line.startswith("H"):
                parts = line.split()
                # H channel L1Counter Type BCID
                if len(parts) >= 3:
                    try:
                        l1 = int(parts[2])
                        l1_list.append(l1)
                        ev_list.append(current_event if current_event is not None else -1)
                    except Exception:
                        pass

    return l1_list, ev_list


def draw_hist_l1(l1_list, title, outpng=None, pause=True):
    c = ROOT.TCanvas(f"c_{title}", title, 900, 650)
    # bins “cómodos”: si está capado a 0-255 lo verás muy claro
    h = ROOT.TH1I(f"h_{title}", f"{title};l1counter;counts", 512, 0, 512)
    for v in l1_list:
        h.Fill(v)
    h.Draw("hist")
    c.Update()
    if outpng:
        c.SaveAs(outpng)
    if pause:
        input("Press Enter to continue...")


def draw_l1_vs_event(l1_list, ev_list, title, outpng=None, pause=True):
    c = ROOT.TCanvas(f"c2_{title}", title, 900, 650)
    # rango de event_number: estimación rápida
    ev_min = min(ev_list) if ev_list else 0
    ev_max = max(ev_list) if ev_list else 1
    if ev_max <= ev_min:
        ev_max = ev_min + 1

    h2 = ROOT.TH2I(
        f"h2_{title}",
        f"{title};event_number;l1counter",
        200, ev_min, ev_max,
        256, 0, 256
    )
    for ev, l1 in zip(ev_list, l1_list):
        h2.Fill(ev, l1)
    h2.Draw("colz")
    c.SetRightMargin(0.15)
    c.Update()
    if outpng:
        c.SaveAs(outpng)
    if pause:
        input("Press Enter to continue...")


@click.command()
@click.argument("semfile", type=click.Path(exists=True))
@click.argument("rootfile", type=click.Path(exists=True))
@click.option("--pause/--no-pause", default=True, help="Pausa con Enter entre plots")
@click.option("--max-lines", default=None, type=int, help="Limita líneas leídas del .sem (debug rápido)")
@click.option("--outdir", default="Debug_L1", type=str, help="Carpeta de salida de PNGs")
def main(semfile, rootfile, pause, max_lines, outdir):
    os.makedirs(outdir, exist_ok=True)

    # -------- SEM --------
    sem_name = os.path.basename(semfile)
    l1_sem, ev_sem = parse_sem_l1counter(semfile, max_lines=max_lines)
    print(f"[SEM] {sem_name}: entries(H lines)={len(l1_sem)}  unique_l1={len(set(l1_sem))}  min={min(l1_sem) if l1_sem else None}  max={max(l1_sem) if l1_sem else None}")

    draw_hist_l1(
        l1_sem,
        title=f"SEM_{sem_name}",
        outpng=os.path.join(outdir, f"l1counter_SEM_{sem_name}.png"),
        pause=pause
    )
    # si quieres ver evolución en SEM:
    draw_l1_vs_event(
        l1_sem,
        ev_sem,
        title=f"SEM_{sem_name}_l1_vs_event",
        outpng=os.path.join(outdir, f"l1_vs_event_SEM_{sem_name}.png"),
        pause=pause
    )

    # -------- ROOT --------
    root_name = os.path.basename(rootfile)
    f = ROOT.TFile.Open(rootfile)
    t = f.Get("Hits")

    # Hist l1counter en ROOT
    c = ROOT.TCanvas("c_root_l1", "ROOT l1counter", 900, 650)
    t.Draw("l1counter")
    c.Update()
    c.SaveAs(os.path.join(outdir, f"l1counter_ROOT_{root_name}.png"))
    if pause:
        input("Press Enter to continue...")

    # l1counter vs event_number en ROOT
    c2 = ROOT.TCanvas("c_root_l1_ev", "ROOT l1 vs event", 900, 650)
    t.Draw("l1counter:event_number", "", "colz")
    c2.SetRightMargin(0.15)
    c2.Update()
    c2.SaveAs(os.path.join(outdir, f"l1_vs_event_ROOT_{root_name}.png"))
    if pause:
        input("Press Enter to continue...")

    # info numérica
    # (OJO: en ROOT son hits, no eventos)
    # Para únicos de l1counter: mejor con RDataFrame en python, pero aquí damos min/max:
    print(f"[ROOT] {root_name}: l1 min={t.GetMinimum('l1counter')}  l1 max={t.GetMaximum('l1counter')}")

    f.Close()
    print(f"[OK] PNGs guardados en: {outdir}/")


if __name__ == "__main__":
    main()