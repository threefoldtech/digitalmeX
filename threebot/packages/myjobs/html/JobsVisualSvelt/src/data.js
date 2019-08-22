function getJobs() {
    return GEDIS_CLIENT.execute(info = { "namespace": "default", "actor": "myjobs", "command": "list_jobs" })
}



function getWorkers() {
    return GEDIS_CLIENT.execute(info = { "namespace": "default", "actor": "myjobs", "command": "list_workers" })
}


export { getJobs, getWorkers }
