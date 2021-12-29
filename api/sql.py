from mixins.database import SessionLocal
from sqlalchemy import func, select, join, table, literal_column, text


def select_books(user_id, title=None, limit=2):
    db = SessionLocal()

    book = select("*").limit(limit).select_from(table('books'))
    if title:
        book = book.where(literal_column('title').like(f'%{title}%'))
    
    book = book.alias('book')

    meta = select(
            "*"
        ).select_from(
            table('book_metadatas')
        ).where(
            literal_column('user_id') >= user_id
        ).alias('meta')
    
    pub = table('publishers').alias('pub')

    book_to_aut = table('book_to_author').alias('book_to_aut')

    aut = table('authors').alias('aut')
    
    main_query = select([
            literal_column('book.uuid').label('uuid'),
            literal_column('book.page').label('page'),
            literal_column('book.title').label('title'),
            literal_column('meta.rate').label('metadata_rate'),
            literal_column('pub.name').label('pub_name'),
            literal_column('pub.id').label('pub_id'),
            literal_column('aut.name').label('author_name'),
            literal_column('aut.id').label('author_id')
        ]).select_from(
        book.outerjoin(
            meta, text('book.uuid = meta.book_uuid')
        ).outerjoin(
            pub, text('book.publisher_id = pub.id')
        ).outerjoin(
            book_to_aut, text('book.uuid = book_to_aut.book_uuid')
        ).outerjoin(
            aut, text('book_to_aut.author_id = aut.id')
        )
    )

    import pprint

    print(main_query)

    vle = db.execute(main_query).fetchall()
    clm = db.execute(main_query).keys()

    

    for i in vle:
        dc = dict(zip(clm , vle))

    pprint.pprint(dc)



if __name__  == '__main__':
    select_books(user_id='akane')