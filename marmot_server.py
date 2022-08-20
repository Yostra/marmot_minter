import json
import signal
import traceback
from pathlib import Path
from typing import List, Optional
import nft_storage
import asyncio

from chia_rs import Coin
from clvm.casts import int_from_bytes
from nft_storage.api import nft_storage_api
from chia.rpc.full_node_rpc_client import FullNodeRpcClient
from chia.rpc.wallet_rpc_client import WalletRpcClient
from chia.types.blockchain_format.program import INFINITE_COST
from chia.types.blockchain_format.sized_bytes import bytes32
from chia.types.coin_record import CoinRecord
from chia.types.coin_spend import CoinSpend
from chia.types.condition_opcodes import ConditionOpcode
from chia.util.bech32m import decode_puzzle_hash, encode_puzzle_hash
from chia.util.config import load_config
from chia.util.default_root import DEFAULT_ROOT_PATH
from chia.util.ints import uint16
from chia.wallet.marmot import sha256sum


import logging

from chia.wallet.marmot_db_api import DatabaseApi
from chia.wallet.marmot_description import create_description
from chia.wallet.marmot_gen import create_nft_image

log = logging.getLogger(__name__)
RECEIVE_ADDRESS = "xch..."
ROYALTY_ADDRESS = "xch..."

XCH_PRICE = 500000000000
NFT_STORAGE_API_KEY = "NFT_STORAGE_API_KEY"
DID_ID = ""
NFT_WALLET_ID = 5
WEBSITE = "https://"
BANNER_URL = "https://"
ICON_URL = "https://"
TWITTER = "@..."
COLLECTION_DESCRIPTION = "Mrmrmrm"
COLLECTION_NAME = "Marmot World Order"
ROYALTY_PERCENTAGE = 3000

