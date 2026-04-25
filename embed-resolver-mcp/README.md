# TMDB Embed Resolver MCP

Local MCP server that turns known TMDB IDs into provider URLs.

This service does not search TMDB. Use the TMDB MCP server to discover media and confirm the `media_type` plus `tmdb_id`, then call this resolver once the user chooses something.

## Tools

- `list_embed_providers` - returns configured provider names.
- `generate_embed_urls_for_tmdb` - returns provider URLs and a local UI prefill URL.

## Inputs

`generate_embed_urls_for_tmdb` accepts:

- `media_type`: `movie` or `tv`
- `tmdb_id`: TMDB movie or TV ID
- `season`: TV season, defaults to `1`
- `episode`: TV episode, defaults to `1`
- `providers_json`: optional JSON array of provider names, defaults to all providers

## Development

```bash
docker build -f embed-resolver-mcp/Dockerfile -t tmdb-embed-resolver .
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | python embed-resolver-mcp/server.py
```

## Configuration

- `TMDB_EMBED_UI_BASE_URL`: base URL used for generated UI prefill links. Defaults to `http://localhost:8689`.
- `TMDB_PROVIDERS_PATH`: optional path to a provider JSON file.

The default Docker image uses the root `providers.json`.
