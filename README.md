### Place these file in `chia/wallet/` directory
### install additional deps
```pip install openai
pip install git+https://github.com/nftstorage/python-client.git
pip install gino
```

### You will need postgresql db, you can run it locally

### Set ENV variable so that marmot_db_api.py can connect to the db

```self.mode = os.getenv("MODE")
self.host = os.getenv("DB_HOST")
self.port = int(os.getenv("DB_PORT"))
self.user = os.getenv("DB_USER")
self.password = os.getenv("DB_PASS")
self.database = os.getenv("DB_NAME")
```

### Customize you collection/wallet info/ did stuff in marmot_server.py
You will have to create https://nft.storage/ account anf get api key

```RECEIVE_ADDRESS = "xch..."
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
```

### make sure to have a local wallet running & is synced

### Run the minter by doing: python chia/wallet/marmot_server.py
