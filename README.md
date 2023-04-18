# ChiaNFTHelper
ChiaNFTHelper is a Python class that provides a convenient way to fetch and extract owner_address_encoded_ids and owner_encoded_ids from the MintGarden API for a given collection ID. The extracted data can be printed to an Excel file.

## Installation
Before using ChiaNFTHelper, you need to install the required Python packages. You can install the required packages using pip:

In your terminal: `pip install requests pandas argparse`

## Usage

### Command Line Arguments
You can also run ChiaNFTHelper from the command line using the following command:

In your terminal: `python ChiaNFTHelper.py -c <collection_id> [-o <output_file>] [-u]`

The available command line arguments are as follows:

-c or --collection_id: The MintGarden Collection ID to fetch data from (required).

-o or --output_file: The output file name to save the results to (default: "output.xlsx").

-u or --unique: If specified, only unique owner_encoded_ids will be extracted (optional).

## License

ChiaNFTHelper is released under the MIT License.

### Disclaimer
This tool is provided for educational and informational purposes only. Use of this tool is at your own risk. The author and the associated contributors are not responsible for any illegal or unethical use of this tool.

### Donations
Support the 300 Mess with donations of NFTs or any CAT - xch1sfym29gczc0q0p0ery93r65k6dajt34wklytcntdzsz752usruzqh5658t
