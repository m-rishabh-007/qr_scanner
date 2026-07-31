import React from "react";
import { StyleSheet, View, type ViewProps } from "react-native";

export function Card({ style, ...props }: ViewProps) {
  return <View style={[styles.card, style]} {...props} />;
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: "#FFFFFF",
    borderRadius: 16,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: "#D0D5DD",
    padding: 16,
    gap: 8
  }
});
