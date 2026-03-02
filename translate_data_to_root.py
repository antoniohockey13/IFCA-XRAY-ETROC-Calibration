import ROOT
import click
import os
from array import array
from tqdm import tqdm

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

    # Format of lines:
    # EH version event_number hits_count num_words
    # H channel L1Counter Type BCID
    # D channel EA Row Col Toa Tot Cal
    # T channel status hits CRC

    # Variables
    variables = {
        # EH
        'event_number': create_array(),
        'version': create_array(),
        'hits_count': create_array(),
        'num_words': create_array(),

        # H
        'channel_h': create_array(),
        'l1counter': create_array(),
        'type': create_array(),
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
        'et_event_number': create_array(),
        'et_event_type': create_array(),
        'et_overflow_count': create_array(),
        'et_hamming_count': create_array(),
        # GLobal event counter
        'event_id': create_array(),
    }


    hits_tree = ROOT.TTree("Hits", "Hits")
    for var_name, var in variables.items():
        hits_tree.Branch(var_name, var, f"{var_name}/I")


    event_id = 0
    previous_hw_event = None
    overflow_counter = 0
    previous_l1 = None
    l1_overflow = 0
    MAX_8BIT = 256

    MAX_16BIT = 65536

    for inputfile in tqdm(inputfiles):
        with open(inputfile) as f:
            lines = f.readlines()
            
        iline = 0
        nlines = len(lines)

        while iline < nlines:
            # Init of block must be EH
            if not lines[iline].startswith('EH'):
                iline += 1
                continue
            # Next line must be H
            if iline + 1 >= nlines or not lines[iline + 1].startswith('H'):
                iline += 1
                continue

            l1_hw = int(lines[iline + 1].split()[2])  # posición del l1counter

            if previous_l1 is not None:
                # Detectar wrap real (255 -> 0)
                if previous_l1 > 200 and l1_hw < 50:
                    l1_overflow += 1

            l1_global = l1_overflow * MAX_8BIT + l1_hw

            previous_l1 = l1_hw

            variables['l1counter'][0] = l1_global

            # Parse EH y H
            try:
                parts = lines[iline].split()
                hw_event = int(parts[1]) # 16-bit
                if previous_hw_event is not None:
                    if hw_event < previous_hw_event:
                        overflow_counter += 1
            
                global_event_number = overflow_counter * MAX_16BIT + hw_event


                variables['event_number'][0] = global_event_number
                variables['version'][0] = int(parts[2])
                variables['hits_count'][0] = int(parts[3])
                variables['num_words'][0] = int(parts[4])

                previous_hw_event = hw_event

                variables['channel_h'][0], variables['l1counter'][0], variables['type'][0], variables['bcid'][0] = \
                    map(int, lines[iline + 1].split()[1:])
                
            except Exception:
                iline += 1
                continue

           # Read all consecutive D lines until T is found
            j = iline + 2
            d_lines = []
            while j < nlines and lines[j].startswith('D'):
                d_lines.append(lines[j])
                j += 1

            # T must be right after D lines
            if j >= nlines or not lines[j].startswith('T'):
                iline += 1
                continue

            # Parse T once
            try:
                variables['channel_t'][0], variables['status'][0], variables['hits_t'][0], variables['crc'][0] = \
                    map(int, lines[j].split()[1:])
            except Exception:
                iline += 1
                continue

            variables['event_id'][0] = event_id
            event_id += 1

            # Parse ET
            if j + 1 < nlines and lines[j + 1].startswith('ET'):
                try:
                    parts_et = lines[j + 1].split()
                    variables['et_event_number'][0] = int(parts_et[1])
                    variables['et_event_type'][0] = int(parts_et[2])
                    variables['et_overflow_count'][0] = int(parts_et[3])
                    variables['et_hamming_count'][0] = int(parts_et[4])
                except Exception:
                    variables['et_event_number'][0] = -1
                    variables['et_event_type'][0] = -1
                    variables['et_overflow_count'][0] = -1
                    variables['et_hamming_count'][0] = -1

            # Fill once per hit
            for d in d_lines:
                try:
                    (variables['channel_d'][0], variables['ea'][0], variables['row'][0],
                     variables['col'][0], variables['toa_code'][0],
                     variables['tot_code'][0], variables['cal'][0]) = \
                        map(int, d.split()[1:])

                    hits_tree.Fill()

                except Exception:
                    continue

            if j + 1 < nlines and lines[j + 1].startswith('ET'):
                iline = j + 2
            else:
                iline = j + 1
            
    hits_tree.Write()
    hits.Close()

    print(f"File saved in {out_path}")
    print(f"Total reconstructed events: {event_id}")
    print(f"Last global event number: {global_event_number}")
    print(f"Last L1 counter value: {l1_global}")

if __name__ == '__main__':
    try:
        main()
    except ValueError as e:
        print(f"\033[91mError: {e}\033[0m")