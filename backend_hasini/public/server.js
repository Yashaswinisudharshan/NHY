const express = require("express");
const cors = require("cors");
const pool = require("./db");

const app = express();

app.use(cors());
app.use(express.json());

app.get("/", (req, res) => {
    res.send("Backend Running");
});
app.get("/api/dashboard", async (req, res) => {
    try {
        const projects = await pool.query(
            "SELECT COUNT(*) FROM projects"
        );

        const districts = await pool.query(
            "SELECT COUNT(*) FROM districts"
        );

        const funds = await pool.query(
            "SELECT SUM(allocated) FROM funds"
        );

        const utilized = await pool.query(
            "SELECT SUM(utilized) FROM funds"
        );

        res.json({
            totalProjects: projects.rows[0].count,
            totalDistricts: districts.rows[0].count,
            totalFunds: funds.rows[0].sum,
            totalUtilized: utilized.rows[0].sum
        });

    } catch (err) {
        console.error(err);
        res.status(500).send("Database Error");
    }
});

app.get("/api/projects", async (req, res) => {
    try {
        const result = await pool.query("SELECT * FROM projects");
        res.json(result.rows);
    } catch (err) {
        console.error(err);
        res.status(500).send("Database Error");
    }
});
app.post("/api/projects", async (req, res) => {
    try {
        const {
            project_name,
            district_id,
            budget,
            utilized,
            progress,
            status
        } = req.body;

        const result = await pool.query(
            `INSERT INTO projects
            (project_name, district_id, budget, utilized, progress, status)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING *`,
            [
                project_name,
                district_id,
                budget,
                utilized,
                progress,
                status
            ]
        );

        res.json(result.rows[0]);

    } catch (err) {
        console.error(err);
        res.status(500).send("Database Error");
    }
});
app.put("/api/projects/:id", async (req, res) => {
    try {
        const { id } = req.params;

        const {
            progress,
            status
        } = req.body;

        const result = await pool.query(
            `UPDATE projects
             SET progress = $1,
                 status = $2
             WHERE project_id = $3
             RETURNING *`,
            [progress, status, id]
        );

        res.json(result.rows[0]);
    } catch (err) {
        console.error(err);
        res.status(500).send("Database Error");
    }
});
app.delete("/api/projects/:id", async (req, res) => {
    try {
        const { id } = req.params;

        await pool.query(
            "DELETE FROM projects WHERE project_id = $1",
            [id]
        );

        res.json({
            message: "Project Deleted"
        });
    } catch (err) {
        console.error(err);
        res.status(500).send("Database Error");
    }
});
app.get("/api/districts", async (req, res) => {
    const result = await pool.query("SELECT * FROM districts");
    res.json(result.rows);
});

app.get("/api/officers", async (req, res) => {
    const result = await pool.query("SELECT * FROM officers");
    res.json(result.rows);
});

app.get("/api/funds", async (req, res) => {
    const result = await pool.query("SELECT * FROM funds");
    res.json(result.rows);
});

app.listen(12345, () => {
    console.log("SERVER ON 12345");
});