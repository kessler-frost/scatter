from scatter import scatter


@scatter
def sample_1(i, j):
    return i + j


@scatter
def sample_2(i, j):
    return "i - j"

@scatter
def sample_task():
    return "poop"

# sample_1.push()
# sample_2.push()
sample_task.push()
