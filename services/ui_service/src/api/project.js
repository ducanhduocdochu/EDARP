import api from "./axios";

export const getModels = () => api.get("/projects/models");

export const getProjects = () => api.get("/projects");

export const getProject = (id) => api.get(`/projects/${id}`);

export const createProject = (payload) => api.post("/projects", payload);

export const updateProject = (id, payload) => api.put(`/projects/${id}`, payload);

export const getApiKeys = (projectId) =>
  api.get(`/projects/${projectId}/api-keys`);

export const createApiKey = (projectId) =>
  api.post(`/projects/${projectId}/api-keys`);

export const getDocuments = (projectId) =>
  api.get(`/projects/${projectId}/documents`);

export const createDocument = (projectId, payload) =>
  api.post(`/projects/${projectId}/documents`, payload);

export const deleteDocument = (documentId) =>
  api.delete(`/documents/${documentId}`);

export const embedText = (projectId, text) =>
  api.post(`/projects/${projectId}/documents/embed`, { text });

export const embedBatch = (projectId, texts) =>
  api.post(`/projects/${projectId}/documents/embed-batch`, { texts });
