DROP TABLE IF EXISTS simulation;

CREATE TABLE IF NOT EXISTS simulation (
    simulation_id TEXT PRIMARY KEY NOT NULL,
    cycle_start TEXT NOT NULL,
    cycle_end TEXT NOT NULL,
    frequency TEXT NOT NULL,
    asset_under_simulation TEXT NOT NULL,
    initial_balance NUMERIC NOT NULL,
    current_balance NUMERIC NOT NULL
);

DROP TABLE IF EXISTS account_position;

CREATE TABLE IF NOT EXISTS account_position (
    account_id TEXT PRIMARY KEY NOT NULL,
    account_name TEXT NOT NULL,
    position_type TEXT NOT NULL,
    position_amount NUMERIC NOT NULL,
    position_quantity NUMERIC NOT NULL,
    simulation_id TEXT NOT NULL,
    FOREIGN KEY(simulation_id) REFERENCES simulation(simulation_id)
);