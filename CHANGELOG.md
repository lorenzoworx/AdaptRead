# Changelog

## Unreleased

### Changed

- Prepare the frontend and API client for deployment beneath
  `/projects/adaptread/`.
- Publish a tested production container to GitHub Container Registry after
  successful `main` branch CI.
- Deploy verified `main` commits on a dedicated production runner, with an
  isolated candidate smoke test, public contract verification, and image
  rollback if promotion fails.
