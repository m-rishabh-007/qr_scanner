import React from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";

export function PeriodSelector({ value, onChange }: { value: number; onChange: (value: 7 | 30 | 90) => void }) {
  return (
    <View style={styles.row}>
      {([7, 30, 90] as const).map((period) => (
        <Pressable key={period} onPress={() => onChange(period)} style={[styles.item, value === period && styles.selected]}>
          <Text style={[styles.label, value === period && styles.selectedLabel]}>{period} days</Text>
        </Pressable>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: "row", backgroundColor: "#EAECF0", borderRadius: 12, padding: 4 },
  item: { flex: 1, alignItems: "center", paddingVertical: 9, borderRadius: 9 },
  selected: { backgroundColor: "#FFFFFF" },
  label: { color: "#667085", fontWeight: "600" },
  selectedLabel: { color: "#172033" }
});
