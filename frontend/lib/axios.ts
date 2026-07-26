import axios from "axios";

const api = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_BASE_URL,
    headers: {
        "Content-Type": "application/json",
    },
});

// Add JWT token to every request
api.interceptors.request.use(
    (config) => {
        if (typeof window !== "undefined") {
            const token = localStorage.getItem("resume_ai_token");

            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }
        }

        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Handle authentication errors globally
api.interceptors.response.use(
    (response) => response,
    (error) => {

        if (
            typeof window !== "undefined" &&
            error.response?.status === 401
        ) {

            // Don't redirect for failed login attempts
            if (!error.config?.url?.includes("/auth/login")) {
                localStorage.removeItem("resume_ai_token");
                window.location.href = "/login";
            }

        }

        return Promise.reject(error);
    }
);

export default api;