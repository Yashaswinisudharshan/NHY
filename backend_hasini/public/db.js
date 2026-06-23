const { Pool } = require("pg");

const pool = new Pool({
    user: "postgres",
    host: "localhost",
    database: "corruption_portal",
    password: "Hasini@1901",
    port: 5432,
});

module.exports = pool;