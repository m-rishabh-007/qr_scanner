import Constants from "expo-constants";

const value = Constants.expoConfig?.extra?.apiBaseUrl;
export const API_BASE_URL = typeof value === "string" ? value.replace(/\/$/, "") : "http://10.0.2.2:8000";
