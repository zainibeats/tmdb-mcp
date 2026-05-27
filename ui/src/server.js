const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 8689;
const MCP_ENDPOINT = process.env.MCP_ENDPOINT || 'http://localhost:5000';

// Load providers configuration once at startup
const providersPath = path.join(__dirname, 'providers.json');
const providersConfig = JSON.parse(fs.readFileSync(providersPath, 'utf8'));

console.log(`Loaded ${providersConfig.providers.length} providers from providers.json`);

// Middleware
app.use(express.json());
app.use(express.static('public'));

// API endpoint to generate embed URLs
app.post('/api/generate-embeds', async (req, res) => {
  const { mediaType, tmdbId, season, episode, providers } = req.body;

  // Validate required fields
  if (!mediaType || !tmdbId) {
    return res.status(400).json({ error: 'mediaType and tmdbId are required' });
  }

  if (mediaType === 'tv' && (!season || !episode)) {
    return res.status(400).json({ error: 'season and episode are required for TV shows' });
  }

  try {
    // Generate URLs using the cached providers config

    // Generate URLs
    const results = [];
    const providerList = providers && providers.length > 0
      ? providers
      : providersConfig.providers.map(p => p.name);

    for (const providerConfig of providersConfig.providers) {
      if (!providerList.includes(providerConfig.name)) {
        continue;
      }

      const template = providerConfig[mediaType];
      if (!template) {
        continue;
      }

      let url = template.replace('{id}', tmdbId);

      if (mediaType === 'tv') {
        url = url.replace('{season}', season).replace('{episode}', episode);
      }

      results.push({
        provider: providerConfig.name,
        url: url
      });
    }

    res.json(results);
  } catch (error) {
    console.error('Error generating embed URLs:', error);
    res.status(500).json({ error: 'Failed to generate embed URLs', details: error.message });
  }
});

// API endpoint to get available providers
app.get('/api/providers', (req, res) => {
  const providerNames = providersConfig.providers.map(p => p.name);
  res.json(providerNames);
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok', mcp_endpoint: MCP_ENDPOINT });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`TMDB Embed UI running on http://0.0.0.0:${PORT}`);
  console.log(`MCP Endpoint: ${MCP_ENDPOINT}`);
});
