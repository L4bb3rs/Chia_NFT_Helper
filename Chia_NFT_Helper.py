import requests
import pandas as pd
import os
import argparse
import itertools


class ChiaNFTHelper:

    def __init__(self, collection_id: str, require_owners: bool) -> None:
        """
        Initialize class attributes.
        """
        self.collection_id = collection_id
        self.url = f"https://api.mintgarden.io/collections/{collection_id}/nfts"
        self.params = {
            "require_owner": str(require_owners).lower(),
            "require_price": "false",
            "size": "100"}
        self.data = None

    def fetch_data(self) -> None:
        """
        Fetch data from the API and store it in the 'data' attribute.
        """
        self.data = {"items": []}
        self.params = {
            "require_owner": str(
                args.did_required).lower(),
            "require_price": "false",
            "size": "100"}

        while True:
            try:
                response = requests.get(self.url, params=self.params)
                # Raise an HTTPError if the status code is >= 400.
                response.raise_for_status()
                page_data = response.json()
                if not page_data["items"]:  # Check if the page has no items
                    break
                self.data["items"].extend(page_data["items"])
                if "next" not in page_data:
                    break
                self.params["page"] = page_data["next"]
            except requests.exceptions.RequestException as e:
                print(
                    f"An error occurred while making a request to the API: {e}")
                break

    def addresses_ids(self) -> None:
        """
        Extract owner_address_encoded_ids and corresponding owner_encoded_ids from the data.
        """
        owner_address_encoded_ids = []
        owner_encoded_ids = []
        encoded_ids = []
        # Loop through each item in the data
        for item in self.data["items"]:
            # Check if the item has encoded_id key
            if "encoded_id" in item:
                # Append the encoded_id to the owner_address_encoded_ids list
                encoded_ids.append(item["encoded_id"])
            else:
                # Append None if owner_address_encoded_id is not present
                encoded_ids.append("No NFT")

            if "owner_address_encoded_id" in item:
                # Append the owner_address_encoded_id to the
                # owner_address_encoded_ids list
                owner_address_encoded_ids.append(
                    item["owner_address_encoded_id"])
            else:
                # Append None if owner_address_encoded_id is not present
                owner_address_encoded_ids.append("No Address")

            # Check if owner_encoded_id key is present and not None
            if "owner_encoded_id" in item and item["owner_encoded_id"] is not None:
                owner_encoded_ids.append(item["owner_encoded_id"])
            else:
                owner_encoded_ids.append("No DID")

        # Create a list of dictionaries containing owner_address_encoded_id,
        # owner_encoded_id, and encoded_id
        self.data["owner_ids"] = [
            {
                "owner_address_encoded_id": addr_id,
                "owner_encoded_id": encoded_id,
                "encoded_id": eid} for addr_id,
            encoded_id,
            eid in itertools.zip_longest(
                owner_address_encoded_ids,
                owner_encoded_ids,
                encoded_ids,
                fillvalue="")]

    def print_results(self, output_file: str, unique: bool = False) -> None:
        """
        Print the extracted owner_address_encoded_ids, owner_encoded_ids, and encoded_ids to an Excel file.
        """
        # Create a list of dictionaries containing owner_address_encoded_id,
        # owner_encoded_id, and encoded_id
        owner_ids = self.data["owner_ids"]

        # If unique flag is True, keep only unique owner_encoded_ids
        if unique:
            # Create a set to store unique owner_encoded_ids
            unique_owner_encoded_ids = set()
            # Create a list to store unique dictionaries
            unique_owner_ids = []
            for d in owner_ids:
                owner_encoded_id = d["owner_encoded_id"]
                if owner_encoded_id != "No DID" and owner_encoded_id not in unique_owner_encoded_ids:
                    unique_owner_encoded_ids.add(owner_encoded_id)
                    unique_owner_ids.append(d)
            owner_ids = unique_owner_ids

        # Convert the list of dictionaries into a pandas DataFrame
        df = pd.DataFrame(
            owner_ids,
            columns=[
                "encoded_id",
                "owner_address_encoded_id",
                "owner_encoded_id"])

        # Get the output directory and join it with the output file name
        output_path = os.path.join(os.getcwd(), output_file)

        # Write the DataFrame to an Excel file
        df.to_excel(output_path, index=False)

    def run(self, output_file: str, unique: bool = False) -> None:
        """
        Run the class methods to fetch data, extract owner_address_encoded_ids and owner_encoded_ids,
        and print the results to an Excel file.
        """
        self.fetch_data()
        self.addresses_ids()
        self.print_results(output_file, unique)


if __name__ == "__main__":
    # Define command line arguments
    parser = argparse.ArgumentParser(
        description="Extract owner_address_encoded_ids and owner_encoded_ids from MintGarden API.")
    parser.add_argument(
        "-c",
        "--collection_id",
        type=str,
        help="Mint Garden Collection ID to fetch data from.",
        required=True)
    parser.add_argument(
        "-o",
        "--output_file",
        type=str,
        help="Output file name to save the results to.",
        default="output.xlsx")
    parser.add_argument(
        "-u", "--unique", action="store_true",
        help="Flag to keep only unique owner DIDs.")
    parser.add_argument(
        "-d", "--did_required", action="store_true",
        help="Flag to require DID for ownership.")
    args = parser.parse_args()

    # Create an instance of MintGardenAPI class
    mint_garden = ChiaNFTHelper(args.collection_id, args.did_required)

    # Run the API data extraction and save the results to an Excel file
    mint_garden.run(args.output_file, args.unique)
