# Project Assistant Guidelines

## Efficient context usage

- Read only files directly related to the requested change.
- Prefer targeted searches with line limits over directory-wide scans.
- Avoid rereading unchanged files or repeating tool output.
- Run commands with concise output and disable pagers.
- Use the smallest relevant validation command.
- Do not start the server or run migrations unless explicitly requested.
- Do not delegate simple lookups or small edits to sub-agents.
- Use sub-agents only for genuinely complex, independent work.
- Keep responses concise and summarize only meaningful changes.
- Do not create planning or status files unless explicitly requested.
- Never include an assistant name or tag in filenames.

## Change discipline

- Make precise, scoped edits and preserve unrelated user changes.
- Follow existing project conventions.
- Do not expose secrets or commit local environment files.
- Validate changed behavior without introducing unnecessary tools or dependencies.
