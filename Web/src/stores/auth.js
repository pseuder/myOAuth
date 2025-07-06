import { defineStore } from "pinia";
import axios from "axios";

// Define the API base URL
const API_BASE_URL = "http://localhost:5000/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // Important for sending session cookies
});

export const useAuthStore = defineStore("auth", {
  state: () => ({
    googleUser: null,
    microsoftUser: null,
    isLoggedInGoogle: false,
    isLoggedInMicrosoft: false,
  }),
  getters: {
    isAuthenticatedGoogle: (state) => state.isLoggedInGoogle,
    isAuthenticatedMicrosoft: (state) => state.isLoggedInMicrosoft,
    googleUserInfo: (state) => state.googleUser,
    microsoftUserInfo: (state) => state.microsoftUser,
  },
  actions: {
    async login(provider) {
      try {
        const response = await api.get(`/auth/${provider}/login`);
        const { authorization_url } = response.data;
        return authorization_url;
      } catch (error) {
        console.error(`Error during ${provider} login:`, error);
        return null;
      }
    },
    logout(provider) {
      if (provider === "google") {
        this.googleUser = null;
        this.isLoggedInGoogle = false;
      } else if (provider === "microsoft") {
        this.microsoftUser = null;
        this.isLoggedInMicrosoft = false;
      }
      api
        .post("/auth/logout")
        .catch((err) => console.error("Logout failed", err));
    },
    handleLoginCallback({ provider, userInfo }) {
      if (provider === "google") {
        this.googleUser = userInfo;
        this.isLoggedInGoogle = true;
      } else if (provider === "microsoft") {
        this.microsoftUser = userInfo;
        this.isLoggedInMicrosoft = true;
      }
    },
  },
});
