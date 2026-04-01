import pytest
from backend.models import ProfileORM, TweetORM, LikeORM


@pytest.mark.asyncio
async def test_get_my_profile(client, session):
    user = ProfileORM(
        name="TestUser",
        api_key="test"
    )
    session.add(user)
    await session.commit()

    response = await client.get("/api/users/me", headers={"api-key": "test"})
    data = response.json()
    assert response.status_code == 200
    assert data == {
        'result': 'true',
        'user': {
            'id': 1,
            'name': 'TestUser',
            'followers': [],
            'following': []
        }}


@pytest.mark.asyncio
async def test_get_profile_by_id(client, session):
    user_1 = ProfileORM(
        name="TestUser1",
        api_key="test1"
    )
    user_2 = ProfileORM(
        name="TestUser2",
        api_key="test"
    )
    session.add(user_1)
    session.add(user_2)
    await session.commit()

    response = await client.get("/api/users/1", headers={"api-key": "test"})
    data = response.json()

    assert response.status_code == 200
    assert data == {
        'result': 'true',
        'user': {
            'id': 1,
            'name': 'TestUser1',
            'followers': [],
            'following': []
        }}


@pytest.mark.asyncio
async def test_delete_follow_in_user(session, client):
    user_1 = ProfileORM(
        name="TestUser1",
        api_key="test1"
    )
    user_2 = ProfileORM(
        name="TestUser2",
        api_key="test"
    )
    session.add(user_1)
    session.add(user_2)
    await session.commit()

    response = await client.delete("/api/delete/1/follow", headers={"api-key": "test"})
    data = response.json()

    assert data == {"result": "true"}


@pytest.mark.asyncio
async def test_create_follow_on_user(session, client):
    user_1 = ProfileORM(
        name="TestUser1",
        api_key="test1"
    )
    user_2 = ProfileORM(
        name="TestUser2",
        api_key="test"
    )
    session.add(user_1)
    session.add(user_2)
    await session.commit()

    response = await client.post("/api/users/1/follow", headers={"api-key": "test"})
    data = response.json()

    assert response.status_code == 201
    assert data == {"result": "true"}


@pytest.mark.asyncio
async def test_get_all_tweets(client, session):
    user = ProfileORM(
        name="TestUser",
        api_key="test"
    )

    session.add(user)
    await session.commit()

    tweet = TweetORM(
        content="great tweet",
        author_id=1
    )
    session.add(tweet)
    await session.commit()

    like = LikeORM(
        user_id=1,
        tweet_id=1
    )
    session.add(like)
    await session.commit()

    response = await client.get("/api/tweets", headers={"api-key": "test"})
    data = response.json()

    assert response.status_code == 200
    assert data == {
            "result": "true",
            "tweets": [{
                "id": 1,
                "content": "great tweet",
                "attachments":[],
                "author": {
                    "id": 1,
                    "name": "TestUser"
                },
                "likes":[{
                    "user_id": 1,
                    "name": "TestUser"
                }]
            }]
        }


@pytest.mark.asyncio
async def test_create_tweet(session, client):
    user = ProfileORM(
        name="TestUser",
        api_key="test"
    )
    session.add(user)
    await session.commit()

    response = await client.post(
        "/api/tweets",
        json={
            "tweet_data": "great tweet"
        },
        headers={"api-key": "test"}
    )
    data = response.json()

    assert response.status_code == 201
    assert data == {"result": "true", "tweet_id": 1}


@pytest.mark.asyncio
async def test_delete_my_tweet(session, client):
    user = ProfileORM(
        name="TestUser",
        api_key="test"
    )
    session.add(user)
    await session.commit()

    tweet = TweetORM(
        content="great tweet",
        author_id=1
    )
    session.add(tweet)
    await session.commit()

    response = await client.delete("/api/tweets/1", headers={"api-key": "test"})
    data = response.json()

    assert response.status_code == 200
    assert data == {"result": "true"}


@pytest.mark.asyncio
async def test_add_like_on_tweet(session, client):
    user = ProfileORM(
        name="TestUser",
        api_key="test"
    )
    session.add(user)
    await session.commit()

    tweet = TweetORM(
        content="great tweet",
        author_id=1,
    )
    session.add(tweet)
    await session.commit()

    response = await client.post("/api/tweets/1/likes", headers={"api-key": "test"})
    data = response.json()

    assert response.status_code == 201
    assert data == {"result": "true"}


@pytest.mark.asyncio
async def test_delete_like_on_tweet(session, client):
    user = ProfileORM(
        name="TestUser",
        api_key="test"
    )
    session.add(user)
    await session.commit()

    tweet = TweetORM(
        content="great tweet",
        author_id=1,
    )
    session.add(tweet)
    await session.commit()

    like = LikeORM(
        user_id=1,
        tweet_id=1
    )
    session.add(like)
    await session.commit()

    response = await client.delete("/api/tweets/1/likes", headers={"api-key": "test"})
    data = response.json()

    assert data == {"result": "true"}