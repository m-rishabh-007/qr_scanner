import { Tabs, router } from "expo-router";
import React from "react";
import { Pressable, Text } from "react-native";

export default function TabsLayout() {
  return (
    <Tabs screenOptions={{
      headerShadowVisible: false,
      headerStyle: { backgroundColor: "#F4F7FB" },
      tabBarActiveTintColor: "#2457D6",
      headerRight: () => <Pressable accessibilityLabel="Settings" onPress={() => router.push("/settings")} style={{ paddingHorizontal: 16 }}><Text style={{ fontSize: 22 }}>⚙</Text></Pressable>
    }}>
      <Tabs.Screen name="index" options={{ title: "Overview", tabBarIcon: ({ color }) => <Text style={{ color }}>▥</Text> }} />
      <Tabs.Screen name="feedback" options={{ title: "Feedback", tabBarIcon: ({ color }) => <Text style={{ color }}>☰</Text> }} />
      <Tabs.Screen name="qr" options={{ title: "QR", tabBarIcon: ({ color }) => <Text style={{ color }}>▦</Text> }} />
    </Tabs>
  );
}
