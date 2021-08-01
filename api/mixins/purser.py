import re
from books.models import BookUserMetaDataModel

class PurseResult():
    def __init__(self, publisher, author, title):
        self.publisher = publisher
        self.author = author
        self.title = title

def old_purser(text):
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


def base_purser(text):
    res = re.findall(r'^(\((.*?)\))? ?(\[(.*?)\])? ?(.*?)(\.zip)?$', text)
    return PurseResult(publisher=res[0][1], author=res[0][3], title=res[0][4])


def get_model_dict(model):
    return dict((
                column.name, 
                getattr(model, column.name)
            )
            for column in model.__table__.columns
        )

def book_result_mapper(rows):
    result = []
    for row in rows:
        dic = row[0].__dict__
        if dic["user_data"] != []:
            dic["user_data"] = dic["user_data"][0].__dict__
            # del dic["user_data"]["book_uuid"], dic["user_data"]["user_id"]
        result.append(dic)
    return result
    
if __name__ == "__main__":
    print(base_purser("aa"))
    print(base_purser("[] aa"))
