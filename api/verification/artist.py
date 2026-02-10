import pandas as pd
from rapidfuzz.process import cdist

from books.models import AuthorModel
from mixins.database import SessionLocal


def main():
    db = SessionLocal()
    author = db.query(AuthorModel).all()

    data_1 = [i.name for i in author ]
    data_2 = [i.name for i in author ]

    similarity_fast = cdist(data_1, data_2, workers=-1)
    print(similarity_fast)


    similarity_fast = pd.DataFrame({
        'master': data_1,
        'transaction': data_2,
        'ratio': similarity_fast.max(axis=1) / 100
    })
    print(similarity_fast)
