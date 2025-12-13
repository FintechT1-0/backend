admin_required = {
    401: {
        "description": "Authorization (admin) is required for this endpoint. For greater detail, check the error."
    }
}

user_required = {
    401: {
        "description": "Authorization (user) is required for this endpoint. For greater detail, check the error."
    }
}

privilege_required = {
    403: {
        "description": "Privileges are required for this endpoint. For greater detail, check the error."
    }
}

def either(*args):
    result = f"Either of {len(args)} conditions:\n"
    for i, arg in enumerate(args, start=1):
        result += f"{i}. {arg}\n"
    return result