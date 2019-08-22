<script>
	import TasksRendering from './TasksRendering.svelte';
	import { getJobs } from '../data';
	import { onMount } from 'svelte';

	let allTasks = [];

	onMount(async() => {
		getJobs().then(function(data) {
			if (!data) {
				return;
			}
			console.log(data);
			allTasks = JSON.parse(data).jobs;
			//Make all the states UpperCase
			allTasks.forEach(task => {
				task.state = task.state.toUpperCase();
			});
		});
	});
</script>

<style>

</style>

<!--[Header]-->
<h1>Tasks</h1>
<TasksRendering {allTasks} />
