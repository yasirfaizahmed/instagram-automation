from attributedict.collections import AttributeDict


comment = AttributeDict({
    "text": "",
    "id": "",
    "parent_id": "",
    "user_id": "",
    "likes": ""
})

media = AttributeDict({
    "id": "",
    "caption": "",
    "user_id": "",
    "likes": "",
    "comments": [comment]
})

user = AttributeDict({
    "id": "",
    "username": "",
    "bio": "",
    "followers": "",
    "following": "",
    "medias": [media]
})

COMMENT_TEMPLATE = \
    {
        "H":
        {
            "M1":
            {

            }
        }
    }
