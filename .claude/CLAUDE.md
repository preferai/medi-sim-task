General rules of interaction:
- Don't assume! Ask me anything that is unclear
- Don't be a sycophant; be straight with me
- Always be transparent
- Don't write too much text, shoot straight to the point

For writing, follow guidelines listed in @~/.claude/TROPES.md.

If enabled during the session, use Context7 when I need library/API documentation, code generation, setup or configuration steps without me having to explicitly ask.

For coding in Python:
- Always use uv
- Follow PEP8 convention as much as possible, but don't sacrifice functionality just for the sake of style
- Format code with ruff
- Check types with ty
- Run tests (when applicable) with pytest

For coding in general:
- Always follow DRY principle
- Don't overengineer - keep things as simple as possible, but not simpler!
- Make sure there's no dead code in the codebase you're currently working in
- Don't use overly verbose comments, and don't overly decorate comments with separators; have simplicity in mind
- Be meticulous when it comes to code style and types
