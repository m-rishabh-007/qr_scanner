import { Redirect } from "expo-router";
import React from "react";
import { ActivityIndicator, View } from "react-native";

import { useAuth } from "@/store/auth";

export default function Index() {
  const { ready, accessToken } = useAuth();
  if (!ready) return <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}><ActivityIndicator /></View>;
  return <Redirect href={accessToken ? "/(tabs)" : "/(auth)/login"} />;
}
