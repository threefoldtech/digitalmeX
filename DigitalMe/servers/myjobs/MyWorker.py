from Jumpscale import j

import pudb
import sys
import traceback
import gevent


class MyWorker(j.application.JSBaseClass):
    def return_data(self, cat, obj):
        data = [cat, obj.id, obj._json]
        self.queue_return.put(data)

    def error_handler(self, logdict):
        # j.shell()
        cat = "L"
        data = j.data.serializers.json.dumps(logdict)
        self.queue_return.put(data)

    def __init__(self, worker_id=None, onetime=False, showout=True, debug=False):
        """
        :return:
        """

        j.application.JSBaseClass.__init__(self)

        self.onetime = onetime
        self.showout = showout
        self.debug = debug

        assert worker_id

        if self.debug:
            j.application.debug = self.debug
            j.core.myenv.debug = self.debug

        # make sure all traces of existing clients are gone
        j.application.subprocess_prepare()
        j.data.bcdb._bcdb_instances = {}

        j.clients.redis._cache_clear()  # make sure we have redis connections empty, because comes from parent

        # MAKE SURE YOU DON'T REUSE SOCKETS FROM MOTHER PROCESSS
        j.core.db.source = "worker"  # this allows us to test
        redisclient = j.core.db

        self.queue_jobs_start = j.clients.redis.queue_get(
            redisclient=redisclient, key="queue:jobs:start", fromcache=False
        )
        self.queue_return = j.clients.redis.queue_get(redisclient=redisclient, key="queue:jobs:return", fromcache=False)

        # test we are using the right redis client
        assert self.queue_jobs_start._db_.source == "worker"
        assert self.queue_return._db_.source == "worker"

        j.errorhandler.handlers.append(self.error_handler)

        storclient = j.clients.rdb.client_get(redisclient=redisclient)
        assert storclient._redis.source == "worker"

        self.bcdb = j.data.bcdb.get("myjobs", storclient=storclient, fromcache=False)
        self.model_job = self.bcdb.model_get_from_url("jumpscale.myjobs.job")
        self.model_action = self.bcdb.model_get_from_url("jumpscale.myjobs.action")
        self.model_worker = self.bcdb.model_get_from_url("jumpscale.myjobs.worker")
        # self.model_job.readonly = True
        # self.model_action.readonly = True
        # self.model_worker.readonly = True

        # self.model_worker.trigger_add(self._save_data)
        # self.model_job.trigger_add(self._save_job)

        self.data = self.model_worker.get(worker_id)
        self.data.state = "new"
        self.data.current_job = 2147483647  # means nil
        self.data.id = worker_id
        # self.data.save()  # save in bcdb will not happen because readonly is True, it will trigger the triggers

        self.start()

    def _save_data(self, obj, action, propertyname):
        if action == "save":
            self.return_data("W", obj)
        j.shell()

    def _save_job(self, obj, action, propertyname):
        if action == "save":
            self.return_data("J", obj)
        j.shell()

    def start(self):

        while True:

            if self.onetime:
                res = None
                while not res:
                    res = self.queue_jobs_start.get(timeout=0)
                    gevent.sleep(0.1)
                    print("jobget")
            else:
                res = self.queue_jobs_start.get(timeout=10)
            if res == None:
                if self.showout:
                    self._log_info("queue request timeout, no data, continue")
                # have to fetch this again because was waiting on queue
                if self.data.halt:
                    # model_worker.
                    print("WORKER REMOVE SELF:%s" % self.data.id)
                    return
            else:
                res.decode()
                jobid = int(res)

                # update worker has been active
                self.data = self.model_worker.get(self.data.id)

                if res == "halt":
                    return
                self.data.last_update = j.data.time.epoch
                self.data.current_job = jobid
                self.data.save()

                job = self.model_job.get(obj_id=jobid, die=False)

                if job == None:
                    print("ERROR: job:%s not found" % jobid)
                else:
                    # now have job
                    action = self.model_action.get(job.action_id, die=False)
                    if action == None:
                        raise j.exceptions.Base("ERROR: action:%s not found" % job.action_id)
                    kwargs =  job.kwargs #j.data.serializers.json.loads(job.kwargs)
                    args = job.args

                    self.data.last_update = j.data.time.epoch
                    self.data.current_job = jobid  # set current jobid
                    self.data.save()

                    if self.showout:
                        print("EXECUTE")
                        print(job)

                    try:
                        exec(action.code)
                        # better not to use eval but the JSX coderunner?
                        method = eval(action.methodname)
                    except Exception as e:
                        tb = sys.exc_info()[-1]
                        # logdict = self.log2str(
                        #     tb=tb, error=e, message="cannot compile action", data=action, stdout=self.showout
                        # )

                        job.error = {"error": str(e)}
                        job.state = "ERROR"
                        job.time_stop = j.data.time.epoch
                        job.save()

                        if self.debug:
                            pudb.post_mortem(tb)

                        if self.onetime:
                            return
                        continue

                    try:
                        # import ipdb; ipdb.set_trace()
                        res = method(*args, **kwargs)
                    except Exception as e:
                        tb = sys.exc_info()[-1]
                        # logdict = self.log(
                        #     tb=tb, error=e, message="cannot execute action", data=action, stdout=self.showout
                        # )
                        job.error = {"error":str(e)}
                        job.state = "ERROR"
                        job.time_stop = j.data.time.epoch
                        job.save()

                        if self.debug:
                            pudb.post_mortem(tb)
                        # msg = err + "\nCOULD NOT EXECUTE METHOD {}.\n {}".format(action.methodname, action.code)
                        if self.showout:
                            print("ERROR:%s" % e)
                        if self.onetime:
                            return
                        continue

                    try:
                        job.result = j.data.serializers.json.dumps({"result": res})
                    except Exception as e:
                        job.error = (
                            str(e) + "\nCOULD NOT SERIALIZE RESULT OF THE METHOD, make sure json can be used on result"
                        )
                        job.state = "ERROR"
                        job.time_stop = j.data.time.epoch
                        job.save()
                        if self.showout:
                            print("ERROR:%s" % e)
                        if onetime:
                            return
                        continue

                    job.time_stop = j.data.time.epoch
                    job.state = "OK"

                    if self.showout:
                        self._log("OK", data=job)

                    job.save()

                    self.data.current_job = 2147483647
                    self.data.save()

            if self.onetime:
                return
