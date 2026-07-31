import React from "react";
import { ActivityIndicator, Pressable, StyleSheet, Text } from "react-native";

export function PrimaryButton({ title, loading, disabled, onPress, destructive = false }: { title: string; loading?: boolean; disabled?: boolean; onPress: () => void; destructive?: boolean }) {
  return (
    <Pressable disabled={disabled || loading} onPress={onPress} style={[styles.button, destructive && styles.destructive, (disabled || loading) && styles.disabled]}>
      {loading ? <ActivityIndicator color="#FFFFFF" /> : <Text style={styles.text}>{title}</Text>}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  button: { minHeight: 48, borderRadius: 12, alignItems: "center", justifyContent: "center", backgroundColor: "#2457D6" },
  destructive: { backgroundColor: "#B42318" },
  disabled: { opacity: 0.5 },
  text: { color: "#FFFFFF", fontWeight: "800" }
});
