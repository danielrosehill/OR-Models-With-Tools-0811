# Kimi K2 Thinking - Full API Response

Model ID: `moonshotai/kimi-k2-thinking`

## Full JSON Response

```json
{
  "id": "moonshotai/kimi-k2-thinking",
  "canonical_slug": "moonshotai/kimi-k2-thinking-20251106",
  "hugging_face_id": "moonshotai/Kimi-K2-Thinking",
  "name": "MoonshotAI: Kimi K2 Thinking",
  "created": 1762440622,
  "description": "Kimi K2 Thinking is Moonshot AI's most advanced open reasoning model to date, extending the K2 series into agentic, long-horizon reasoning. Built on the trillion-parameter Mixture-of-Experts (MoE) architecture introduced in Kimi K2, it activates 32 billion parameters per forward pass and supports 256 k-token context windows. The model is optimized for persistent step-by-step thought, dynamic tool invocation, and complex reasoning workflows that span hundreds of turns. It interleaves step-by-step reasoning with tool use, enabling autonomous research, coding, and writing that can persist for hundreds of sequential actions without drift.\n\nIt sets new open-source benchmarks on HLE, BrowseComp, SWE-Multilingual, and LiveCodeBench, while maintaining stable multi-agent behavior through 200–300 tool calls. Built on a large-scale MoE architecture with MuonClip optimization, it combines strong reasoning depth with high inference efficiency for demanding agentic and analytical tasks.",
  "context_length": 262144,
  "architecture": {
    "modality": "text->text",
    "input_modalities": [
      "text"
    ],
    "output_modalities": [
      "text"
    ],
    "tokenizer": "Other",
    "instruct_type": null
  },
  "pricing": {
    "prompt": "0.0000006",
    "completion": "0.0000025",
    "request": "0",
    "image": "0",
    "web_search": "0",
    "internal_reasoning": "0",
    "input_cache_read": "0.00000015"
  },
  "top_provider": {
    "context_length": 262144,
    "max_completion_tokens": 262144,
    "is_moderated": false
  },
  "per_request_limits": null,
  "supported_parameters": [
    "frequency_penalty",
    "include_reasoning",
    "max_tokens",
    "presence_penalty",
    "reasoning",
    "response_format",
    "stop",
    "structured_outputs",
    "temperature",
    "tool_choice",
    "tools",
    "top_p"
  ],
  "default_parameters": {
    "temperature": null,
    "top_p": null,
    "frequency_penalty": null
  }
}
```
