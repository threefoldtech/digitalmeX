from Jumpscale import j


def main(self):
    """
    kosmos 'j.servers.myjobs.test("simple_error")'
    """

    j.tools.logger.debug = True

    self.reset()

    def add(a, b):
        raise ValueError("aaa")
        return a + b

    job = self.schedule(add, 1, 2)

    error = False
    try:
        self.worker_start(onetime=True)
    except Exception as e:
        error = True
        j.shell()

    assert error

    print(self.results([job]))

    self._log_info("basic error test done")
