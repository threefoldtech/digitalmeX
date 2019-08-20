import gevent


def main(self, start=True, count=100):
    self.workers_nr_max = count
    if start:
        self.start()

    def wait_1sec():
        import time

        gevent.sleep(1)
        return "OK"

    ids = []
    for x in range(count):
        ids.append(self.schedule(wait_1sec))

    res = self.results(ids)

    print("TESTOK")
