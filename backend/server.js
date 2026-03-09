import express from "express";
import dotenv from "dotenv";
import marketRoutes from "./routes/market.js"; // default export

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware to parse JSON
app.use(express.json());

// Use market routes with /api prefix
app.use("/api/market", marketRoutes);

// Root route
app.get("/", (req, res) => {
  res.send("DeltaPilot Backend is running!");
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});