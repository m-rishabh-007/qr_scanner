import React, { useState } from "react";
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from "react-native";

import { useFeedback } from "@/api/hooks";
import { Card } from "@/components/Card";
import { PeriodSelector } from "@/components/PeriodSelector";
import { Screen } from "@/components/Screen";

const filters = ["", "high-rated", "neutral", "low-rated"] as const;

export default function FeedbackScreen() {
  const [period, setPeriod] = useState<7 | 30 | 90>(30);
  const [classification, setClassification] = useState<(typeof filters)[number]>("");
  const query = useFeedback(period, classification);
  return (
    <Screen>
      <PeriodSelector value={period} onChange={setPeriod} />
      <View style={styles.filters}>{filters.map((filter) => <Pressable key={filter || "all"} onPress={() => setClassification(filter)} style={[styles.filter, classification === filter && styles.filterActive]}><Text style={[styles.filterText, classification === filter && styles.filterTextActive]}>{filter || "all"}</Text></Pressable>)}</View>
      {query.isLoading && <ActivityIndicator />}
      {!!query.error && <Text style={styles.error}>{query.error.message}</Text>}
      {query.data?.map((item) => (
        <Card key={item.id}>
          <View style={styles.row}><Text style={styles.score}>{item.overall_rating ?? "—"}/5</Text><Text style={styles.classification}>{item.classification}</Text></View>
          <Text style={styles.date}>{new Date(item.created_at).toLocaleString()}</Text>
          {!!item.optional_comment && <Text style={styles.comment}>{item.optional_comment}</Text>}
          {item.answers.map((answer) => <View key={answer.aspect_id} style={styles.answer}><Text>{answer.label}</Text><Text style={styles.answerScore}>{answer.rating}/5</Text></View>)}
          {!!item.final_review_text && <View style={styles.final}><Text style={styles.finalLabel}>Final selected text</Text><Text>{item.final_review_text}</Text></View>}
          <Text style={styles.google}>Google opened: {item.google_opened ? "Yes" : "No"}</Text>
        </Card>
      ))}
      {query.data?.length === 0 && <Text style={styles.empty}>No feedback in this period.</Text>}
    </Screen>
  );
}

const styles = StyleSheet.create({
  filters: { flexDirection: "row", flexWrap: "wrap", gap: 8 },
  filter: { paddingHorizontal: 12, paddingVertical: 8, borderRadius: 999, backgroundColor: "#EAECF0" },
  filterActive: { backgroundColor: "#2457D6" },
  filterText: { textTransform: "capitalize", color: "#475467" },
  filterTextActive: { color: "#FFFFFF" },
  row: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  score: { fontSize: 22, fontWeight: "900" },
  classification: { color: "#667085" },
  date: { color: "#667085", fontSize: 12 },
  comment: { fontSize: 16, lineHeight: 22 },
  answer: { flexDirection: "row", justifyContent: "space-between", borderTopWidth: StyleSheet.hairlineWidth, borderColor: "#EAECF0", paddingTop: 8 },
  answerScore: { fontWeight: "700" },
  final: { backgroundColor: "#F4F7FB", borderRadius: 10, padding: 10, gap: 5 },
  finalLabel: { fontWeight: "800" },
  google: { color: "#475467", fontWeight: "600" },
  empty: { color: "#667085", textAlign: "center", marginTop: 30 },
  error: { color: "#B42318" }
});
