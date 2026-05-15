# Ralph Loop Correction Restart

Restart Ralph on the correction queue.

This requires the Anthropic-verified Ralph Loop plugin installed in Claude Code: https://claude.com/plugins/ralph-loop.

Use this executor command shape:

```text
/ralph-loop:ralph-loop "Read @docs/roadmap/<feature>/ralph-loop-prompt.md, @docs/roadmap/<feature>/correction-queue.md, and @docs/roadmap/<feature>/gates.md. Close every blocking correction with evidence, wait 5 minutes, reread the correction queue, and repeat until no blocking correction remains open." --max-iterations 20 --completion-promise RALPH_DONE
```

If Claude Code exposes the plugin command as `/ralph-loop`, use that command name with the same prompt and flags.

Before restart, make sure every blocking correction has an ID, severity, risk, required fix, acceptance criteria, and evidence fields.
