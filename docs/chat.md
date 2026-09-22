# Chat, comparisons, and memory

## Start and use

Restart the existing PyCharm MathApp configuration and open http://localhost:3001.
Select a saved conversation or choose New chat. Enter sends; Shift+Enter inserts
a newline. Follow-ups now send the conversation ID and receive earlier context.
Click View insights on an assistant message to inspect that turn. On narrow
screens, the chart button opens insights and the menu button opens conversations.
Chats survive reloads; select one in the sidebar to resume. Messages paginate
newest-first, with Load earlier messages for older pages.

The plus button accepts one PNG/JPEG/WebP image or PDF (10 MB maximum) and an
optional caption. Uploads use multipart instead of JSON base64. Extraction runs
once per upload; subsequent turns use saved text. Original binaries are not
retained or resent. Image OCR still requires EasyOCR from backend/requirements.txt;
PDF extraction requires pdfplumber. The existing OCR is English, and scanned PDFs
are not supported. The browser does not apply lossy resizing to math images.

You can also copy a screenshot/image and press Ctrl+V in the message field
(Cmd+V on macOS). A thumbnail appears before sending; add a caption or remove
the attachment with its X button. Pasting does not upload or spend API tokens.
Plain text and LaTeX still paste normally. One attachment per message is accepted;
remove an existing attachment first. Clipboard HTML/remote image links are not
downloaded automatically. The same file types and 10 MB limit apply.

## What the right panel means

- Local classifier: three class scores and a predicted subject. Confidence is
  uncalibrated, not measured accuracy on that question. Follow-ups are classified
  from their own text and can be UNKNOWN even when the conversation is calculus.
- OpenAI: contextual subject and short final answer, returned with the solution
  in one request. OTHER covers arithmetic and other subjects outside the local
  model's three classes. This is not independently verified ground truth.
- Reviewed reference: owners/staff can save a known answer and subject for their
  own problem. Reviewer and time are recorded. Compare the reference with the
  generated answer; arbitrary mathematical equivalence is not auto-graded.
- Usage: recorded input, cached input, output tokens, model and context mode.

References and predictions do not automatically become approved training data.

## Compact memory and API cost

The browser sends only the new message/file and conversation ID. PostgreSQL
keeps complete original messages. The backend sends at most four complete recent
turns (eight messages), within 12,000 history characters. It never slices equations
or individual messages. Character counts are not token counts. The current
extracted task is separately limited to 20,000 characters.

Each successful OpenAI response includes answer, subject, final answer and memory
in one structured response. Memory is ideally under 120 words, with a hard limit
of 3,000 characters. Each assistant message stores its own derived snapshot.
When history is too long, the latest snapshot and recent complete turns replace
replaying the full transcript. Summaries are fallible and can omit old details;
restate exact earlier equations when needed. Full original messages remain intact.
Older long chats without a snapshot fail explicitly before spending, asking the
user to start a new chat with the relevant problem.

There is no extra paid classification, summary or answer-grading call. The memory
and comparison fields add some tokens on short chats; bounded history reduces
growth on long chats. Actual savings depend on conversation length and responses.
An open session does not make history free. Minifying JSON or gzipping it does
not reduce billed text tokens. Stable instructions allow provider prompt caching
where available; only provider-reported cached usage is displayed.

The app uses store=False and manages conversation state itself. Output tokens
remain capped by OPENAI_MAX_OUTPUT_TOKENS. SDK automatic retries are disabled.
Malformed/incomplete responses are not saved as answers; measured usage from
those responses is recorded on failed SolveEvents. Network failures may have
unknown billed usage.

The browser blocks double-click sends. A database lease blocks simultaneous
requests in an existing chat, released on completion/failure or after ten minutes
following a crash. A process-local throttle permits six solve requests per minute
per user. These are development guards, not hard dollar caps, daily quotas,
distributed limits or request idempotency. New chats can be created concurrently.
Before hosting, add shared rate limits, idempotency, budget reservation and the
agreed invited-testers access. Do not claim the deployment is production-ready.

## Compressed files

The download icon exports a lossless .json.gz containing all conversation message
text and roles. Streaming gzip keeps export memory bounded. Standard archive
tools can unpack it. This is download/backup compression, separate from the
model-generated summary. Database originals are never replaced with summaries
or compressed blobs.

## Endpoints and data

- POST /api/solver/solve/: text JSON or multipart attachment plus conversation_id;
  returns saved messages with analysis, keeping memory backend-only.
- GET /api/solver/conversations/: owner-only paginated chats.
- GET /api/solver/conversations/{id}/messages/: newest-first messages.
- GET /api/solver/conversations/{id}/export/: owner-only streamed gzip.
- PATCH /api/solver/problems/{id}/reference/: staff + owner only, answer and label.
- POST /api/solver/classify/: existing local-only classification endpoint.

Migration 0004 adds Conversation leases, Message analysis/memory, Problem review
fields, and SolveEvent cached-input counts. Existing data remains. SolveHistory
still duplicates successful turns for compatibility; remove that storage only
through a separately tested history migration.

JWT refresh shares one pending request and persists rotated refresh tokens.
Login errors no longer trigger a refresh loop. Markdown rendering disables raw
HTML and remote images; KaTeX uses trust=False.

## Development verification

Run the repository tests (all paid provider calls mocked), Django checks and
npm --prefix frontend run build. Tests cover follow-up context, compact limits,
original preservation, ownership, review permissions, lease cleanup, failure
usage, multipart reuse, and lossless export.

Compatible npm security patches were applied. Remaining audit findings require
major Vite/esbuild and React Router upgrades before hosting; these were not
forced during the chat change. The production build succeeds with a large
Markdown/KaTeX chunk warning. Live provider output quality and summary fidelity
still require real user testing.

For a no-cost visual test, visit http://localhost:3001/dev/chat-preview.html.
The account is visibly named Offline preview. It uses fictional fixtures and an
adapter that intercepts every API request; it never calls Django/OpenAI. It is
available only in the Vite dev server and excluded from the production entry.

Official sources:
- https://developers.openai.com/api/docs/guides/structured-outputs
- https://developers.openai.com/api/docs/guides/conversation-state
