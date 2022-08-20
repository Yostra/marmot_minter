import os
import time
from typing import Any, List, Optional

from chia.wallet.models import db, MintTask


class DatabaseApi:
    max_timestamp: int
    host: str
    port: int
    user: str
    database: str
    url: str
    password: str
    _database: Any

    def set_start_time(self, start):
        self.start_time = start

    @staticmethod
    async def create_api():
        self = DatabaseApi()

        self.mode = os.getenv("MODE")
        self.host = os.getenv("DB_HOST")
        self.port = int(os.getenv("DB_PORT"))
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASS")
        self.database = os.getenv("DB_NAME")

        self.url = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

        self.max_timestamp = 1893474000  # 01/01/2030 timestamp
        self._database = db
        await self._database.set_bind(self.url)

        # await self._database.gino.create_all()
        return self

    async def get_mint_id(self):
        ordering = MintTask.marmot_id.desc()
        posts: List[MintTask] = (
            await MintTask.query.order_by(ordering).offset(0).limit(1).gino.all()
        )
        post = posts[0]
        return post.marmot_id + 1

    async def get_mint_task(self, parent_id) -> Optional[MintTask]:
        task = await MintTask.query.where(MintTask.parent_id == parent_id).gino.one_or_none()
        return task

    async def create_mint_task(self, parent_id: str, to_puzzle_hash: str, custom_text: str):
        marmot_id = await self.get_mint_id()
        mint = await MintTask.create(
            marmot_id = marmot_id,
            to_address = to_puzzle_hash,
            status =0,
            custom_text=custom_text,
            valid_from = int(time.time()),
            parent_id=parent_id,
            valid_to = self.max_timestamp
        )
        return mint

    async def get_pending_tasks(self) -> List[MintTask]:
        ordering = MintTask.marmot_id.asc()
        tasks = await MintTask.query.order_by(ordering).where(MintTask.status == 0).gino.all()
        return tasks
