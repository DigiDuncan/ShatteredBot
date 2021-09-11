ok_roles = ["Owner And plant.", "Digimon", "TW"]


def is_dm(user) -> bool:
    for role in ok_roles:
        if role in user.rolelist:
            return True
    return False
