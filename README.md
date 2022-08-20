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

You will have to create open ai dalle account and get authorization token, replace it in marmot_get.py
```
  bearer = "Bearer sess-xxxx"
 ```

### make sure to have a local wallet running & is synced

### Run the minter by doing: python chia/wallet/marmot_server.py



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
