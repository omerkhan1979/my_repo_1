from exrex import getone


def generate_target_tote():
    # tote for outbound operations (orders)
    return getone("998[0-9]{11}")


def generate_storage_tote():
    # a.k.a "source tote" - for decanting
    return getone("1[0-9]{7}1[0-9]{1}")
