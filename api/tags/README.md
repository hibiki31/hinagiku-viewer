

## 


```sql
SELECT 
    tags.id, tags.name, users_1.id AS id_1, users_1.password, users_1.is_admin, librarys_1.id AS id_2, librarys_1.name AS name_1, librarys_1.user_id, genres_1.id AS id_3, genres_1.name AS name_2, publishers_1.id AS id_4, publishers_1.name AS name_3, series_1.id AS id_5, series_1.name AS name_4, authors_1.id AS id_6, authors_1.name AS name_5, authors_1.description, book_metadatas_1.user_id AS user_id_1, book_metadatas_1.book_uuid, book_metadatas_1.last_open_date, book_metadatas_1.read_times, book_metadatas_1.open_page, book_metadatas_1.rate, books_1.uuid, books_1.user_id AS user_id_2, books_1.size, books_1.sha1, books_1.page, books_1.add_date, books_1.file_date, books_1.import_file_name, books_1.title, books_1.series_no, books_1.library_id, books_1.genre_id, books_1.publisher_id, books_1.series_id, books_1.is_shered, books_1.state 
FROM tags LEFT OUTER JOIN (tag_to_book AS tag_to_book_1 JOIN books AS books_1 ON books_1.uuid = tag_to_book_1.book_uuid) ON tags.id = tag_to_book_1.tags_id LEFT OUTER JOIN librarys AS librarys_1 ON librarys_1.id = books_1.library_id LEFT OUTER JOIN (library_to_user AS library_to_user_1 JOIN users AS users_1 ON users_1.id = library_to_user_1.user_id) ON librarys_1.id = library_to_user_1.library_id LEFT OUTER JOIN genres AS genres_1 ON genres_1.id = books_1.genre_id LEFT OUTER JOIN publishers AS publishers_1 ON publishers_1.id = books_1.publisher_id LEFT OUTER JOIN series AS series_1 ON series_1.id = books_1.series_id LEFT OUTER JOIN (book_to_author AS book_to_author_1 JOIN authors AS authors_1 ON authors_1.id = book_to_author_1.author_id) ON books_1.uuid = book_to_author_1.book_uuid LEFT OUTER JOIN book_metadatas AS book_metadatas_1 ON books_1.uuid = book_metadatas_1.book_uuid 
WHERE EXISTS (SELECT 1 FROM books, tag_to_book WHERE tags.id = tag_to_book.tags_id AND books.uuid = tag_to_book.book_uuid AND books.user_id = :user_id_3)
```


## 多対多リレーション時のフィルタ

```python
query = db.query(TagsModel).filter(TagsModel.books.any(user_id=current_user.id))
```

```sql
SELECT tags.id, tags.name 
FROM tags 
WHERE EXISTS (
    SELECT 1 
    FROM books, tag_to_book 
    WHERE tags.id = tag_to_book.tags_id AND books.uuid = tag_to_book.book_uuid AND books.user_id = :user_id_1
)
```