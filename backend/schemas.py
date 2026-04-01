from pydantic import BaseModel


class CreateTweetSchema(BaseModel):
    """
        CreateTweetSchema - форма для создания твита.
    """
    tweet_data: str