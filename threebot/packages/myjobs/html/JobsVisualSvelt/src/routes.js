import Workers from './routes/Workers.svelte';
import Tasks from './routes/Tasks.svelte';
import SingleWorkerTasks from './routes/SingleWorkerTasks.svelte';
import NotFound from './routes/NotFound.svelte';

let routes
routes = new Map()
routes.set('/', Workers)
routes.set('/workers', Workers)
routes.set('/tasks', Tasks)
routes.set('/single-worker-tasks/:taskId', SingleWorkerTasks)
// Catch-all, must be last
routes.set('*', NotFound)

export default routes
