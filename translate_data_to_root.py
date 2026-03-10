import ROOT
import click
import os
from array import array
from tqdm import tqdm


MAX_16BIT = 65536


def create_array():
    """
    Create an array of integers with one element.
    """
    return array('i', [0])

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
    if f.split('.')[-1] != 'sem':
        raise ValueError(f"Input file must have .sem extension and it has .{f.split('.')[-1]}")  

    run_dir = os.path.dirname(os.path.abspath(f))  
    k_dir = os.path.basename(os.path.dirname(run_dir)) 
    run_folder = os.path.basename(run_dir) 

    out_dir = os.path.join("Root_files", k_dir)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{run_folder}.root")
    hits = ROOT.TFile(out_path, "RECREATE")
    hits_tree = ROOT.TTree("Hits", "Hits")

    # Format of lines:
    # EH version event_number hits_count num_words
    # H channel L1Counter Type BCID
    # D channel EA Row Col Toa Tot Cal
    # T channel status hits CRC

    # Variables
    variables = {
        # EH
        'event_number': create_array(),
        'event_type': create_array(),
        'num_words': create_array(),

        # H
        'channel_h': create_array(),
        'l1counter_hw': create_array(), 
        'l1counter_global': create_array(), 
        'type_': create_array(),
        'bcid': create_array(),
        # D
        'channel_d': create_array(),
        'ea': create_array(),
        'col': create_array(),
        'row': create_array(),
        'toa_code': create_array(),
        'tot_code': create_array(),
        'cal': create_array(),
        # T
        'channel_t': create_array(),
        'status': create_array(),
        'hits_t': create_array(),
        'crc': create_array(),
        # ET
        'et_num_hits': create_array(),
        'et_overflow_count': create_array(),
        'et_hamming_count': create_array(),
        'et_crc': create_array(),
        # Gobal event counter
        'event_id_': create_array(),
    }


    for var_name, var in variables.items():
        hits_tree.Branch(var_name, var, f"{var_name}/I")

    with open(inputfiles[0]) as f:
        lines = f.readlines()
            
    iline = 0
    nlines = len(lines)

    previous_l1_hw = -1 
    previous_event_number = -1
    global_event_counter = 0
    global_l1_counter = 0
    events_at_reset = 0
    events_at_l1_reset = 0
    reset_number = 0

    while iline < nlines-3:
        if lines[iline].startswith("EH") and lines[iline+1].startswith("H"):
            eh_line = lines[iline]
            h_line = lines[iline + 1]
        else:
            iline += 1 
            continue

        data_line = True
        i_data = 0
        d_lines = []
        while data_line:
            if lines[iline+2+i_data].startswith("D"):
                # print(lines[iline + 2 + i_data])
                d_lines.append(lines[iline+2+i_data])
                i_data+=1
                # print(i_data)
            else:
                data_line = False
        # XXX - Keep only events with a single hit
        if i_data != 1:
            iline += 2
            continue

        # print(lines[iline + 2 + i_data])
        # print(lines[iline + 3 + i_data])
        if lines[iline+2+i_data].startswith("T") and lines[iline+3+i_data].startswith("ET"):
            t_line = lines[iline + 2 + i_data]
            et_line = lines[iline + 3 + i_data]
        else:
            print(f"ERROR, unexpected line in {iline}")
            print(lines[iline])
            print(lines[iline+1])
            print(lines[iline+2])
            print(lines[iline+1+i_data])
            print(lines[iline+2+i_data])
            input()

        # Parse lines
        # EH event_number, event_type, num_words
        # print(eh_line.split())
        _, event_number, event_type, num_words, _ = eh_line.split()
        event_number = int(event_number)
        event_type = int(event_type)
        num_words = int(num_words)
        # H channel, l1_counter, type, bcid
        # print(h_line.split())
        _, channel_h, l1_counter_hw, type_, bcid = h_line.split()
        channel_h = int(channel_h)
        l1_counter_hw = int(l1_counter_hw)
        type_ = int(type_)
        bcid = int(bcid)
        # T channel, status, hits, crc
        # print(t_line.split())
        parts = t_line.split()
        channel_t = int(parts[1])
        status = int(parts[2])
        hits_t = int(parts[3])
        crc_t = int(parts[4])
        # ET num_hits, overflow_count, hamming_count, crc
        # print(et_line.split())
        _, num_hits, overflow_count, hamming_count, crc_et = et_line.split()
        num_hits = int(num_hits)
        overflow_count = int(overflow_count)
        hamming_count = int(hamming_count)
        crc_et = int(crc_et)

        # Compute global counters
        if event_number <= previous_event_number:
            print(f"Found reset in line {iline}, at previous event number = {previous_event_number} and event number = {event_number}, number of resets = {reset_number}")
            reset_number += 1
            events_at_reset += previous_event_number
        if event_number == 0:
            events_at_reset += 1
        global_event_counter = events_at_reset + event_number
   
        if l1_counter_hw < previous_l1_hw:
            # print(f"Found reset in line {iline}, at previous l1 = {previous_l1_hw} and l1 counter= {l1_counter_hw}")
            # print(lines[iline])
            events_at_l1_reset += previous_l1_hw
        if l1_counter_hw == 0:
            events_at_l1_reset += 1
        global_l1_counter = events_at_l1_reset + l1_counter_hw


        for i_data_line in d_lines:
            try:
                # D channel, EA, Row, Col, ToA, ToT, Cal
                # print(i_data_line.split())
                _, channel_d, ea, row, col, toa, tot, cal = i_data_line.split()
                channel_d = int(channel_d)
                ea = int(ea)
                row = int(row)
                col = int(col)
                toa = int(toa)
                tot = int(tot)
                cal = int(cal)
                # Fill the tree
                variables['event_number'][0]      = event_number
                variables['event_type'][0]        = event_type
                variables['num_words'][0]         = num_words
                variables['channel_h'][0]         = channel_h
                variables['l1counter_hw'][0]      = l1_counter_hw
                variables['l1counter_global'][0]  = global_l1_counter
                variables['type_'][0]             = type_
                variables['bcid'][0]              = bcid
                variables['channel_d'][0]         = channel_d
                variables['ea'][0]                = ea
                variables['col'][0]               = col
                variables['row'][0]               = row
                variables['toa_code'][0]          = toa
                variables['tot_code'][0]          = tot
                variables['cal'][0]               = cal
                variables['channel_t'][0]         = channel_t
                variables['status'][0]            = status
                variables['hits_t'][0]            = hits_t
                variables['crc'][0]               = crc_t
                variables['et_num_hits'][0]       = num_hits
                variables['et_overflow_count'][0] = overflow_count
                variables['et_hamming_count'][0]  = hamming_count
                variables['et_crc'][0]            = crc_et
                variables['event_id_'][0]         = global_event_counter
                # print(event_number, event_type, num_words, channel_h, l1_counter_hw, global_l1_counter, type_, bcid, channel_d, ea, col, row, toa, tot, cal, channel_t, status, hits, crc_t, num_hits, overflow_count, hamming_count, crc_et, global_event_counter)
                hits_tree.Fill()


            except (ValueError, IndexError):
                print("ERROR")
                continue
        # if global_l1_counter != global_event_counter:
        #     print("ERROR: different number of events")
        #     print(f"global event = {global_event_counter}, l1 event = {global_l1_counter}")
        #     print(f"line = {iline}")
        #     # input()
        # Update counters 
        iline += 4 + i_data
        previous_event_number = event_number
        previous_l1_hw = l1_counter_hw
  
            
            
    hits_tree.Write()
    hits.Close()

    print(f"File saved in {out_path}")
    print(f"Total reconstructed events: {global_event_counter}")
    print(f"Last L1 counter value: {global_l1_counter}")

if __name__ == '__main__':
    try:
        main()
    except ValueError as e:
        print(f"\033[91mError: {e}\033[0m")