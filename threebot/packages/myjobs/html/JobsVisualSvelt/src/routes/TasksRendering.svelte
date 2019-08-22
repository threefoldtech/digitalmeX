<script>
	export let allTasks = [];
	export let isError = false;
	const state = {
		RESULT: 'OK',
		ERROR: 'ERROR',
		NEW: 'NEW',
		RUNNING: 'RUNNING',
		HALTED: 'HALTED',
		ALL: 'all',
	};

	let counters = { success: 0, error: 0, new: 0, running: 0, halted: 0 };
	let currentFilter = state.ALL;
	$: filteredTasks = () =>  {
		if (currentFilter == state.ALL) return allTasks;
		else if (currentFilter == state.RESULT) return tasksFiltering(state.RESULT);
	};

	function tasksFiltering(state) {
		let filteredTasks = [];
		allTasks.forEach(task => {
			task.state == state;
			filteredTasks.push(task);
		});
		return filteredTasks;
	}

	if (isError != true) {
		statsticsCalculation();
	}
	function statsticsCalculation() {
		allTasks.forEach(task => {
			if (task.state == state.RESULT) counters['success']++;
			else if (task.state == state.ERROR) counters['error']++;
			else if (task.state == state.NEW) counters['new']++;
			else if (task.state == state.RUNNING) counters['running']++;
			else if (task.state == state.HALTED) counters['halted']++;
			else {
			}
		});
	}
	function updateFilter(filter) {
		console.log(`updating currentFilter to : ${filter}`);
		currentFilter = filter;
	}
</script>

<style>
	.mt-3 {
		margin-top: 20px;
	}
</style>

<!--[Containder]-->
<div>
	<div class="row">
		<!--[Tasks-Data]-->
		<div class="col-xs-12">
			{#if isError != true}
				<!-- content here -->
				<table class="table table-striped">
					<!--[Tasks-Data-Headers]-->
					<thead>
						<tr>
							<th scope="col">#</th>
							<th scope="col">Id</th>
							<th scope="col">Category</th>
							<th scope="col">Time Start</th>
							<th scope="col">Time Stop</th>
							<th scope="col">State</th>
							<th scope="col">Timeout</th>
							<th scope="col">Action Id</th>
							<th scope="col">args</th>
							<th scope="col">kwargs</th>
							<th scope="col">Result</th>
							<th scope="col">Error</th>
							<th scope="col">Return Queues</th>
						</tr>
					</thead>
					<!--[Tasks-Data-Body]-->
					<tbody>
						{#each filteredTasks() as task, i}
							<tr>
								<th scope="row">{i + 1}</th>
								<td>{task.id}</td>
								<td>{task.category}</td>
								<td>{task.time_start}</td>
								<td>{task.time_stop}</td>
								{#if task.state == state.RESULT}
									<td>
										<span class="label label-pill label-success">
											{task.state}
										</span>
									</td>
								{:else if task.state == state.ERROR}
									<td>
										<span class="label label-pill label-danger">
											{task.state}
										</span>
									</td>
								{:else if task.state == state.NEW}
									<td>
										<span class="label label-pill label-primary">
											{task.state}
										</span>
									</td>
								{:else if task.state == state.RUNNING}
									<td>
										<span class="label label-pill label-warning">
											{task.state}
										</span>
									</td>
								{:else if task.state == state.HALTED}
									<td>
										<span class="label label-pill label-info">
											{task.state}
										</span>
									</td>
								{/if}

								<td>{task.timeout}</td>
								<td>{task.action_id}</td>
								<td>{task.args}</td>
								<td>{task.kwargs}</td>
								<td>{task.result}</td>
								<td>{task.error}</td>
								<td>{task.return_queues}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			{:else}
				<!-- else content here -->
				<h3>There is no worker with this ID</h3>
			{/if}

		</div>
	</div>

	<!--[Filter]-->
	<div>
		<button
			on:click={() => updateFilter(state.ALL)}
			class:active={currentFilter === state.ALL}>
			All
		</button>
		<button
			on:click={() => updateFilter(state.RESULT)}
			class:active={currentFilter === state.RESULT}>
			Succes
		</button>

	</div>
	<!--[Statstics]-->
	{#if isError != true}
		<!--[Containder]-->
		<div class="row mt-3">
			<!--[Tasks-Data]-->
			<div class="col-xs-12">
				<!-- content here -->
				<table class="table table-striped">
					<!--[Tasks-Data-Headers]-->
					<thead>
						<tr>
							<th class="text-center" scope="col">Total Tasks</th>
							<th class="text-center" scope="col">Success Tasks</th>
							<th class="text-center" scope="col">Failure Tasks</th>
							<th class="text-center" scope="col">New Tasks</th>
							<th class="text-center" scope="col">Running Tasks</th>
							<th class="text-center" scope="col">Halted Tasks</th>
						</tr>
					</thead>
					<tbody class="text-center">
						<td>{allTasks.length}</td>
						<td>{counters['success']}</td>
						<td>{counters['error']}</td>
						<td>{counters['new']}</td>
						<td>{counters['running']}</td>
						<td>{counters['halted']}</td>
					</tbody>
				</table>
			</div>
		</div>
	{/if}
</div>
