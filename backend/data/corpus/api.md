# API Reference

Shakers exposes a RESTful API at `https://api.shakers.io/v1`. All endpoints require a valid Bearer token.

## Authentication

- **Header**: `Authorization: Bearer <your_api_token>`

## Endpoints

### Create Workspace

```http
POST /v1/workspaces
Content-Type: application/json

{
  "name": "Project Phoenix",
  "privacy": "private"
}
