This is the minting tool used for generating the Marmot World Order (MWO) NFT collection using [DALL-E](https://openai.com/blog/dall-e/).

## Setup Instructions

### Place these files in the `chia/wallet/` directory
### Install additional dependencies 
```
pip install openai
pip install git+https://github.com/nftstorage/python-client.git
pip install gino
```

### You will need PostgreSQL databse
You can run this [PostgreSQL](PostgreSQL) db locally.

### Set ENV variable so that marmot_db_api.py can connect to the database

```
self.mode = os.getenv("MODE")
self.host = os.getenv("DB_HOST")
self.port = int(os.getenv("DB_PORT"))
self.user = os.getenv("DB_USER")
self.password = os.getenv("DB_PASS")
self.database = os.getenv("DB_NAME")
```

### Customize collection info
You will have to create an [NFT.Storage](https://nft.storage/) account and get an api key.

Edit this section in the `marmot_server.py` file:

```
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
```

You will have to create an Open AI account, get access to DALL-E, and get authorization token. Put this token in marmot_get.py
```
  bearer = "Bearer sess-xxxx"
 ```

### Make sure you have local wallet running and that it is synced

### Run the minter
```python
python chia/wallet/marmot_server.py
```

---

MIT License

Copyright (c) Yostra

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.