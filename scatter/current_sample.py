from scatter.main import save, flush


def sample_1(i, j):
    return i + j * 2


def sample_2(i, j):
    return i - j


save(sample_1)
# save(sample_2)
# flush()
