import api from "./axios";

export const indexText = (projectId, text, metadata = {}) =>
  api.post(`/index/${projectId}/text`, { text, metadata });

export const indexJsonFile = (projectId, file) => {
  const form = new FormData();
  form.append("file", file);
  return api.post(`/index/${projectId}/json`, form, {
    headers: { "Content-Type": "multipart/form-data" },
    timeout: 300000,
  });
};

export const indexBatch = (projectId, documents) =>
  api.post(`/index/${projectId}/batch`, { documents });

export const searchIndex = (projectId, query, topK = 5) =>
  api.post(`/index/${projectId}/search`, { query, top_k: topK });

export const getIndexStatus = (projectId) =>
  api.get(`/index/${projectId}/status`);

export const clearIndex = (projectId) =>
  api.delete(`/index/${projectId}`);
