# 2026-07-01 Interface Docs Re-test

## Scope

Re-tested the three local API interface documents in
`C:\Users\19351\Desktop\tem` from their current contents:

- `GPT大模型接口说明文档.md`
- `Claude大模型接口说明文档.md`
- `DeepSeek大模型接口说明文档.md`

The request prompt was `Reply with exactly one word: ok`. Project records use
redacted credential hints only.

## Results

| Provider doc | Endpoint | Model | Result |
| --- | --- | --- | --- |
| GPT | `POST https://coderxiaoc.com/v1/responses` | `gpt-5.5` | HTTP 200 on attempt 2, returned `ok` |
| GPT | `POST https://coderxiaoc.com/v1/responses` | `gpt-5.4` | HTTP 200 on attempt 1, returned `ok` |
| Claude | `POST https://coderxiaoc.com/v1/messages` | `claude-opus-4-8` | HTTP 502 after 5 attempts with regular doc key; HTTP 502 after 5 attempts with Desktop token |
| Claude | `POST https://coderxiaoc.com/v1/messages` | `claude-opus-4-7` | HTTP 502 after 5 attempts with regular doc key; HTTP 502 after 5 attempts with Desktop token |
| Claude | `POST https://coderxiaoc.com/v1/messages` | `claude-opus-4-6` | HTTP 502 after 5 attempts with regular doc key; HTTP 502 after 5 attempts with Desktop token |
| DeepSeek | `POST https://api.deepseek.com/chat/completions` | `deepseek-v4-flash` | HTTP 200 on attempt 1, returned `ok` |
| DeepSeek | `POST https://api.deepseek.com/chat/completions` | `deepseek-v4-pro` | HTTP 200 on attempt 1, returned `ok` |

## Interpretation

GPT and DeepSeek docs are currently runnable as direct HTTP examples.

Claude direct HTTP requests reached the documented endpoint shape but failed
with HTTP 502 after the documented retry window. Treat this as current
upstream/direct-request unavailability, not as proof that the Claude aliases
are invalid or that Claude Desktop/CC Switch cannot work through its client
path.

## Same-day Claude-only Re-test

After the initial all-doc test, Claude was re-tested separately.

| Credential path | Header variant | Model | Result |
| --- | --- | --- | --- |
| Regular Claude doc key | Standard Anthropic Messages headers | `claude-opus-4-8` | HTTP 200 on attempt 1, returned `ok` |
| Regular Claude doc key | Standard Anthropic Messages headers | `claude-opus-4-7` | HTTP 200 on attempt 1, returned `ok` |
| Regular Claude doc key | Standard Anthropic Messages headers | `claude-opus-4-6` | HTTP 200 on attempt 1, returned `ok` |
| Desktop direct provider token | Standard Anthropic Messages headers | `claude-opus-4-8` | HTTP 502 after 5 attempts |
| Desktop direct provider token | Standard Anthropic Messages headers | `claude-opus-4-7` | HTTP 502 after 5 attempts |
| Desktop direct provider token | Standard Anthropic Messages headers | `claude-opus-4-6` | HTTP 502 after 5 attempts |
| Regular Claude doc key | Claude Code/Desktop beta header | `claude-opus-4-8` | HTTP 200 on attempt 1, returned `ok` |
| Regular Claude doc key | Claude Code/Desktop beta header | `claude-opus-4-7` | HTTP 200 on attempt 1, returned `ok` |
| Regular Claude doc key | Claude Code/Desktop beta header | `claude-opus-4-6` | HTTP 200 on attempt 1, returned `ok` |

Updated interpretation: the Claude document is runnable with the regular API
key. The earlier Claude 502s were transient gateway/upstream failures for that
direct request path. The Desktop token remains unavailable through naked direct
HTTP in this test.

## Evidence Boundary

This re-test checks local interface-document requestability only. It does not
complete AI-Scientist-v2 LLM-client smoke, full live/BFTS run, human
annotation, provider billing, or AAAI submission readiness.
