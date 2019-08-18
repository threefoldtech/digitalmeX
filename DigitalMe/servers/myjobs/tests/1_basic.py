from Jumpscale import j


def main(self):
    """
    kosmos 'j.servers.myjobs.test("basic")'
    """

    j.tools.logger.debug = True

    self.reset()

    def add(a, b):
        return a + b

    jobid = self.schedule(add, 1, 2)
    assert isinstance(jobid, int)

    self.worker_start(onetime=True)

    res = self.results([jobid])

    j.shell()

    print(res)

    print("Basic Done")

    print("**DONE**")
