from gino import Gino

db = Gino()
import logging
logging.basicConfig()
logging.getLogger("gino.engine._SAEngine").setLevel(logging.ERROR)



class DBJSON(db.Model):
    def __repr__(self):
        return str(self.to_dict())

class MintTask(db.Model):  # type: ignore # noqa
    __tablename__ = "mint_task"

    id = db.Column(db.Integer(), primary_key=True)
    marmot_id = db.Column(db.Integer(), nullable=False, unique=True)
    marmot_image_url = db.Column(db.Text(), nullable=True)
    marmot_ipfs_url = db.Column(db.Text(), nullable=True)
    to_address = db.Column(db.Text(), nullable=False)
    custom_text = db.Column(db.Text(), nullable=True, default="")
    parent_id = db.Column(db.Text(), nullable=False)
    status = db.Column(db.Integer(), nullable=False)
    valid_from = db.Column(db.Integer(), nullable=False)
    valid_to = db.Column(db.Integer(), nullable=False)

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

db.Index("index_MintTask_valid_from", MintTask.valid_from)
db.Index("index_MintTask_valid_to", MintTask.valid_to)
db.Index("index_MintTask_address", MintTask.to_address)
db.Index("index_MintTask_status", MintTask.status)
db.Index("index_MintTask_marmot_id", MintTask.marmot_id)
