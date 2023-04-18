import requests
import pandas as pd
import os
import argparse

class MintGardenAPI:
    
    def __init__(self, collection_id: str) -> None:
        """
        Initialize class attributes.
        """
        self.collection_id = collection_id
        self.url = f"https://api.mintgarden.io/collections/{collection_id}/nfts"
        self.params = {"require_owner": "true", "require_price": "false", "size": "100"}
        self.data = None
        self.unique_owner_encoded_ids = None
        self.unique_owner_address_encoded_ids = None
        self.unique_owners_dict = None
    
    def fetch_data(self) -> None:
        """
        Fetch data from the API and store it in the 'data' attribute.
        """
        self.data = {"items": []}
        self.params = {"require_owner": "true", "require_price": "false", "size": "100"}

        while True:
            try:
                response = requests.get(self.url, params=self.params)
                response.raise_for_status()  # Raise an HTTPError if the status code is >= 400.
                page_data = response.json()
                if not page_data["items"]: # Check if the page has no items
                    break
                self.data["items"].extend(page_data["items"])
                if "next" not in page_data:
                    break
                self.params["page"] = page_data["next"]
            except requests.exceptions.RequestException as e:
                print(f"An error occurred while making a request to the API: {e}")
                break

    
    def extract_unique_ids(self) -> None:
        """
        Extract unique owner_encoded_ids and corresponding owner_address_encoded_ids from the data.
        """
        if self.data is None:
            print("No data to extract IDs from.")
            return

        self.unique_owner_encoded_ids = set()
        self.unique_owners_dict = {}

        for item in self.data["items"]:
            owner_encoded_id = item.get("owner_encoded_id")
            owner_address_encoded_id = item.get("owner_address_encoded_id")
            if owner_encoded_id:
                if owner_encoded_id not in self.unique_owner_encoded_ids:
                    self.unique_owner_encoded_ids.add(owner_encoded_id)
                    self.unique_owners_dict[owner_encoded_id] = [owner_address_encoded_id]
                else:
                    self.unique_owners_dict[owner_encoded_id].append(owner_address_encoded_id)

        self.unique_owners_dict = {owner_encoded_id: list(set(owner_address_encoded_ids))
                                for owner_encoded_id, owner_address_encoded_ids
                                in self.unique_owners_dict.items()}


    def print_results(self, output_file: str, unique: bool = False) -> None:
        # Create a list of dictionaries for each unique owner_encoded_id and owner_address_encoded_id pair
        unique_owners_list = []
        for owner_encoded_id in self.unique_owner_encoded_ids:
            owner_address_encoded_id = self.unique_owners_dict[owner_encoded_id]
            unique_owners_list.append({"owner_encoded_id": owner_encoded_id, "owner_address_encoded_id": owner_address_encoded_id})

        if unique:
            # Create a set to keep track of seen owner_address_encoded_id values
            seen_addresses = set()
            # Create a new list to store only unique owner_encoded_id and owner_address_encoded_id pairs
            unique_owners_list_new = []
            for owner_dict in unique_owners_list:
                address = tuple(owner_dict["owner_address_encoded_id"])
                if address not in seen_addresses:
                    seen_addresses.add(address)
                    unique_owners_list_new.append(owner_dict)
            unique_owners_list = unique_owners_list_new

        # Convert the list of dictionaries into a pandas DataFrame
        df = pd.DataFrame(unique_owners_list)

        # Remove the [' '] from the addresses
        if unique:
            df['owner_address_encoded_id'] = df['owner_address_encoded_id'].apply(lambda x: x[0] if len(x) > 0 else '')

        # Get the output directory and join it with the output file name
        output_path = os.path.join(os.getcwd(), output_file)

        # Write the DataFrame to an Excel file
        df.to_excel(output_path, index=False)




    def run(self, output_file: str, unique: bool = False) -> None:
        """
        Run the class methods to fetch data, extract unique IDs, and print results.
        """
        self.fetch_data()
        self.extract_unique_ids()
        self.print_results(output_file, unique=unique)




parser = argparse.ArgumentParser(description="MintGardenAPI script")

parser.add_argument("-c", "--collection_id", type=str, required=True,
                    help="The ID of the MintGarden collection to fetch data from.")
parser.add_argument("-o", "--output_file", type=str, default="output.xlsx",
                    help="The name of the output file. Default is 'output.xlsx'.")
parser.add_argument("-u", "--unique", action="store_true", default=False,
                    help="Whether to extract only unique owner_encoded_ids and owner_address_encoded_ids.")

args = parser.parse_args()


api = MintGardenAPI(args.collection_id)
api.run(args.output_file, unique=args.unique)


