# 2026-06-30 DeepSeek Interface Docs Runnable Check

## Goal

Verify whether the DeepSeek temporary key can actually call the DeepSeek API and then provide a local interface document in the same minimal format as the GPT/Claude docs.

## Checked Artifact

- DeepSeek temporary key: `sk-a858...af98`

## Request Shapes

- Models returned by `/models`:
  - `deepseek-v4-flash`
  - `deepseek-v4-pro`
- Chat endpoint: `POST https://api.deepseek.com/chat/completions`

## Test Method

- First call `GET /models` with `Authorization: Bearer <API-Key>`.
- Then call `/chat/completions` with a minimal prompt: `Reply with exactly one word: ok`
- Retry rule: up to 5 attempts per model, with a short pause between failures.

## Results

- `/models`: HTTP 200 on attempt 1; returned `deepseek-v4-flash` and `deepseek-v4-pro`.
- `deepseek-v4-flash`: HTTP 200 on attempt 1.
- `deepseek-v4-pro`: HTTP 200 on attempt 1.
- `deepseek-v4-flash` with a slightly larger `max_tokens` also returned visible content `ok`.

## Conclusion

The DeepSeek temporary key is usable, and the interface requests run successfully.
