import uvicorn
import logging
from fastapi import FastAPI, Header, status, HTTPException, File, UploadFile
from sqlalchemy import select, delete, insert
from sqlalchemy.orm import selectinload

from .models import (
    ProfileORM,
    follow_association_table,
    TweetORM,
    LikeORM,
    MediaORM
)
from .schemas import CreateTweetSchema
from .conf import SessionDep, lifespan


logger = logging.getLogger(__name__)

app = FastAPI(lifespan=lifespan)


@app.get("/api/users/me", status_code=status.HTTP_200_OK)
async def get_my_profile(
        session: SessionDep,
        api_key: str = Header(...)
) -> dict:

    get_profile = await session.execute(select(ProfileORM).options(
        selectinload(ProfileORM.followers),
        selectinload(ProfileORM.following)
    ).where(ProfileORM.api_key == api_key)
            )

    profile = get_profile.scalar_one_or_none()
    if profile:
        logger.info("Успешный запрос на данные профиля пользователя!")
        return {
            "result": "true",
            "user":{
                "id": profile.id,
                "name": profile.name,
                "followers": [{
                    "id": user.id,
                    "name": user.name,
                } for user in profile.followers ],
                'following': [{
                   "id": user.id,
                    "name": user.name
                } for user in profile.following ],
            }
        }

    logger.exception("Не найден пользователь по запросу!")
    return {"result": "false"}


@app.get("/api/users/{user_id}", status_code=status.HTTP_200_OK)
async def get_profile_by_id(
        user_id: int,
        session: SessionDep,
) -> dict:

    get_profile = await session.execute(select(ProfileORM).options(
        selectinload(ProfileORM.followers),
                selectinload(ProfileORM.following))
                .where(ProfileORM.id == user_id)
            )

    profile = get_profile.scalar_one_or_none()
    if profile:
        logger.info("Успешный запрос на данные профиля пользователя!")
        return {
                "result": "true",
                "user" :{
                    "id": profile.id,
                    "name": profile.name,
                    "followers": [{
                        "id": user.id,
                        "name": user.name,
                    } for user in profile.followers ],
                    "following": [{
                       "id": user.id,
                        "name": user.name
                    } for user in profile.following ],
                }
            }

    logger.exception("Не найден пользователь по запросу!")
    return {"result": "false"}


@app.delete("/api/delete/{user_id}/follow")
async def delete_follow_in_user(
        user_id: int,
        session: SessionDep,
        api_key: str = Header(...)
) -> dict:
    get_profile = await session.execute(select(ProfileORM.id).where(ProfileORM.api_key == api_key))
    my_id = get_profile.scalar_one_or_none()

    if my_id is None or user_id == my_id:
        logger.exception("Не найден id пользователя, или не корректный id!")
        return {"result": "false"}

    try:
        delete_follow = (delete(follow_association_table)
                         .where(follow_association_table.c.following_id==user_id,
                                follow_association_table.c.followers_id ==my_id
                         ))

        await session.execute(delete_follow)
        await session.commit()

        logger.info("Попытка отписки от пользователя была выполнена успешно!")
        return {"result": "true"}

    except HTTPException:
        logger.exception("Попытка отписки от пользователя была провалена!")
        return {"result": "false"}


@app.post("/api/users/{user_id}/follow", status_code=status.HTTP_201_CREATED)
async def create_follow_on_user(
        user_id: int,
        session: SessionDep,
        api_key: str = Header(...)
) -> dict:

    get_profile = await session.execute(
        select(ProfileORM.id).where(ProfileORM.api_key == api_key)
    )
    my_id = get_profile.scalar_one_or_none()

    if my_id is None or my_id == user_id:
        logger.exception("Не найден id пользователя, или не корректный id!")
        return {"result": "false"}

    try:
        create_follow = insert(follow_association_table).values(
            following_id=user_id,
            followers_id=my_id
        )

        await session.execute(create_follow)
        await session.commit()

        logger.info("Попытка подписки на пользователя прошла успешно!")
        return {"result": "true"}

    except HTTPException:
        logger.exception("Попытка подписки на пользователя была провалена!")
        return {"result": "false"}


