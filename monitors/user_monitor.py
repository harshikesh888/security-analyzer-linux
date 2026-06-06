def get_users():

    users = []

    with open("/etc/passwd") as f:
        for line in f:
            users.append(
                line.split(":")[0]
            )

    return users
