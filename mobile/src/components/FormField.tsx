import React from "react";
import { StyleSheet, Text, TextInput, type TextInputProps, View } from "react-native";

export function FormField({ label, error, ...props }: TextInputProps & { label: string; error?: string }) {
  return (
    <View style={styles.wrapper}>
      <Text style={styles.label}>{label}</Text>
      <TextInput autoCapitalize="none" placeholderTextColor="#98A2B3" style={[styles.input, !!error && styles.inputError]} {...props} />
      {!!error && <Text style={styles.error}>{error}</Text>}
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: { gap: 6 },
  label: { fontWeight: "700", color: "#172033" },
  input: { minHeight: 48, backgroundColor: "#FFFFFF", borderColor: "#D0D5DD", borderWidth: 1, borderRadius: 12, paddingHorizontal: 12, color: "#172033" },
  inputError: { borderColor: "#B42318" },
  error: { color: "#B42318" }
});
