from scatter.main import scatter


@scatter
def sample_1(i, j):
    return i + j * 2


def sample_2(i, j):
    return i - j

sample_1.save()
# save(sample_2)
