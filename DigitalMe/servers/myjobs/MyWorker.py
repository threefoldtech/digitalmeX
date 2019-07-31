# import pudb
import sys
import traceback
import time


def MyWorker(worker_id=999999, onetime=False, showout=False):
    """
    :return:
    """

    from Jumpscale import j

    # make sure all traces of existing clients are gone
    j.application.subprocess_prepare()

    w = None

    j.clients.redis._cache_clear()  # make sure we have redis connections empty, because comes from parent

    # MAKE SURE YOU DON'T REUSE SOCKETS FROM MOTHER PROCESSS
    j.core.db.source = "worker"  # this allows us to test
    redisclient = j.core.db

    queue_jobs_start = j.clients.redis.queue_get(redisclient=redisclient, key="queue:jobs:start", fromcache=False)
    queue_return = j.clients.redis.queue_get(redisclient=redisclient, key="queue:jobs:return", fromcache=False)

    # test we are using the right redis client
    assert queue_jobs_start._db_.source == "worker"
    assert queue_return._db_.source == "worker"

    def return_data(cat, obj):
        data = j.data.serializers.msgpack.dumps([cat, obj.id, obj._json])
        queue_return.put(data)

    def return_job_obj(obj):
        return_data("J", obj)

    def return_worker_obj(obj):
        return_data("W", obj)

    def return_error(error, objid=None):
        cat = "E"
        data = j.data.serializers.msgpack.dumps([cat, objid, error])
        queue_return.put(data)

    def my_excepthook(exception_type, exception_obj, tb):
        # print(exception_obj)
        # traceback.print_tb(tb)
        pm = "\n".join(traceback.format_tb(tb))
        if w and w.current_job != 2147483647:
            msg = "exception in myjobs worker (%s)\n" % w.current_job
        else:
            msg = "exception in myjobs worker\n"
        msg += "%s\n" % exception_type
        msg += "%s\n\n" % exception_obj
        msg += "%s\n" % pm
        j.core.tools.pprint("{RED}CANNOT CONTINUE{RESET}\n%s" % msg)
        raise_error(msg)

    def raise_error(msg):
        if w:
            w.error = msg
            w.state = "error"
            w.last_update = j.data.time.epoch
            return_worker_obj(w)
            return_error(w.id)
        sys.exit(1)

    sys.excepthook = my_excepthook

    storclient = j.clients.rdb.client_get(redisclient=redisclient)
    assert storclient._redis.source == "worker"

    bcdb = j.data.bcdb.get("myjobs", storclient=storclient)
    # TODO: should test here too that we are using the right redis, its important we no-where reuse a socket
    model_job = bcdb.model_get_from_url("jumpscale.myjobs.job")
    model_action = bcdb.model_get_from_url("jumpscale.myjobs.action")
    model_worker = bcdb.model_get_from_url("jumpscale.myjobs.worker")

    assert model_worker.storclient._redis.source == "worker"

    w = model_worker.get(worker_id)
    w.state = "init"
    w.current_job = 2147483647  # means nil
    return_worker_obj(w)

    while True:

        if onetime:
            res = None
            while not res:
                res = queue_jobs_start.get(timeout=0)
                time.sleep(0.1)
                print("jobget")
        else:
            res = queue_jobs_start.get(timeout=10)
        if res == None:
            if showout:
                print("queue request timeout, no data, continue")
            w = model_worker.get(worker_id)
            # have to fetch this again because was waiting on queue
            if w.halt:
                # model_worker.
                print("WORKER REMOVE SELF:%s" % worker_id)
                return
        else:
            res.decode()
            jobid = int(res)
            # update worker has been active
            w = model_worker.get(worker_id)

            if res == "halt":
                return
            w.last_update = j.data.time.epoch
            w.current_job = jobid
            return_worker_obj(w)

            job = model_job.get(obj_id=jobid, die=False)

            if job == None:
                print("ERROR: job:%s not found" % jobid)
            else:
                # now have job
                action = model_action.get(job.action_id, die=False)
                if action == None:
                    raise RuntimeError("ERROR: action:%s not found" % job.action_id)
                kwargs = j.data.serializers.json.loads(job.kwargs)
                args = j.data.serializers.json.loads(job.args)

                w.last_update = j.data.time.epoch
                w.current_job = jobid  # set current jobid
                return_worker_obj(w)

                if showout:
                    print("EXECUTE")
                    print(job)

                try:
                    exec(action.code)
                    method = eval(action.methodname)
                except Exception as e:
                    job.error = str(e) + "\nCOULD NOT GET TO METHOD, IMPORT ERROR."
                    job.state = "ERROR"
                    job.time_stop = j.data.time.epoch
                    return_job_obj(job)
                    if showout:
                        print("ERROR:%s" % e)
                    if onetime:
                        return
                    continue

                try:
                    res = method(*args, **kwargs)
                except Exception as e:
                    job.error = str(e)
                    job.state = "ERROR"
                    job.time_stop = j.data.time.epoch
                    return_job_obj(job)
                    if showout:
                        print("ERROR:%s" % e)
                    if onetime:
                        return
                    continue

                try:
                    job.result = j.data.serializers.json.dumps(res)
                except Exception as e:
                    job.error = (
                        str(e) + "\nCOULD NOT SERIALIZE RESULT OF THE METHOD, make sure json can be used on result"
                    )
                    job.state = "ERROR"
                    job.time_stop = j.data.time.epoch
                    return_job_obj(job)
                    if showout:
                        print("ERROR:%s" % e)
                    if onetime:
                        return
                    continue

                job.time_stop = j.data.time.epoch
                job.state = "OK"

                if showout:
                    print("OK")
                    print(job)

                return_job_obj(job)

                w.current_job = 2147483647
                return_worker_obj(w)

        if onetime:
            return
