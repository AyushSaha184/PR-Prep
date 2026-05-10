# Changelog

All notable changes to this project will be documented in this file.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.1.0] - 2026-05-10
### Added
- Initial release
- LangGraph-orchestrated PR preparation agent
- Short-circuit routing: trivial / Flash / Pro / cached
- Parallel AST parsing via LangGraph Send API
- Breaking change detection via tree-sitter symbol diffing
- MD5 hash caching to avoid redundant LLM calls
- Streaming output via Gemini generate_content_stream
- Human-in-the-loop review gate with edit/submit/abort
- GitHub PR submission via gh CLI
- Tiered model routing: gemini-1.5-flash and gemini-1.5-pro

