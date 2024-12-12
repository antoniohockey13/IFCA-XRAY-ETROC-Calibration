import ROOT
import click
import os
from array import array

@click.command()
@click.argument('inputfiles', nargs=-1, type=click.Path(exists=True))
def main(inputfiles):
    """
    Process TOT and TOA data from input files and generate a 2D hit map.
    
    INPUTFILES: List of input files to process.
    """
    # Create folder to save root files
    os.makedirs("Root_files", exist_ok=True)

    f = inputfiles[0]
    
    folder = f.split('/')[0].split('_')[1]
    # Separate date and time with _ 
    folder = folder[:4] + '_' + folder[4:6] + '_' + folder[6:8] + '-' + folder[8:10]+ '_' + folder[10:12] + '_' + folder[12:]
    hits = ROOT.TFile(f"Root_files/{folder}.root", "RECREATE")

    # Format of lines:
    # EH version event_number hits_count num_words
    # H channel L1Counter Type BCID
    # D channel EA Row Col Toa Tot Cal
    # T channel status hits CRC
    # EH
    version = array('i', [0])
    event_number = array('i', [0])
    hits_count = array('i', [0])
    num_words = array('i', [0])
    # H
    channel_h = array('i', [0])
    l1counter = array('i', [0])
    type = array('i', [0])
    bcid = array('i', [0])
    # D
    channel_d = array('i', [0])
    ea = array('i', [0])
    col = array('i', [0])
    row = array('i', [0])
    toa_code = array('i', [0])
    tot_code = array('i', [0])
    cal = array('i', [0])
    # T
    channel_t = array('i', [0])
    status = array('i', [0])
    hits_t = array('i', [0])
    crc = array('i', [0])
    # Create tree
    hits_tree = ROOT.TTree("Hits", "Hits")
    # EH
    hits_tree.Branch("version", version, "version/I")
    hits_tree.Branch("event_number", event_number, "event_number/I")
    hits_tree.Branch("hits_count", hits_count, "hits_count/I")
    hits_tree.Branch("num_words", num_words, "num_words/I")
    # H
    hits_tree.Branch("channel_h", channel_h, "channel/I")
    hits_tree.Branch("l1counter", l1counter, "l1counter/I")
    hits_tree.Branch("type", type, "type/I")
    hits_tree.Branch("bcid", bcid, "bcid/I")
    # D
    hits_tree.Branch("channel_d", channel_d, "channel_d/I")
    hits_tree.Branch("ea", ea, "ea/I")
    hits_tree.Branch("col", col, "col/I")
    hits_tree.Branch("row", row, "row/I")
    hits_tree.Branch("toa_code", toa_code, "toa_code/I")
    hits_tree.Branch("tot_code", tot_code, "tot_code/I")
    hits_tree.Branch("cal", cal, "cal/I")
    # T
    hits_tree.Branch("channel_t", channel_t, "channel_t/I")
    hits_tree.Branch("status", status, "status/I")
    hits_tree.Branch("hits_t", hits_t, "hits_t/I")
    hits_tree.Branch("crc", crc, "crc/I")


    for inputfile in inputfiles:
        with open(inputfile) as f:
            lines = f.readlines()
            iline = 0
            while iline < (len(lines)):
                if lines[iline][0:2] == 'EH' and lines[iline+1][0] == 'H' and lines[iline+2][0]== 'D' and lines[iline+3][0] == 'T':
                    line_eh = lines[iline]
                    line_h = lines[iline+1]
                    line_d = lines[iline+2]
                    line_t = lines[iline+3]
                    # EH
                    _, iversion, ievent_number, ihits_count, inum_words = line_eh.strip().split()
                    iversion, ievent_number, ihits_count, inum_words = int(iversion), int(ievent_number), int(ihits_count), int(inum_words)
                    # H
                    _, ichannel_h, il1counter, itype, ibcid = line_h.strip().split()
                    ichannel_h, il1counter, itype, ibcid = int(ichannel_h), int(il1counter), int(itype), int(ibcid)
                    # D
                    _, ichannel_d, iea, irow, icol, itoa_code, itot_code, ical = line_d.strip().split()
                    ichannel_d, iea, irow, icol, itoa_code, itot_code, ical = int(ichannel_d), int(iea), int(irow), int(icol), int(itoa_code), int(itot_code), int(ical)
                    # T
                    _, ichannel_t, istatus, ihits_t, icrc = line_t.strip().split()
                    ichannel_t, istatus, ihits_t, icrc = int(ichannel_t), int(istatus), int(ihits_t), int(icrc)

                    # Save data to root file
                    # Event header variables
                    version[0], event_number[0], hits_count[0], num_words[0] = iversion, ievent_number, ihits_count, inum_words
                    # Header variables
                    channel_h[0], l1counter[0], type[0], bcid[0] = ichannel_h, il1counter, itype, ibcid
                    # Data variables
                    channel_d[0], ea[0], row[0], col[0], toa_code[0], tot_code[0], cal[0] = ichannel_d, iea, irow, icol, itoa_code, itot_code, ical
                    # Trailer variables
                    channel_t[0], status[0], hits_t[0], crc[0] = ichannel_t, istatus, ihits_t, icrc

                    hits_tree.Fill()
                    iline += 4
                else:
                    iline += 1
    hits_tree.Write()
    hits.Write()
    hits.Close()

if __name__ == '__main__':
    main()