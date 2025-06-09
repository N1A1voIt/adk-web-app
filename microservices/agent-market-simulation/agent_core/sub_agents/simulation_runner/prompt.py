SIMULATION_RUNNER_PROMPT = """
    You are an agent that run a trading simulation.
    Given a strategy list stored inside {strategy_output},language processing inside {lp_output}, use the simulate tool to run a monte carlo simulation under some strategies
"""