@app.get("/api/tweets")
async def get_all_tweets(
        session: SessionDep
) -> dict:

    get_tweets = await session.execute(select(TweetORM).options(selectinload(TweetORM.author)))
    get_likes = await session.execute(
        select(LikeORM).options(
            selectinload(LikeORM.tweet),
            selectinload(LikeORM.user),
        ))

    tweets = get_tweets.scalars().all()
    if tweets:
        likes = get_likes.scalars().all()
        likes_dict = {}
        for like in likes:
            likes_dict.setdefault(like.tweet_id, []).append(like)

        logger.info("Попытка запроса данных на твиты прошла успешно!")
        return {
            "result": "true",
            "tweets": [{
                "id": tweet.id,
                "content": tweet.content,
                "attachments":[],
                "author": {
                    "id": tweet.author.id,
                    "name": tweet.author.name
                },
                "likes":[{
                    "user_id": like.user.id,
                    "name": like.user.name
                } for like in likes_dict.get(tweet.id, [])]
            } for tweet in tweets]
        }

    logger.exception("Попытка запроса на твиты была провалена!")
    return {
        "result": "false",
        "error_type": "ValueError",
        "error_message": "Попытка запроса на данные твитов была провалена!"
    }


@app.post("/api/tweets", status_code=status.HTTP_201_CREATED)
async def create_tweet(
        session: SessionDep,
        schema: CreateTweetSchema,
        api_key: str = Header(...)
) -> dict:

    get_my_id = await session.execute(select(ProfileORM.id).where(ProfileORM.api_key == api_key))
    my_id = get_my_id.scalar_one_or_none()

    if my_id:
        tweet = TweetORM(
                author_id=my_id,
                content=schema.tweet_data
            )
        session.add(tweet)
        await session.commit()

        logger.info("Попытка создания нового твита прошла успешно!")
        return {"result": "true", "tweet_id": tweet.id}

    logger.exception("Попытка создания нового твита была провалена!")
    return {"result": "false"}


@app.delete("/api/tweets/{tweet_id}")
async def delete_my_tweet(
        tweet_id: int,
        session: SessionDep,
) -> dict:

    get_tweet = await session.execute(
        select(TweetORM).options(
            selectinload(TweetORM.author)
        ).where(TweetORM.id == tweet_id)
    )
    tweet = get_tweet.scalar_one_or_none()
    if tweet:
        await session.delete(tweet)
        await session.commit()

        logger.info("Попытка удаления твита прошла успешно!")
        return {"result": "true"}

    logger.exception("Попытка удаления твита была провалена!")
    return {"result": "false"}


@app.post("/api/tweets/{tweet_id}/likes", status_code=status.HTTP_201_CREATED)
async def add_like_on_tweet(
        tweet_id: int,
        session: SessionDep,
        api_key: str = Header(...)
) -> dict:

    get_my_id = await session.execute(select(ProfileORM.id).where(ProfileORM.api_key == api_key))
    my_id = get_my_id.scalar_one_or_none()

    if my_id:

        like = LikeORM(
            user_id=my_id,
            tweet_id=tweet_id
        )
        session.add(like)
        await session.commit()

        logger.info("Попытка установления отметки нравится прошла успешно!")
        return {"result": "true"}

    logger.exception("Попытка установления отметки нравится была провалена!")
    return {"result": "false"}


@app.delete("/api/tweets/{tweet_id}/likes")
async def delete_like_on_tweet(
        tweet_id: int,
        session: SessionDep,
        api_key: str = Header(...)
) -> dict:

    get_my_id = await session.execute(select(ProfileORM.id).where(ProfileORM.api_key == api_key))
    my_id = get_my_id.scalar_one_or_none()
    if my_id:

        get_likes = await session.execute(
            select(LikeORM).options(
                selectinload(LikeORM.user),
                selectinload(LikeORM.tweet)
            ).where(LikeORM.user_id == my_id, LikeORM.tweet_id == tweet_id)
        )
        like = get_likes.scalar_one_or_none()

        if like:
            await session.delete(like)
            await session.commit()
            logger.info("Попытка удаления отметки нравится прошла успешно!")
            return {"result": "true"}

    logger.exception("Попытка удаления отметки нравится была провалена!")
    return {"result": "false"}


@app.post("/api/medias")
async def upload_media_file(
        session: SessionDep,
        file: UploadFile = File(...),
):
    content = await file.read()

    my_file = MediaORM(
        title=file.filename,
        content_type=file.content_type,
        data=content
    )
    session.add(my_file)
    await session.commit()

    return {"result": "true", "media_id": my_file.id}


if __name__ == "__main__":
    uvicorn.run("clone_twitter:app", host="0.0.0.0", port=8000)