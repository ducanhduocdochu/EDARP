import api from "./axios";

export const queryRAG = (projectId, query, options = {}) =>
  api.post(`/query/${projectId}`, {
    query,
    top_k: options.topK ?? 3,
    max_new_tokens: options.maxNewTokens ?? undefined,
    temperature: options.temperature ?? undefined,
  });
