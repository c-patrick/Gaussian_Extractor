import os, sys, math
from pathlib import Path
import re
import numpy as np
import json

# Setup paths
WORKING_DIR = Path(__file__).resolve().parent
print(f"Working Directory: {WORKING_DIR}")
INPUT_DIR = Path(WORKING_DIR).joinpath("input")
print(f"Input Directory: {INPUT_DIR}")
OUTPUT_DIR = Path(WORKING_DIR).joinpath("output")
print(f"Output Directory: {OUTPUT_DIR}")

# Configure allowed file extensions
FILE_EXT = (".log", ".out")

# Supported calculation types
CALC_TYPE = ["opt", "freq", "td"]


# Gather files
def gather_files(directory, extensions):
    all_files = []
    for ext in extensions:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(ext):
                    all_files.append(os.path.abspath(os.path.join(root, file)))
    return all_files


# Read input file
def read_input(file):
    with open(file, "r") as f:
        lines = f.readlines()
    Links = split_links(lines)
    link_index = tag_links(Links)
    return Links, link_index


# Split each calculation links into a seperate list element
def split_links(lines):
    Links = []
    Link = []
    for line in lines:
        if line.find("Initial command:") > 0:
            Links.append(Link)
            Link = []
        Link.append(line)
    Links.append(Link)
    print(f"Number of Links: {len(Links)}")
    return Links


# Tag links
def tag_links(Links):
    """Returns a dictionary with key value pairs corresponding to the calculation type and index corresponding to that calculation."""
    index = {
        "opt": 0,
        "freq": 0,
        "td": 0,
    }
    calc_type = CALC_TYPE
    for Link in Links:
        # print(f"Link {Links.index(Link)}") # for debugging
        for line in Link:
            # Check for combined opt-freq calculations
            if "#" in line and re.search("opt freq", line, re.IGNORECASE):
                # print("Found OPTFREQ") # for debugging
                index["opt"] = Links.index(Link)
                index["freq"] = Links.index(Link)
            else:
                for s in calc_type:
                    if "#" in line and re.search(s, line, re.IGNORECASE):
                        # print(f"Found {s}") # for debugging
                        index[s] = Links.index(Link)
    print(index)
    return index


# Exctract SCF energy from link
def Extract_SCF_Energy(lines):
    Energy = []
    for line in lines:
        if "SCF Done:  " in line:
            line_StateInfo = line.split()
            Energy.append(float(line_StateInfo[4]))
    return Energy[-1]


# Extract MOs from link
def Extract_MO(lines):
    AlphaEigenVal = []
    for line in lines:
        if " basis functions, " in line:
            line_StateInfo = line.split()
            NumBasisFunc = int(line_StateInfo[0])
        if " alpha electrons " in line:
            line_StateInfo = line.split()
            # print(line_StateInfo)
            NumAlphaElec = int(line_StateInfo[0])
        if "Alpha  occ. eigenvalues --" in line:
            if len(AlphaEigenVal) == NumBasisFunc:
                AlphaEigenVal = []
            line_removed = line.replace("Alpha  occ. eigenvalues --", " ")
            line_StateInfo = line_removed.split()
            for i in range(len(line_StateInfo)):
                AlphaEigenVal.append(float(line_StateInfo[i]))
        if "Alpha virt. eigenvalues --" in line:
            line_removed = line.replace("Alpha virt. eigenvalues --", " ")
            line_StateInfo = line_removed.split()
            for i in range(len(line_StateInfo)):
                AlphaEigenVal.append(float(line_StateInfo[i]))
    data = {
        "HOMO": AlphaEigenVal[NumAlphaElec - 1],
        "LUMO": AlphaEigenVal[NumAlphaElec],
    }
    return data, NumAlphaElec, AlphaEigenVal


