<script>
	import { getWorkers } from '../data';
	import { onMount } from 'svelte';

	console.log(getWorkers)
	import {
		link,
		push,
		pop,
		replace,
		location,
		querystring,
	} from 'svelte-spa-router';

	const state = {
		RESULT: 'OK',
		ERROR: 'ERROR',
		NEW: 'NEW',
	};

	var successCount = 0;
	var failureCount = 0;
	var newCount = 0;

	const status = { ONLINE: 'online', OFFLINE: 'offline' };
	let workers = [];

	onMount(async() => {
		getWorkers().then(function(data) {
		if (!data) {
			return;
		}
		debugger;
		console.log(data, typeof data);
		workers = JSON.parse(data).workers;
		workers.forEach(worker => {
			worker.state = worker.state.toUpperCase();
		});


		statsticsCalculation();

		function statsticsCalculation() {
			console.log('statstics');
			workers.forEach(worker => {
				if (worker.state == state.RESULT) successCount++;
				else if (worker.state == state.ERROR) failureCount++;
				else if (worker.state == state.NEW) newCount++;
				else {
				}
			});
		}

		});
	});
	console.log(newCount);
</script>

<style>
	.mt-3 {
		margin-top: 20px;
	}
</style>

<!--[Header]-->
<h1>Workers</h1>
<!--[Containder]-->
<div class="row">
	<!--[Workers-Data]-->
	<div class="col-xs-12">
		<table class="table table-striped">
			<!--[Workers-Data-Headers]-->
			<thead>
				<tr>
					<th scope="col">#</th>
					<th scope="col">Id</th>
					<th scope="col">Halt</th>
					<th scope="col">Pid</th>
					<th scope="col">State</th>
					<th scope="col">Error</th>
					<th scope="col">Current Job</th>
					<th scope="col">Last Update</th>
					<th scope="col">Time Start</th>
					<th scope="col">Timeout</th>
				</tr>
			</thead>
			<!--[Workers-Data-Body]-->
			<tbody>
				{#each workers as worker, i}
					<tr>
						<th scope="row">{i + 1}</th>
						<td>
							<a href="/single-worker-tasks/{worker.id}" use:link>
								{worker.id}
							</a>
						</td>
						<td>{worker.halt}</td>
						<td>{worker.pid}</td>
						{#if worker.state == state.RESULT}
							<td>
								<span class="label label-pill label-success">
									{worker.state}
								</span>
							</td>
						{:else if worker.state == state.ERROR}
							<td>
								<span class="label label-pill label-danger">
									{worker.state}
								</span>
							</td>
						{:else if worker.state == state.NEW}
							<td>
								<span class="label label-pill label-primary">
									{worker.state}
								</span>
							</td>
						{/if}
						<td>{worker.error}</td>
						<td>{worker.current_job}</td>
						<td>{worker.last_update}</td>
						<td>{worker.time_start}</td>
						<td>{worker.timeout}</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
</div>

<div class="row mt-3">
	<!--[Tasks-Data]-->
	<div class="col-xs-12">
		<!-- content here -->
		<table class="table table-striped">
			<!--[Tasks-Data-Headers]-->
			<thead>
				<tr>
					<th class="text-center" scope="col">Total Workers</th>
					<th class="text-center" scope="col">New Workers</th>
					<th class="text-center" scope="col">Success Workers</th>
					<th class="text-center" scope="col">Failure Workers</th>
				</tr>
			</thead>
			<tbody class="text-center">
				<td>{workers.length}</td>
				<td>{newCount}</td>
				<td>{successCount}</td>
				<td>{failureCount}</td>
			</tbody>
		</table>
	</div>
</div>
