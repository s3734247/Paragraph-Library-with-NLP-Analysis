import sqlalchemy as _sa
from app import db, logger

class PostManager(object):
    TABLE = "Post join Author on Post.author_id = Author.id"
    FIELDS = "Post.id as post_id, Post.*, Author.*"

    @property
    def conn(self):
        return db.connect()

    def get_one(self, post_id):
        sql = f"select {self.FIELDS} from {self.TABLE} where Post.id = :post_id"
        stmt = _sa.text(sql).bindparams(post_id=post_id)
        result = None
        with self.conn as conn:
            result = conn.execute(stmt)
        for r in result:
            # only returns the first
            return self.transformRow(r)
        return None

    def get_many(self, filt: dict) -> list:
        sql = f"select {self.FIELDS} from {self.TABLE}"
        if len(filt) > 0:
            sql += " where "
        conds = []
        for k in filt.keys():
            if k == "post_id":
                conds.append(f"Post.id = :{k}")
            elif k == "id":
                conds.append(f"Post.id = :{k}")
            elif k in ("sentiment_score", "sentiment_magnitude"):
                conds.append(f"abs({k} - :{k}) <= 0.1")
            else:
                conds.append(f"{k} = :{k}")
        sql += " and ".join(conds)
        stmt = _sa.text(sql).bindparams(**filt)
        result = None
        with self.conn as conn:
            result = conn.execute(stmt)
        return [self.transformRow(r) for r in result]

    @staticmethod
    def transformRow(row):
        d = dict(row)
        d.pop("id")
        return d
        
