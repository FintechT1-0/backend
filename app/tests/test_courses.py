from fastapi.testclient import TestClient
from app.tests.api.auth import get_user, get_admin
from app.tests.data.courses import *
from app.tests.api.courses import *
from loguru import logger


def test_course_flow(client: TestClient):
    admin = get_admin(client)

    created = create_course(client, admin["token"], COURSE)
    assert created.status_code == 200

    course_id = created.json()["id"]

    patched = patch_course(client, admin["token"], course_id, COURSE_PATCH)
    assert patched.status_code == 200

    patched_course = patched.json()
    for key in COURSE_PATCH.keys():
        assert patched_course[key] == COURSE_PATCH[key]

    got_by_id = get_course(client, admin["token"], course_id)
    assert got_by_id.status_code == 200 

    deleted = delete_course(client, admin["token"], course_id)
    assert deleted.status_code == 204

    got_nothing_by_id = get_course(client, admin["token"], course_id)
    assert got_nothing_by_id.status_code == 404


def test_rights(client: TestClient):
    admin = get_admin(client)
    user = get_user(client)

    created = create_course(client, admin["token"], COURSE)
    created_unpublished = create_course(client, admin["token"], COURSE_UNPUBLISHED)

    course_id = created.json()["id"]
    unpublished_id = created_unpublished.json()["id"]

    user_patch = patch_course(client, user["token"], course_id, COURSE_PATCH)
    assert user_patch.status_code == 403

    user_create = create_course(client, user["token"], COURSE)
    assert user_create.status_code == 403

    user_delete = delete_course(client, user["token"], course_id)
    assert user_delete.status_code == 403

    user_get_unpublished = get_course(client, user["token"], unpublished_id)
    assert user_get_unpublished.status_code == 403

    user_filter_unpublished = get_courses(client, user["token"], "isPublished=false")
    assert user_filter_unpublished.status_code == 403


def test_query(client: TestClient):
    admin = get_admin(client)

    create_course(client, admin["token"], COURSE)
    create_course(client, admin["token"], COURSE_UNPUBLISHED)
    create_course(client, admin["token"], COURSE_EN)

    all_courses = get_courses(client, admin["token"], "")
    assert all_courses.status_code == 200
    assert all_courses.json()["page_size"] == 3

    for key in [k for k in COURSE.keys() if k != "price" and k != "tags"]:
        logger.debug(f"Testing filtering courses for {key}, value = {COURSE[key]}")
        filtered = get_courses(client, admin["token"], f"{key}={COURSE[key]}")
        assert filtered.status_code == 200
        assert filtered.json()["page_size"] > 0
    
    filtered_price = get_courses(client, admin["token"], f"price_min={COURSE['price'] - 5}&price_max={COURSE['price'] + 5}")
    assert filtered_price.status_code == 200
    assert filtered_price.json()["page_size"] == 1

    filtered_tags = get_courses(client, admin["token"], "&".join(f"tags={tag}" for tag in COURSE['tags']) + "&tags=en")
    assert filtered_tags.status_code == 200
    assert filtered_tags.json()["page_size"] == 2