# Extract dipole/quadrupole from link
def Extract_Multipole(lines, match):
    # Explicit index counting required in case two lines are identical (then only the index of the first match is given)
    index = 0
    for line in lines:
        if match in line:
            line_StateInfo = lines[index + 1]
            if "Quadrupole" in match:
                line_StateInfo += lines[index + 2]
        index += 1
    line_StateInfo = line_StateInfo.split()
    # Split at "=", convert key to float and make dictionary
    data = {
        k.split("=", 1)[0]: float(v)
        for k, v in zip(line_StateInfo[0::2], line_StateInfo[1::2])
    }
    print(data)
    return data


# Extract vibrational fequencies from link
def Extract_Vibrations(lines, raman=False):
    frequencies = []
    intensities_IR = []
    intesntities_Raman = []
    for line in lines:
        if "Frequencies " in line:
            tmpfreq = np.fromstring(line[15:], sep=" ")
            # Avoid reading second output
            if frequencies:
                if tmpfreq[0] < frequencies[-1]:
                    break
            frequencies.extend(tmpfreq)
        if "IR Inten    " in line:
            intensities_IR.extend(np.fromstring(line[15:], sep=" "))
        if raman == True and "Raman Activ" in line:
            intensities_IR.extend(np.fromstring(line[15:], sep=" "))
    data = {
        "Frequency": frequencies,
        "IR Intensity": intensities_IR,
    }
    # Check for Raman data and add to dictionary if present
    if intesntities_Raman != []:
        data["Raman Intensity"] = intesntities_Raman
    print(data)
    return data


# Extract excited states from link
def Extract_ExcitedState(lines):
    WaveLength = []
    V_OS = []
    for line in lines:
        if "Excited State  " in line:
            line_StateInfo = line.split()
            WaveLength.append(float(line_StateInfo[6]))
            OS_info = line_StateInfo[8].split("=")
            V_OS.append(float(OS_info[1]))
    data = {
        "Wavelength": WaveLength,
        "Oscillator Strength": V_OS,
    }
    print(data)
    return data


def Extract_Data(
    infile,
    energy=False,
    mo=False,
    dipole=False,
    quadrupole=False,
    vibrations=False,
    excited_states=False,
):
    # Read input file
    print(f"Input File: {infile}")
    Links, link_index = read_input(infile)
    # Get lines from each link
    if link_index["opt"] != 0:
        link_OPT = Links[link_index["opt"]]
    if link_index["freq"] != 0:
        link_FREQ = Links[link_index["freq"]]
    if link_index["td"] != 0:
        link_TD = Links[link_index["td"]]
    # Initialise data list
    data = {}
    # Extract values
    if energy == True:
        data["SCF Energy"] = Extract_SCF_Energy(link_OPT)
    if mo == True:
        mo_data, NumAlphaElec, AlphaEigenVal = Extract_MO(link_OPT)
        data.update(mo_data)
        data["Molecular Orbitals"] = AlphaEigenVal
    if dipole == True:
        data["Dipole"] = Extract_Multipole(link_OPT, match="Dipole moment")
    if quadrupole == True:
        data["Quadrupole"] = Extract_Multipole(
            link_OPT, match="Traceless Quadrupole moment"
        )
    if vibrations == True:
        data["Vibrations"] = Extract_Vibrations(link_FREQ)
    if excited_states == True:
        data["Excited States"] = Extract_ExcitedState(link_TD)
    return data


# Write data to JSON
def make_JSON(data, outpath):
    job_name = list(data.keys())[0]
    outfile = Path.joinpath(outpath, job_name)
    with open(f"{outfile}.json", "w") as f:
        json.dump(data, f)


input_files = gather_files(INPUT_DIR, FILE_EXT)

for file in input_files:
    infile = Path(file)

    datafile = Extract_Data(
        infile=infile,
        energy=True,
        mo=True,
        dipole=True,
        quadrupole=True,
        vibrations=True,
        excited_states=True,
    )

    # Format job name: data as key value pair
    datafile = {infile.stem: datafile}

    # Output data to JSON
    make_JSON(data=datafile, outpath=OUTPUT_DIR)
