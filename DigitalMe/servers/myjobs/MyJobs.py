import inspect
from Jumpscale import j
import gipc
import gevent
import sys
from .MyWorker import MyWorker

JSBASE = j.application.JSBaseClass

schema_job = """
@url = jumpscale.myjobs.job
category*= ""
time_start = 0 (T)
time_stop = 0 (T)
state* = "NEW,ERROR,OK,RUNNING,HALTED" (E)
timeout = 0
action_id* = 0
args = (json)
kwargs = (dict)
result = (S)
error = (dict)
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
state* = "NEW"
pid = 0
halt = false (B)

"""


class MyJobs(JSBASE, j.application.JSFactoryTools):
    __jslocation__ = "j.servers.myjobs"

    def _init(self, **kwargs):
        self.queue_jobs_start = j.clients.redis.queue_get(redisclient=j.core.db, key="queue:jobs:start")
        self.queue_return = j.clients.redis.queue_get(redisclient=j.core.db, key="queue:jobs:return")
        self.workers = {}
        self.workers_nr_min = 1
        self.workers_nr_max = 10
        self.mainloop = None
        self.dataloop = None

        db = j.data.bcdb.get("myjobs", storclient=j.clients.rdb.client_get())

        self.model_job = db.model_get(schema=schema_job)
        self.model_action = db.model_get(schema=schema_action)
        self.model_worker = db.model_get(schema=schema_worker)

        self._init_ = False
        self.scheduled_ids = []

    def job_get(self, job_id):
        return self.model_job.get(job_id)

    def init(self):
        """
        activates the models and starts the worker manager if required
        """
        if self._init_ is False:

            if self.mainloop != None:
                self.mainloop.kill()

            if self.dataloop != None:
                self.dataloop.kill()

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

    def start(self, debug=False, fixed_workers=None):
        """

        kosmos -p "j.servers.myjobs.start()"
        kosmos -p "j.servers.myjobs.start(debug=True)"
        kosmos -p "j.servers.myjobs.start(debug=True,fixed_workers=10)"

        if non debug and fixed workers is None:
            always in subprocess, cannot see the output
            will add worker(s) when needed, when there is more work

        to test can but debug on True and run in separate console

        :return:
        """
        self.init(reset=False)
        if not debug:
            if not fixed_workers:
                self.mainloop = gevent.spawn(self._main_loop)
            else:
                self._main_loop_fixed(nr=fixed_workers, debug=debug)  # does not wait, no need to do in gevent
        self.dataloop = gevent.spawn(self._data_loop)  # returns the data
        if debug:
            j.tools.logger.debug = True
            if not fixed_workers:
                self._main_loop()
            else:
                self._main_loop_fixed(nr=fixed_workers, debug=debug)

    def worker_start(self, onetime=False, subprocess=True, worker_id=None, debug=False):
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
            worker = gipc.start_process(target=MyWorker, kwargs={"worker_id": w.id})
            self.workers[w.id] = worker
        else:
            MyWorker(worker_id=w.id, onetime=onetime, debug=debug)
            # will make sure the data comes back
            self._data_process_untill_empty(timeout=5, die=False)

    def dataloop_start(self):
        if not self.dataloop:
            self.dataloop = gevent.spawn(self._data_loop)

    def workers_start_corex(self, nrworkers=3, debug=False):
        """
        kosmos "j.servers.myjobs.workers_start_corex(1)"
        """
        # j.builders.apps.corex.install()
        # j.servers.corex.default.start()  # starts corex at port 1500

        for nr in range(nrworkers):
            cmd = j.servers.startupcmd.get(name="workers_%s" % nr)
            if debug:
                cmd.cmd_start = "j.servers.myjobs.worker_start(subprocess=False,debug=True)"
            else:
                cmd.cmd_start = "j.servers.myjobs.worker_start(subprocess=False,debug=False)"
            # COREX has still issues so fall back on tmux
            cmd.executor = "tmux"
            cmd.interpreter = "jumpscale"
            cmd.start(reset=True)

        self.dataloop_start()

        self._log_info("visit http://localhost:1500/ for seeing the corex webscreen")

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

    def _data_process_1time(self, timeout=0, die=False):
        r = self.queue_return.get(timeout=timeout)
        if r == None:
            return

        thedata = j.data.serializers.json.loads(r)  # change to json

        cat, objid, data = thedata

        if cat == "W":
            worker = self.model_worker.new(data=data)
            worker.id = objid
            worker.save()
            return True
        elif cat == "J":
            job = self.model_job.new(data=data)
            job.id = objid
            job.save()
            for queue_name in job.return_queues:
                queue = j.clients.redis.getQueue(redisclient=j.core.db, name="myjobs:%s" % queue_name)
                queue.put(job.id)
            return True
        elif cat == "E":
            datae = j.data.serializers.json.loads(data)
            j.core.tools.log2stdout(datae)
            if die:
                raise j.exceptions.Base(data=datae)
            return True
        else:
            raise j.exceptions.Base("return queue does not have right obj")

    def _data_process_untill_empty(self, timeout=1, die=True):
        self.init()
        # need to wait till first one comes
        r = self._data_process_1time(timeout=timeout, die=die)
        if not r:
            return

        while r is not None:
            if self.queue_return.empty:
                return
            r = self._data_process_1time(timeout=timeout, die=die)

    def _main_loop_fixed(self, nr=10, debug=False):
        """
        will not dynamically allocate the workers, will be a fixed pool
        :param nr:
        :param debug:
        :return:
        """

        for i in range(nr):
            self.worker_start()
        if debug:
            j.shell()

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
            # gevent.sleep(2)

            # TEST for timeout
            wids = [key for key in self.workers.keys()]
            for wid in wids:
                if wid in self.workers:
                    gproc = self.workers[wid]
                else:
                    continue
                if gproc.exitcode != None:
                    raise j.exceptions.Base("subprocess should never have been exitted")
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
                        self.worker_start()

            if test_workers_more():
                # test if we need to add workers
                while test_workers_more():
                    print("WORKERS START")
                    self.worker_start()
            else:

                # test if we have too many workers
                removed_one = False
                active_workers = [key for key in self.workers.keys()]
                active_workers.sort()
                for wid in active_workers:
                    gproc = self.workers[wid]
                    if gproc.exitcode != None:
                        raise j.exceptions.Base("subprocess should never have been exit-ed")
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
        print("executing method with *args {} and **kwargs {} ".format(args, kwargs))
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
            raise j.exceptions.Base("defname cannot be empty")

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
            raise j.exceptions.Base("need to implement")

        self.queue_jobs_start.put(job.id)

        if job.id not in self.scheduled_ids:
            self.scheduled_ids.append(job.id)

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

    def reset(self):
        # kill leftovers from last time, if any
        self.halt(graceful=False, reset=True)
        assert self.queue_jobs_start.qsize() == 0
        assert self.queue_return.qsize() == 0

    def results(self, ids=None, timeout=100, die=True):
        """

        :param ids: if not specified then will be the last launched jobs
        :param timeout:
        :param die:  id die False then result will be the full objects
        :return:
        """

        if not ids:
            ids = self.scheduled_ids
        res = {}
        counter = 0

        if len(ids) > 0:
            current_id = ids[0]
        else:
            current_id = None

        while current_id:
            job = self.model_job.get(current_id)
            if job == None:
                raise j.exceptions.Base("job:%s not found" % current_id)
            if job.time_stop != 0:
                if job.state == "OK":
                    if die:
                        res[current_id] = job.result
                    else:
                        res[current_id] = job
                    if len(ids) > 0:
                        ids.pop(0)
                        if len(ids) > 0:
                            current_id = ids[0]
                        else:
                            current_id = None
                elif job.state == "ERROR":
                    logdict = job.error
                    j.core.tools.log2stdout(logdict)
                    if die:
                        self.scheduled_ids = []
                        raise RuntimeError("job:%s in error" % job.id)
                    else:
                        # we collect all errors so we need to make sure we get all other errors or non other errorobj
                        res[current_id] = job
                        if len(ids) > 0:
                            ids.pop(0)
                            if len(ids) > 0:
                                current_id = ids[0]
                            else:
                                current_id = None
                elif job.state == "HALTED":
                    # dont think we use at this point
                    j.shell()

            if len(ids) == 0:
                self.scheduled_ids = []
                return res

            counter += 1
            if counter > timeout * 10:
                self.scheduled_ids = []
                raise j.exceptions.Base("timeout for results with jobids:%s" % ids)

            if not self.dataloop:
                # means we have to manually fetch the objects there is no dataloop doing it for us
                self._data_process_untill_empty(die=False)

        self.scheduled_ids = []
        return res

    workers_start = workers_start_corex

    def test(self, name="basic", start=False):
        """
        it's run all tests
        kosmos 'j.servers.myjobs.test()'

        """
        if start:
            self.workers_start()
        self._test_run(name=name)

    # def test_spawn(self):
    #     """
    #     kosmos -p "j.servers.myjobs.test_spawn()"
    #
    #     note the -p it will make sure the monkey patching happens
    #
    #     this testfunction will test the debug window
    #
    #     :return:
    #     """
    #
    #     j.core.myenv.config["LOGGER_PANEL_NRLINES"] = 15  # means 15 lines in panel  (-1 means auto, 0 means none)
    #     j.tools.logger.debug = True
    #
    #     def something():
    #         counter = 1
    #         while True:
    #             counter += 1
    #             self._log_debug("test")
    #             self._log_info("test:%s" % counter)
    #             self._log_warning("test")
    #             gevent.sleep(1)
    #
    #     gevent.spawn(something)
    #
    #     j.shell()  # you will see the shell is now interactive but yet still the something greenlet is running

    def test1(self):
        """
        kosmos "j.servers.myjobs.test1()"
        :return:
        """

        j.tools.logger.debug = True

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
            raise j.exceptions.Base("s")

        def wait():
            import time

            gevent.sleep(10000)

        def wait_2sec():
            import time

            gevent.sleep(2)

        reset()

        self.worker_start(onetime=True)

        # test the behaviour for 1 job in process, only gevent for data handling
        jobid = self.schedule(add_error, 1, 2)

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
            return cmd

        cmd = tmux_start()
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
        gevent.sleep(0.5)
        assert q.qsize() == 1
        job_return = j.servers.myjobs.wait("myself")
        assert job_return.result == "3"
        assert job_return.id == 11
        assert job_return.state == "OK"

        cmd.stop(force=True)

        # TMUX and in process tests are done, lets now see if as subprocess it works

        self.init(reset=True)
        self.start()

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
        kosmos "j.servers.myjobs.test2()"
        :return:
        """
        self.init(reset=True)
        self.start()

        def wait_2sec():
            import time

            gevent.sleep(2)

        for x in range(40):
            self.schedule(wait_2sec)

        self.start()

        gevent.joinall([self.dataloop, self.mainloop])

        print("TEST OK")

        self.halt(reset=True)

    def test3(self, start=True, count=100):
        """
        kosmos -p "j.servers.myjobs.test3()"
        kosmos -p "j.servers.myjobs.test3(start=False,count=10)"
        kosmos -p "j.servers.myjobs.test3(start=False,count=100)"
        :return:
        """
        self.init(reset=True)
        if start:
            self.start()
        self.workers_nr_max = 100

        def wait_1sec():
            import time

            gevent.sleep(1)
            return "OK"

        ids = []
        for x in range(count):
            ids.append(self.schedule(wait_1sec))

        res = self.results(ids)

        j.shell()

    def test4(self, start=True, count=20):
        """
        kosmos -p "j.servers.myjobs.test4()"
        kosmos -p "j.servers.myjobs.test4(start=False,count=3)"
        :return:
        """
        if start:
            j.servers.myjobs.workers_start_corex(4)

        def wait_1sec():
            import time

            gevent.sleep(1)
            return "OK"

        ids = []
        self._data_process_untill_empty()
        for x in range(count):
            ids.append(j.servers.myjobs.schedule(wait_1sec))

        print(ids)

        res = j.servers.myjobs.results(ids)
        for id in ids:
            assert res[id] == "OK"

        print("TESTOK")
