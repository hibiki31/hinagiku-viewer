import re


class ParseResult:
    """ファイル名パース結果を保持するクラス"""
    def __init__(self, publisher, author, title):
        self.publisher = publisher
        self.author = author
        self.title = title


def old_parser(text):
    """旧形式のファイル名パーサー（後方互換性のため保持）"""
    publisher = re.findall(r'^\((.*?)\).*', text)
    if len(publisher) == 0:
        publisher = None
    else:
        publisher = publisher[0]

    author = re.sub(r'.*\[(.*?)\].*', r'\1', text)
    text = re.sub(r'.*\[(.*?)\](.*)', r'\2', text)

    title = re.sub(r'\.zip', r'', text)
    title = re.sub(r'^ ', r'', title)

    print({'publisher': publisher, 'author': author, 'title': title})


def parse_filename(text):
    """
    ファイル名から書籍メタデータをパースする

    フォーマット: (出版社) [著者] タイトル.zip
    例: (Publisher) [Author] Title.zip

    Args:
        text: パースするファイル名

    Returns:
        ParseResult: パース結果
    """
    res = re.findall(r'^(\((.*?)\))? ?(\[(.*?)\])? ?(.*?)(\.zip)?$', text)
    return ParseResult(publisher=res[0][1], author=res[0][3], title=res[0][4])


def get_model_dict(model):
    """SQLAlchemyモデルを辞書に変換する"""
    return {column.name: getattr(model, column.name)
            for column in model.__table__.columns
        }


def book_result_mapper(rows):
    """
    書籍クエリ結果をAPIレスポンス用に整形する

    Args:
        rows: SQLAlchemyクエリ結果

    Returns:
        list: 整形された結果リスト
    """
    result = []
    for row in rows:
        dic = row[0].__dict__
        if dic["user_data"] != []:
            dic["user_data"] = dic["user_data"][0].__dict__
        else:
            dic["user_data"] = {"rate": None}
        result.append(dic)
    return result


if __name__ == "__main__":
    print(parse_filename("aa"))
    print(parse_filename("[] aa"))
