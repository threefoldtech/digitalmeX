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

    # means work scheduled
    assert self.scheduled_ids == [jobid]

    self.worker_start(onetime=True)
    assert self.scheduled_ids == [jobid]

    res = self.results()

    v = [i for i in res.values()]
    assert len(res.values()) == 1
    assert v[0] == str(3)

    jobid = self.schedule(add, 3, 4)

    self.worker_start(onetime=True)

    res = self.results([jobid])
    v = [i for i in res.values()]
    assert v[0] == str(7)

    print(res)

    print("Basic Done")

    print("**DONE**")