class WalletServer:
    shut_down: bool
    shut_down_event: asyncio.Event
    full_node_rpc: FullNodeRpcClient
    wallet_client: WalletRpcClient
    receive_address: str
    database_api: DatabaseApi

    def get_memos(self, coin_spend: CoinSpend) -> str:
        _, result = coin_spend.puzzle_reveal.run_with_cost(INFINITE_COST, coin_spend.solution)
        for condition in result.as_python():
            if condition[0] == ConditionOpcode.CREATE_COIN and len(condition) >= 4:
                # If only 3 elements (opcode + 2 args), there is no memo, this is ph, amount
                coin_added = Coin(coin_spend.coin.name(), bytes32(condition[1]), int_from_bytes(condition[2]))
                if type(condition[3]) != list:
                    # If it's not a list, it's not the correct format
                    continue
                return condition[3][0].decode()

        return ""

    @staticmethod
    async def create_web_server():
        self = WalletServer()
        self.shut_down = False
        self.shut_down_event = asyncio.Event()
        config = load_config(DEFAULT_ROOT_PATH, "config.yaml")
        self_hostname = config["self_hostname"]
        wallet_rpc_port = config["wallet"]["rpc_port"]
        fullnode_rpc_port = config["full_node"]["rpc_port"]

        self.wallet_client = await WalletRpcClient.create("127.0.0.1", uint16(wallet_rpc_port), DEFAULT_ROOT_PATH, config)
        self.receive_address = RECEIVE_ADDRESS
        self.full_node_rpc = await FullNodeRpcClient.create(
            self_hostname, fullnode_rpc_port, DEFAULT_ROOT_PATH, config
        )
        self.database_api = await DatabaseApi.create_api()
        asyncio.create_task(self.monitor_deposit_task())
        asyncio.create_task(self.payout_task())

        asyncio.get_running_loop().add_signal_handler(signal.SIGINT, self.stop_all)
        asyncio.get_running_loop().add_signal_handler(signal.SIGTERM, self.stop_all)
        return self

    async def monitor_deposit_task(self):
        while True:
            address_bytes = decode_puzzle_hash(self.receive_address)
            coin_records: List[
                CoinRecord
            ] = await self.full_node_rpc.get_coin_records_by_puzzle_hash(
                address_bytes, False
            )
            print(f"Number of coins {len(coin_records)}" )

            for coin_record in coin_records:

                # Fetch parent spend
                parent_coin_name = coin_record.coin.parent_coin_info
                parent_coin: Optional[
                    CoinRecord
                ] = await self.full_node_rpc.get_coin_record_by_name(
                    parent_coin_name
                )


                received_amount = coin_record.coin.amount
                to_puzzle_hash = parent_coin.coin.puzzle_hash
                to_address = encode_puzzle_hash(to_puzzle_hash, "xch")

                parent_id = parent_coin.coin.name()
                task = await self.database_api.get_mint_task(parent_id.hex())
                if task is not None:
                    print("task for this one already exists")
                    continue

                if received_amount < XCH_PRICE:
                    print(f"Not enough xch received {received_amount}")
                    continue

                cs: CoinSpend = await self.full_node_rpc.get_puzzle_and_solution(parent_id, parent_coin.spent_block_index)
                memo = self.get_memos(cs)
                if len(memo) > 60:
                    memo = ""

                print(f"Received amount: {received_amount}")
                print(f"Parent_id: {parent_id.hex()}")
                print(f"Mint for: {to_puzzle_hash.hex()}")

                await self.database_api.create_mint_task(parent_id=parent_id.hex(), to_puzzle_hash=to_address, custom_text=memo)
                print("Creating a mint task")
                pass

            await asyncio.sleep(30)

    # mint
    async def mint(self, image_path: str, to_address: str, marmot_id: int, custom_text: str):
        filepath = image_path
        sha = sha256sum(filepath)

        configuration = nft_storage.Configuration(
            host="https://api.nft.storage",
            access_token=NFT_STORAGE_API_KEY
        )

        cid = None
        with nft_storage.ApiClient(configuration) as api_client:
            # Create an instance of the API class
            api_instance = nft_storage_api.NFTStorageAPI(api_client)
            body = open(filepath, 'rb')  # file_type |

            try:
                # Check if a CID of an NFT is being stored by nft.storage.
                api_response = api_instance.store(body, _check_return_type=False)
                cid = api_response["value"]["cid"]
                print(api_response)
            except nft_storage.ApiException as e:
                print("Exception when calling NFTStorageAPI->check: %s\n" % e)

        assert cid is not None
        wallet_id = NFT_WALLET_ID
        image_url = f"https://{cid}.ipfs.nftstorage.link/"
        uris = [image_url]
        hash = sha
        fee = 1000
        edition_number = 1
        royalty_percentage = ROYALTY_PERCENTAGE
        target_address = to_address
        royalty_address = ROYALTY_ADDRESS

        custom_description = await create_description(custom_text, marmot_id)

        text_data = {"format": "CHIP-0007", "name": f"Marmot #{marmot_id}", "description": f"{custom_description}",
                     "sensitive_content": False,
                     "collection": {
                         "name": COLLECTION_NAME,
                         "id": DID_ID,
                         "attributes": [
                             {
                                 "type": "description",
                                 "value": COLLECTION_DESCRIPTION
                             },
                             {
                                 "type": "twitter",
                                 "value": TWITTER
                             },
                             {
                                 "type": "website",
                                 "value": WEBSITE
                             },
                             {
                                 "type": "banner",
                                 "value": BANNER_URL
                             },
                             {
                                 "type": "icon",
                                 "value": ICON_URL
                             },
                         ]
                     }}
        json_text = json.dumps(text_data, indent=4)
        json_path = Path(f"image_tasks/{marmot_id}.json")
        json_path.write_text(json_text)

        with nft_storage.ApiClient(configuration) as api_client:
            # Create an instance of the API class
            api_instance = nft_storage_api.NFTStorageAPI(api_client)
            body = open(f"{json_path}", 'rb')  # file_type |

            try:
                # Check if a CID of an NFT is being stored by nft.storage.
                api_response = api_instance.store(body, _check_return_type=False)
                json_cid = api_response["value"]["cid"]
                print(api_response)
            except nft_storage.ApiException as e:
                print("Exception when calling NFTStorageAPI->check: %s\n" % e)

        assert cid is not None
        metadata_url = f"https://{json_cid}.ipfs.nftstorage.link/"
        metadata_sha = sha256sum(f"{json_path}")
        json_path.unlink()
        print("Minting!!")
        res = await self.wallet_client.mint_nft(
            wallet_id=wallet_id,
            royalty_address=royalty_address,
            target_address=target_address,
            hash=hash,
            uris=uris,
            fee=100000,
            meta_hash=metadata_sha,
            meta_uris=[metadata_url],
            royalty_percentage=royalty_percentage,
            did_id=DID_ID
        )


    async def payout_task(self):
        while True:
            await asyncio.sleep(10)
            standard = await self.wallet_client.get_wallet_balance(1)
            standard_balance = standard["spendable_balance"]
            standard_total = standard["confirmed_wallet_balance"]

            mint = False
            if standard_balance > 0 and standard_balance == standard_total:
                mint = True

            if mint is False:
                continue

            # Get pending mints
            tasks = await self.database_api.get_pending_tasks()

            if len(tasks) == 0:
                print(f"There are {len(tasks)} tasks")
                continue

            print(f"There are {len(tasks)} tasks")
            task = tasks[0]
            image_path = None

            tasks = await self.database_api.get_pending_tasks()
            task = tasks[0]

            if task.marmot_image_url is not None and task.marmot_image_url != "":
                image_path = task.marmot_image_url
            else:
                for i in range(0, 3):
                    try:
                        image_path = await create_nft_image(task.custom_text)
                        break
                    except Exception as e:
                        print(f"Exception in create_nft image")
                        pass

                if image_path is None:
                    try:
                        image_path = await create_nft_image("")
                    except:
                        pass

            if image_path is None:
                continue


            print(f"Time to mint {task}")
            assert Path(image_path).is_file()
            assert len(Path(image_path).read_bytes()) > 10000

            new_path = Path(f"{Path(image_path).parent}/{task.marmot_id}.png")
            new_path.write_bytes(Path(image_path).read_bytes())

            new_path_str = f"{new_path.absolute()}"
            if task.marmot_id == 1000 or task.marmot_id>1000:
                await asyncio.sleep(30000)
                continue

            await task.update(status=1).apply()
            await self.mint(to_address=task.to_address, marmot_id=task.marmot_id, image_path=new_path_str, custom_text=task.custom_text)

    def stop_all(self):
        self.shut_down = True
        self.shut_down_event.set()



async def run_wallet_server():
    server: WalletServer = await WalletServer.create_web_server()
    await server.shut_down_event.wait()


def main():
    asyncio.run(run_wallet_server())


if __name__ == "__main__":
    try:
        main()
    except Exception:
        tb = traceback.format_exc()
        print(f"Error in Web Server. {tb}")
        raise
