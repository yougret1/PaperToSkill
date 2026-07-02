# 2026-06-30 Interface Docs Runnable Check

## Goal

Verify whether the two local interface documents in `C:\Users\19351\Desktop\tem` actually produce runnable requests.

## Checked Artifacts

- `C:\Users\19351\Desktop\tem\GPT大模型接口说明文档.md`
- `C:\Users\19351\Desktop\tem\Claude大模型接口说明文档.md`

## Request Shapes

- GPT: `POST https://coderxiaoc.com/v1/responses`
- Claude: `POST https://coderxiaoc.com/v1/messages`

## Test Method

- Use the API keys embedded in the local documents.
- Send a minimal prompt: `Reply with exactly one word: ok`
- Retry rule: up to 5 attempts per model, with a short pause between failures.

## Results

- GPT `gpt-5.5`: HTTP 200 on attempt 1.
- GPT `gpt-5.4`: HTTP 200 on attempt 1.
- Claude `claude-opus-4-8`: HTTP 200 on attempt 1.
- Claude `claude-opus-4-7`: HTTP 200 on attempt 1.
- Claude `claude-opus-4-6`: HTTP 200 on attempt 1.

## Conclusion

Both local interface documents are runnable as written.
