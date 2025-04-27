/* ASI1-Mini LLM README
 *
 * A minimal guide to using the ASI1-Mini chat‐completion API
 * Copy this file into your IDE to get started.
 */

/* Prerequisites
 *  - ASI1_API_KEY set in your environment
 *  - curl or any HTTP client
 *  - (Optional) JavaScript or Python runtime for examples
 */

/* Base URL & Auth
 *  URL: https://api.asi1.ai/v1/chat/completions
 *  Header:
 *    Authorization: Bearer $ASI1_API_KEY
 *    Content-Type: application/json
 */

/* Create a Chat Completion
 *
 * Request:
 *  POST /v1/chat/completions
 *  Body:
 *    {
 *      "model": "asi1-mini",            // model ID
 *      "messages": [                    // conversation history
 *        { "role": "system", "content": "You are a helpful assistant." },
 *        { "role": "user",   "content": "Hello!" }
 *      ],
 *      "temperature": 0.7,              // 0.0–2.0
 *      "stream": false,                 // true for SSE
 *      "max_tokens": 1024               // cap response tokens
 *    }
 *
 * curl example:
 *  curl -X POST https://api.asi1.ai/v1/chat/completions \
 *    -H "Authorization: Bearer $ASI1_API_KEY" \
 *    -H "Content-Type: application/json" \
 *    -d '{
 *      "model": "asi1-mini",
 *      "messages": [
 *        { "role": "system", "content": "You are a helpful assistant." },
 *        { "role": "user",   "content": "Tell me a joke." }
 *      ],
 *      "temperature": 0.8,
 *      "stream": false,
 *      "max_tokens": 150
 *    }'
 */

/* JavaScript (fetch) Example
 *
 * const resp = await fetch("https://api.asi1.ai/v1/chat/completions", {
 *   method: "POST",
 *   headers: {
 *     "Authorization": `Bearer ${process.env.ASI1_API_KEY}`,
 *     "Content-Type": "application/json"
 *   },
 *   body: JSON.stringify({
 *     model: "asi1-mini",
 *     messages: [
 *       { role: "system", content: "You are a helpful assistant." },
 *       { role: "user",   content: "Help me write a summary." }
 *     ],
 *     temperature: 0.5,
 *     stream: false,
 *     max_tokens: 200
 *   })
 * });
 * const data = await resp.json();
 * console.log(data.choices[0].message.content);
 */

/* Python (requests) Example
 *
 * import os, requests
 *
 * url = "https://api.asi1.ai/v1/chat/completions"
 * headers = {
 *   "Authorization": f"Bearer {os.getenv('ASI1_API_KEY')}",
 *   "Content-Type": "application/json"
 * }
 * payload = {
 *   "model": "asi1-mini",
 *   "messages": [
 *     { "role": "system", "content": "You are a helpful assistant." },
 *     { "role": "user",   "content": "Draft an email reply." }
 *   ],
 *   "temperature": 0.6,
 *   "stream": False,
 *   "max_tokens": 250
 * }
 *
 * resp = requests.post(url, json=payload, headers=headers)
 * resp.raise_for_status()
 * print(resp.json()["choices"][0]["message"]["content"])
 */

/* Response Format
 *
 * {
 *   "model": "asi1-mini",
 *   "id": "id_…",
 *   "executed_data": [],          // reserved
 *   "conversation_id": null,      // or string
 *   "thought": [ "internal reasoning" ],
 *   "tool_thought": [],           // if tools used
 *   "choices": [
 *     {
 *       "index": 0,
 *       "finish_reason": "stop",
 *       "message": {
 *         "role": "assistant",
 *         "content": "Your reply here."
 *       }
 *     }
 *   ],
 *   "usage": {
 *     "prompt_tokens": 39,
 *     "completion_tokens": 22,
 *     "total_tokens": 61
 *   }
 * }
 */

/* Streaming
 *  - Set "stream": true
 *  - Read SSE data events until [DONE]
 */

/* Errors
 *  4xx: client errors (invalid key, bad JSON)
 *  5xx: server errors (retry with backoff)
 */

/* Next Steps
 *  - Integrate into your app logic
 *  - Maintain dynamic messages for context
 *  - Tune temperature and max_tokens for your use case
 */
