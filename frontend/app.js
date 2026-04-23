const express = require('express');
const axios = require('axios');
const path = require('path');
const app = express();

// Allow API_URL to be configured via environment variable
const API_URL = process.env.API_URL || "http://localhost:8000";
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static(path.join(__dirname, 'views')));

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'healthy' });
});

app.post('/submit', async (req, res) => {
  try {
    const response = await axios.post(`${API_URL}/jobs`, {}, {
      timeout: 5000
    });
    res.json(response.data);
  } catch (err) {
    console.error('Error submitting job:', err.message);
    res.status(500).json({ error: "Failed to submit job" });
  }
});

app.get('/status/:id', async (req, res) => {
  try {
    const response = await axios.get(`${API_URL}/jobs/${req.params.id}`, {
      timeout: 5000
    });
    res.json(response.data);
  } catch (err) {
    if (err.response && err.response.status === 404) {
      return res.status(404).json({ error: "Job not found" });
    }
    console.error('Error fetching job status:', err.message);
    res.status(500).json({ error: "Failed to fetch job status" });
  }
});

app.listen(PORT, () => {
  console.log(`Frontend running on port ${PORT}`);
  console.log(`API URL configured as: ${API_URL}`);
});
