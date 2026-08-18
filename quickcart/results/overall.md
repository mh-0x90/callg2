## Targetted vulnerabilites

- Blind info leak in getattr(mode, AMK)/Blind template detection - audit.py:9
- Weak authentication in error page
- Auditor authentication flow break- business logic error - validation.py:12
- Unencrypted Logging

#### The repo also includes minor vulnerabilites to create the complicated flow

Analysis

Semgrep: 1 FP
CodeQL: 2 TP
ClaudeSDK with GPT 5.5: 1 targetted vulnerability identified