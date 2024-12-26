import ROOT
import click
import os
from array import array

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
    if f.split('.')[-1] != 'nem':
        raise ValueError(f"Input file must have .nem extension and it has .{f.split('.')[-1]}")  
    
    folder = f.split('/')[1].split('_')[1]
    # Separate date and time with _ 
    folder = folder[:4] + '_' + folder[4:6] + '_' + folder[6:8] + '-' + folder[8:10]+ '_' + folder[10:12] + '_' + folder[12:]
    hits = ROOT.TFile(f"Root_files/{folder}.root", "RECREATE")

    # Format of lines:
    # EH version event_number hits_count num_words
    # H channel L1Counter Type BCID
    # D channel EA Row Col Toa Tot Cal
    # T channel status hits CRC

    # Variables
    variables = {
        # EH
        'version': create_array(),
        'event_number': create_array(),
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
        'crc': create_array()
    }

    # Create tree
    hits_tree = ROOT.TTree("Hits", "Hits")
    for var_name, var in variables.items():
        hits_tree.Branch(var_name, var, f"{var_name}/I")


    for inputfile in inputfiles:
        with open(inputfile) as f:
            lines = f.readlines()
            iline = 0
            while iline < (len(lines)):
                if (
                    lines[iline][0:2] == 'EH' and 
                    lines[iline+1][0] == 'H' and 
                    lines[iline+2][0]== 'D' and 
                    lines[iline+3][0] == 'T'
                ):
                    # EH
                    variables['version'][0], variables['event_number'][0], variables['hits_count'][0], variables['num_words'][0] \
                        = map(int, lines[iline].split()[1:])
                    # H
                    variables['channel_h'][0], variables['l1counter'][0], variables['type'][0], variables['bcid'][0] \
                        = map(int, lines[iline + 1].split()[1:])
                    # D
                    variables['channel_d'][0], variables['ea'][0], variables['row'][0], variables['col'][0], \
                        variables['toa_code'][0], variables['tot_code'][0], variables['cal'][0] \
                        = map(int, lines[iline + 2].split()[1:])
                    # T
                    variables['channel_t'][0], variables['status'][0], variables['hits_t'][0], variables['crc'][0] \
                        = map(int, lines[iline + 3].split()[1:])

                    hits_tree.Fill()
                    iline += 4 # Skip to next block
                else:
                    iline += 1 # Skip to next line
    hits_tree.Write()
    hits.Write()
    hits.Close()

if __name__ == '__main__':
    try:
        main()
    except ValueError as e:
        print(f"\033[91mError: {e}\033[0m")
