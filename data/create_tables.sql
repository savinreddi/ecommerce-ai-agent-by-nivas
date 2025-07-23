
DROP TABLE IF EXISTS ad_sales;
CREATE TABLE ad_sales (
    date TEXT,
    item_id INTEGER,
    ad_sales REAL,
    impressions INTEGER,
    ad_spend REAL,
    clicks INTEGER,
    units_sold INTEGER
);

DROP TABLE IF EXISTS total_sales;
CREATE TABLE total_sales (
    date TEXT,
    item_id INTEGER,
    total_sales REAL,
    total_units_ordered INTEGER
);

DROP TABLE IF EXISTS eligibility;
CREATE TABLE eligibility (
    eligibility_datetime_utc TEXT,
    item_id INTEGER,
    eligibility BOOLEAN,
    message TEXT
);
