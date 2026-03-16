import api from "./axios";

export const register = (payload) => api.post("/auth/register", payload);

export const login = (payload) => api.post("/auth/login", payload);

export const getMe = () => api.get("/auth/me");

export const getUsers = () => api.get("/users");

export const createUser = (payload) => api.post("/users", payload);
