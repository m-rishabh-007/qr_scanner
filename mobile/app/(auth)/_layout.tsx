import { Stack } from "expo-router";
import React from "react";

export default function AuthLayout() {
  return <Stack screenOptions={{ headerShadowVisible: false, headerStyle: { backgroundColor: "#F4F7FB" } }} />;
}
