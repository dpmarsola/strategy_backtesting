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

DROP TABLE IF EXISTS trades;

CREATE TABLE IF NOT EXISTS trades (
    trade_open_date TIMESTAMP PRIMARY KEY NOT NULL,
    simulation_id TEXT NOT NULL,
    asset_under_simulation TEXT NOT NULL,
    position_type TEXT NOT NULL,
    position_amount NUMERIC NOT NULL,
    position_quantity NUMERIC NOT NULL,
    trade_close_date TIMESTAMP NOT NULL,
    trade_close_amount NUMERIC NOT NULL,
    profit_amount NUMERIC NOT NULL,
    profit_percentage NUMERIC NOT NULL, 
    FOREIGN KEY(simulation_id) REFERENCES simulation(simulation_id)
);
