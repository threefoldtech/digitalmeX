<script>
	import Router from 'svelte-spa-router';
	import Workers from './routes/Workers.svelte';
	import Tasks from './routes/Tasks.svelte';
	import SingleWorkerTasks from './routes/SingleWorkerTasks.svelte';
	import Navigtation from './Navigation.svelte';
	import TasksRendering from './routes/TasksRendering.svelte';

	import routes from './routes';
	import {
		link,
		push,
		pop,
		replace,
		location,
		querystring,
	} from 'svelte-spa-router';
</script>

<style>

</style>

<!--Navigtation bar-->
<div>
	<Navigtation />
</div>
<div class="container">
	<!-- Show the router -->
	<Router {routes} />
</div>
