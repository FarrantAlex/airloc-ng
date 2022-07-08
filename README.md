## airloc-ng

Parses logcsv output from airodump-ng and geo-locates BSSIDs.
A WiGLE commercial account is required.

The script defaults to 2450MHz, with an 18dBi antenna and a target talking 20dBm. 
You may want to change these.

## Install

```
pip3 install simplekml requests
```

## Usage

```
python3 airloc-ng output.csv
```

## Known issues

WiGLE API may report unauthorized. Speak to WiGLE support.
