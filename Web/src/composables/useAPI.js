import axios from "axios";
// Define the API base URL
const API_BASE_URL = "http://localhost:5000/api";

// Create a single, shared Axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // Important for sending cookies
});

// The composable now simply exposes functions that use the shared `api` instance
export const useAPI = () => {
  const sendGoogleEmail = async (mailData) => {
    try {
      // The interceptor will automatically add the auth header
      const response = await api.post("/send_google_email", mailData);
      return response.data;
    } catch (error) {
      console.error("Error sending mail:", error);
      throw error;
    }
  };

  const sendMicrosoftEmail = async (mailData) => {
    try {
      // The interceptor will automatically add the auth header
      const response = await api.post("/send_microsoft_email", mailData);
      return response.data;
    } catch (error) {
      console.error("Error sending mail:", error);
      throw error;
    }
  };

  return {
    sendGoogleEmail,
    sendMicrosoftEmail,
  };
};
