import type { ExpoConfig, ConfigContext } from "expo/config";

export default ({ config }: ConfigContext): ExpoConfig => {
  const appName = process.env.APP_NAME ?? "ReviewFlow Merchant";
  const slug = process.env.APP_SLUG ?? "reviewflow-merchant";
  const androidPackage = process.env.ANDROID_PACKAGE ?? "com.example.reviewflow";
  const scheme = process.env.APP_SCHEME ?? "reviewflow";

  return {
    ...config,
    name: appName,
    slug,
    version: "0.1.0",
    orientation: "portrait",
    icon: process.env.APP_ICON_PATH ?? "./assets/icon.png",
    scheme,
    userInterfaceStyle: "light",
    android: {
      package: androidPackage,
      versionCode: 1,
      adaptiveIcon: {
        foregroundImage: process.env.APP_ADAPTIVE_ICON_PATH ?? "./assets/adaptive-icon.png",
        backgroundColor: "#F4F7FB"
      },
      permissions: []
    },
    plugins: [
      "expo-router",
      "expo-secure-store",
      [
        "expo-splash-screen",
        {
          image: process.env.APP_SPLASH_PATH ?? "./assets/splash.png",
          resizeMode: "contain",
          backgroundColor: "#F4F7FB"
        }
      ]
    ],
    experiments: { typedRoutes: true },
    extra: {
      apiBaseUrl: process.env.EXPO_PUBLIC_API_BASE_URL ?? "http://10.0.2.2:8000",
      eas: { projectId: process.env.EAS_PROJECT_ID ?? undefined }
    }
  };
};
