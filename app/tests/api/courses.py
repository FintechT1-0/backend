from fastapi.testclient import TestClient


def create_course(client: TestClient, token: str, course: dict): 
    return client.post("/courses/", json=course, headers={
        "Authorization": f"Bearer {token}"
    })


def patch_course(client: TestClient, token: str, id: int, changes: dict):
    return client.patch(f"/courses/{id}", json=changes, headers={
        "Authorization": f"Bearer {token}"
    })


def delete_course(client: TestClient, token: str, id: int):
    return client.delete(f"/courses/{id}", headers={
        "Authorization": f"Bearer {token}"
    })


def get_course(client: TestClient, token: str, id: int):
    return client.get(f"/courses/{id}", headers={
        "Authorization": f"Bearer {token}"
    })


def get_courses(client: TestClient, token: str, query: str = ""):
    return client.get(f"/courses?{query}", headers={
        "Authorization": f"Bearer {token}"
    })