import inspect
from Jumpscale import j
import gipc
import gevent
import time
import sys
from .MyWorker import MyWorker

JSBASE = j.application.JSBaseClass

schema_job = """
@url = jumpscale.myjobs.job
category*= ""
time_start = 0 (T)
time_stop = 0 (T)
state* = "new,error,ok" [E]
timeout = 0
action_id* = 0
args = ""   #json
kwargs = "" #json
result = "" #json
error = ""
return_queues = (LS)


"""

schema_action = """
@url = jumpscale.myjobs.action
actorname = ""
methodname = ""
key* = ""  #hash    
code = ""


"""

# NOT THE FASTEST WAY TO KEEP STATE OF WORKER BETWEEN THE PROCESSES, BUT EASY
schema_worker = """
@url = jumpscale.myjobs.worker
timeout = 3600
time_start = 0 (T)
last_update = 0 (T)
current_job = (I)
error = "" (S)
state* = "new,error,ok" [E]
pid = 0
halt = false (B)

"""


class MyJobs(JSBASE):
    __jslocation__ = "j.servers.myjobs"

    def _init(self):
        self.queue_jobs_start = j.clients.redis.queue_get(redisclient=j.core.db, key="queue:jobs:start")
        self.queue_return = j.clients.redis.queue_get(redisclient=j.core.db, key="queue:jobs:return")
        self.workers = {}
        self.workers_nr_min = 1
        self.workers_nr_max = 10
        self.mainloop = None
        self.dataloop = None
        self.model_job = None
        self.model_action = None
        self.model_worker = None
        self._init_ = False

    def init(self, reset=False):
        """
        activates the models and starts the worker manager if required
        """
        if self._init_ == False or reset:

            # if self.mainloop == None and  self.dataloop == None:
            #     from gevent import monkey
            #     monkey.patch_all()  #NEED TO BE VERY CAREFUL WITH THIS

            if self.mainloop != None:
                self.mainloop.kill()

            if self.dataloop != None:
                self.dataloop.kill()

            db = j.data.bcdb.get("myjobs", storclient=j.clients.rdb.client_get())

            self.model_job = db.model_get_from_schema(schema_job)
            self.model_action = db.model_get_from_schema(schema_action)
            self.model_worker = db.model_get_from_schema(schema_worker)

            if reset:
                self.halt(reset=True)

            self._init_ = True

    def action_get(self, key, return_none_if_not_exist=False):
        self.init()
        res = self.model_action.find(key=key)
        if len(res) > 0:
            o = self.model_action.get(res[0].id)
            return False, o
        else:
            if return_none_if_not_exist:
                return
            o = self.model_action.new()
            return True, o

    @property
    def workers_count(self):
        return len(self.workers.values())

    def start(self):
        """
        always in subprocess, cannot see the output
        will add worker(s) when needed, when there is more work

        :return:
        """
        self.init(reset=False)
        self.mainloop = gevent.spawn(self._main_loop)
        self.dataloop = gevent.spawn(self._data_loop)  # returns the data

    def worker_start(self, onetime=False, subprocess=True, worker_id=None):
        self.init()
        if onetime:
            subprocess = False
        if worker_id:
            w = self.model_worker.get(worker_id)
        else:
            w = self.model_worker.new()
            w.time_start = j.data.time.epoch
            w.last_update = j.data.time.epoch
            w = self.model_worker.set(w)
        self._log_debug("worker add: %s" % w.id, data=w._data)
        if subprocess:
            worker = gipc.start_process(target=MyWorker, args=(w.id,))
            self.workers[w.id] = worker
        else:
            excepthook_old = sys.excepthook
            MyWorker(w.id, onetime=onetime)
            # will make sure the data comes back
            self._data_process_untill_empty(timeout=5)
            sys.excepthook = excepthook_old

    def worker_start_inprocess(self, worker_id=None):
        """
        kosmos "j.servers.myjobs.worker_start_inprocess()"

        easy to debug the myworker framework because can see issues in the jobs executed

        :return:
        """
        self.worker_start(subprocess=False, worker_id=worker_id)

    def _data_loop(self):
        while True:
            self._log_debug("data_process run")
            self._data_process_1time(timeout=1)

    def _data_process_1time(self, timeout=0):
        r = self.queue_return.get(timeout=timeout)
        if r == None:
            return
        cat, objid, json_ = j.data.serializers.msgpack.loads(r)
        if cat not in ["E"]:
            ddict = j.data.serializers.json.loads(json_)
        if cat == "W":
            worker = self.model_worker.new(data=ddict)
            worker.id = objid
            worker.save()
            return worker
        elif cat == "J":
            job = self.model_job.new(data=ddict)
            job.id = objid
            job.save()
            for queue_name in job.return_queues:
                queue = j.clients.redis.getQueue(redisclient=j.core.db, name="myjobs:%s" % queue_name)
                queue.put(job.id)
            return job
        elif cat == "E":
            worker = self.model_worker.get(json_)
            j.core.tools.pprint(worker)
            sys.exit(1)
        else:
            raise RuntimeError("return queue does not have right obj")

    def _data_process_untill_empty(self, timeout=5):
        res = []

        # need to wait till first one comes
        r = self._data_process_1time(timeout=timeout)
        if not r:
            raise RuntimeError("timeout did not get data back")

        while r:
            r = self._data_process_1time(timeout=0)
        return res

    def _main_loop(self):

        self._log_debug("monitor start")

        def test_workers_more():
            workers_count = self.workers_count
            a = workers_count < self.workers_nr_max
            b = workers_count < self.queue_jobs_start.qsize() or workers_count < self.workers_nr_min
            return a and b

        def test_workers_less():
            workers_count = self.workers_count
            a = workers_count > self.workers_nr_max
            b = workers_count > self.queue_jobs_start.qsize() and workers_count > self.workers_nr_min
            return a or b

        while True:

            self._log_debug("monitor run")

            # #there is already 1 working, lets give 2 sec time before we start monitoring
            # time.sleep(2)

            # TEST for timeout
            wids = [key for key in self.workers.keys()]
            for wid in wids:
                if wid in self.workers:
                    gproc = self.workers[wid]
                else:
                    continue
                if gproc.exitcode != None:
                    raise RuntimeError("subprocess should never have been exitted")
                w = self.model_worker.get(wid)
                if w == None:
                    # should always find the worker
                    # j.shell()
                    continue

                job_running = w.current_job != 2147483647

                if job_running:
                    job = self.model_job.get(w.current_job)

                    if job != None and job.state != "OK" and j.data.time.epoch > job.time_start + job.timeout:
                        # WE ARE IN TIMEOUT
                        # print("TIMEOUT")
                        # print(w)
                        self._log_info("KILL:%s in worker %s" % (w.id, job.id))
                        gproc.kill()
                        self.workers.pop(wid)
                        job.state = "ERROR"
                        job.error = "TIMEOUT"
                        job.time_stop = j.data.time.epoch
                        self.model_job.set(job)
                        print(job)
                        # make sure right nr of workers are active
                        self._worker_start()

            if test_workers_more():
                # test if we need to add workers
                while test_workers_more():
                    print("WORKERS START")
                    self._worker_start()
            else:

                # test if we have too many workers
                removed_one = False
                active_workers = [key for key in self.workers.keys()]
                active_workers.sort()
                for wid in active_workers:
                    gproc = self.workers[wid]
                    if gproc.exitcode != None:
                        raise RuntimeError("subprocess should never have been exit-ed")
                    w = self.model_worker.get(wid)
                    if w == None:
                        continue

                    job_running = w.current_job != 2147483647
                    self._log_debug("job running:%s (%s)" % (w.id, job_running))

                    if w.halt == False and not job_running and self.queue_jobs_start.qsize() == 0:
                        if removed_one == False and test_workers_less():
                            self._log_debug("worker remove:%s" % wid)
                            removed_one = True
                            w.halt = True
                            self.model_worker.set(w)  # mark worker to halt
                            gproc.kill()
                            gproc.terminate()
                            self.model_worker.delete(wid)
                            gproc2 = self.workers[wid]
                            while gproc.is_alive():
                                gevent.sleep(0.1)
                                print("worker,killing:%s" % wid)
                            assert gproc2.is_alive() == False
                            self.workers.pop(wid)

            # print(self.workers)

            self._log_debug("nr workers:%s, queuesize:%s" % (self.workers_count, self.queue_jobs_start.qsize()))
            gevent.sleep(1)

    def schedule(
        self,
        method,
        *args,
        category="",
        timeout=120,
        inprocess=False,
        return_queues=[],
        return_queues_reset=False,
        gevent=False,
        **kwargs,
    ):
        """

        :param method:
        :param args:
        :param category:
        :param timeout:
        :param inprocess:
        :param return_queues: the result job id will be posted on the specified return_queue names (error or ok)
        :param return_queues_reset, if True will make sure the queues are empty
        :param gevent: means return queues will not be kept in redis, but in gevent queues
        :param kwargs:
        :return:
        """
        if inprocess:
            return method(*args, **kwargs)
        self.init()
        code = inspect.getsource(method)
        code = j.core.text.strip(code)
        code = code.replace("self,", "").replace("self ,", "").replace("self  ,", "")

        methodname = ""
        for line in code.split("\n"):
            if line.startswith("def "):
                methodname = line.split("(", 1)[0].strip().replace("def ", "")

        if methodname == "":
            raise RuntimeError("defname cannot be empty")

        key = j.data.hash.md5_string(code)
        new, action = self.action_get(key)
        if new:
            action.code = code
            action.key = key
            action.methodname = methodname
            self.model_action.set(action)

        job = self.model_job.new()
        job.action_id = action.id
        job.time_start = j.data.time.epoch
        job.state = "NEW"
        job.timeout = timeout
        job.category = category
        job.args = j.data.serializers.json.dumps(args)
        job.kwargs = j.data.serializers.json.dumps(kwargs)
        if not gevent:
            for qname in return_queues:
                job.return_queues.append(qname)
                if return_queues_reset:
                    q = j.clients.redis.getQueue(redisclient=j.clients.redis.core_get(), name="myjobs:%s" % queue_name)
                    q.reset()
        job = self.model_job.set(job)

        if gevent and return_queues != []:
            # self.return_queues[job.id]
            raise RuntimeError("need to implement")

        self.queue_jobs_start.put(job.id)

        return job.id

    def halt(self, graceful=True, reset=True):

        if self.mainloop != None:
            self.mainloop.kill()

        if self.dataloop != None:
            self.dataloop.kill()

        for wid, gproc in self.workers.items():
            if gproc.exitcode != None:
                continue

            w = self.model_worker.get(wid)

            job_running = w.current_job != 2147483647

            if not graceful or not job_running:
                gproc.kill()
                gproc.terminate()  # dont know difference

        if reset:
            self.model_action.destroy()
            self.model_job.destroy()
            self.model_worker.destroy()
            # delete the queue
            while self.queue_jobs_start.get_nowait() != None:
                pass
            while self.queue_return.get_nowait() != None:
                pass

            self._init_ = False

    def results(self, ids, timeout=10):
        res = {}
        counter = 0
        while len(ids) > 0:
            id = ids[0]
            job = self.model_job.get(id)
            if job == None:
                raise RuntimeError("job:%s not found" % id)
            if job.time_stop != 0:
                if job.state == "OK":
                    res[id] = job.result
                    ids = ids[1:]
                else:
                    raise RuntimeError("job in eror:\n%s" % job)
            if len(ids) > 0:
                gevent.sleep(0.1)
                counter += 1
                if counter > timeout * 10:
                    raise RuntimeError("timeout for results with jobids:%s" % ids)
        return res

    def test(self):
        """
        js_shell "j.servers.myjobs.test()"
        :return:
        """
        self.workers_start()
        self.test1()
        self.test2()
        self.test3()
        print("TEST MYWORKERS FOR 3 TESTS DONE")

    def test1(self):
        """
        kosmos "j.servers.myjobs.test1()"
        :return:
        """

        j.tools.logger.debug = True

        # TO TEST DEBUG WINDOW
        # def sometging():
        #     while True:
        #         self._log_debug("test")
        #         self._log_info("test")
        #         self._log_warning("test")
        #         time.sleep(1)
        #
        # self.dataloop = gevent.spawn(sometging)

        def reset():
            # kill leftovers from last time, if any
            self.init(reset=True)
            jobs = self.model_job.find()
            assert len(jobs) == 0
            assert self.queue_jobs_start.qsize() == 0
            assert self.queue_return.qsize() == 0

        def add(a, b):
            return a + b

        def add_error(a, b):
            raise RuntimeError("s")

        def wait():
            import time

            time.sleep(10000)

        def wait_2sec():
            import time

            time.sleep(2)

        reset()

        # test the behaviour for 1 job in process, only gevent for data handling
        jobid = self.schedule(add_error, 1, 2)

        self.worker_start(onetime=True)
        job = self.model_job.get(jobid)
        assert job.error == "s"
        assert job.result == ""
        assert job.state == "ERROR"
        assert job.time_stop > 0

        jobs = self.model_job.find()

        assert len(jobs) == 1
        job = jobs[0]
        assert job.error == "s"
        assert job.result == ""
        assert job.state == "ERROR"
        assert job.time_stop > 0

        j.servers.myjobs.schedule(add, 1, 2)
        self.worker_start(onetime=True)

        jobs = self.model_job.find()
        assert len(jobs) == 2
        job = jobs[1]
        assert job.error == ""
        assert job.result == "3"
        assert job.state == "OK"
        assert job.time_stop > 0

        # lets start from scratch, now we know the super basic stuff is working
        self.init(reset=True)

        for x in range(10):
            self.schedule(add, 1, 2)

        j.servers.myjobs.schedule(add_error, 1, 2)

        jobs = self.model_job.find()

        assert len(jobs) == 11

        assert self.queue_jobs_start.qsize() == 11  # there need to be 12 jobs in queue

        # nothing got started yet

        def tmux_start():
            w = self.model_worker.new()
            cmd = j.servers.startupcmd.get(name="myjobs_worker")
            cmd.cmd_start = "j.servers.myjobs.worker_start_inprocess(worker_id=%s)" % w.id
            cmd.process_strings = "/sandbox/var/cmds/myjobs_worker.py"
            cmd.interpreter = "jumpscale"
            cmd.stop(force=True)
            cmd.start()
            print("WORKER STARTED IN TMUX")

        tmux_start()
        self.dataloop = gevent.spawn(self._data_loop)

        job = jobs[0]

        res = self.results([job.id])

        assert res == {job.id: "3"}  # is the result back

        assert 3 == j.servers.myjobs.schedule(add, 1, 2, inprocess=True)

        print("will wait for results")
        assert self.results([jobs[2].id, jobs[3].id, jobs[4].id], timeout=1) == {
            jobs[2].id: "3",
            jobs[3].id: "3",
            jobs[4].id: "3",
        }

        jobs = self.model_job.find()
        errors = [job for job in jobs if job.state == "ERROR"]
        assert len(errors) == 1

        # test with publish_subscribe channels
        queue_name = "myself"
        q = j.clients.redis.getQueue(redisclient=j.clients.redis.core_get(), name="myjobs:%s" % queue_name)
        q.reset()  # lets make sure its empty

        j.servers.myjobs.schedule(add, 1, 2, return_queues=[queue_name])
        time.sleep(0.5)
        assert q.qsize() == 1
        job_return = j.servers.myjobs.wait("myself")
        assert job_return.result == "3"
        assert job_return.id == 11
        assert job_return.state == "OK"

        kill()

        # TMUX and in process tests are done, lets now see if as subprocess it works

        self.init(reset=True, start=True)

        print("wait to schedule jobs")
        gevent.sleep(2)

        for x in range(20):
            self.schedule(wait_2sec)

        j.servers.myjobs.schedule(wait, timeout=1)
        j.servers.myjobs.schedule(add_error, 1, 2)

        print("there should be 10 workers, so wait is max 5 sec")
        gevent.sleep(5)

        # now timeout should have happened & all should have executed

        jobs = self.model_job.find()
        assert len(jobs) == 22

        completed = [job for job in jobs if job.time_stop != 0]

        assert len(completed) == 22

        errors = [job for job in jobs if job.error != ""]
        assert len(errors) == 2

        errors = [job for job in jobs if job.state == "ERROR"]
        assert len(errors) == 2

        errors = [job for job in jobs if job.error == "s"]
        assert len(errors) == 1

        errors = [job for job in jobs if job.error == "TIMEOUT"]
        assert len(errors) == 1

        jobs = [job for job in jobs if job.state == "OK"]
        assert len(jobs) == 20

        self.halt(reset=True)

        print("TEST1 OK, ALL PASSED")

    def test2(self):
        """
        js_shell "j.servers.myjobs.test2()"
        :return:
        """
        self.init(reset=True)

        def wait_2sec():
            import time

            time.sleep(2)

        for x in range(40):
            self.schedule(wait_2sec)

        self.start()

        gevent.joinall([self.dataloop, self.mainloop])

        print("TEST OK")

        self.halt(reset=True)

    def test3(self):
        """
        js_shell "j.servers.myjobs.test3()"
        :return:
        """
        self.init(reset=True)
        self.workers_nr_max = 100

        def wait_1sec():
            import time

            time.sleep(1)
            return "OK"

        ids = []
        for x in range(100):
            ids.append(self.schedule(wait_1sec))

        res = self.results(ids)

        j.shell()

    def test4(self):
        """
        js_shell "j.servers.myjobs.test2()"
        :return:
        """

        def use_jumpscale():
            return j.data.serializers.json.dumps([1, 2])

        self.result_queue_get()
