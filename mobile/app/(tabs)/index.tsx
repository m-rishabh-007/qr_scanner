import * as Sharing from "expo-sharing";
import React, { useRef, useState } from "react";
import { ActivityIndicator, StyleSheet, Text, View } from "react-native";
import ViewShot, { captureRef } from "react-native-view-shot";

import { useOverview } from "@/api/hooks";
import { AspectChart, TrendChart } from "@/components/Charts";
import { Card } from "@/components/Card";
import { PeriodSelector } from "@/components/PeriodSelector";
import { PrimaryButton } from "@/components/PrimaryButton";
import { Screen } from "@/components/Screen";

export default function OverviewScreen() {
  const [period, setPeriod] = useState<7 | 30 | 90>(30);
  const reportRef = useRef<React.ElementRef<typeof ViewShot>>(null);
  const query = useOverview(period);
  const share = async () => {
    if (!reportRef.current || !(await Sharing.isAvailableAsync())) return;
    const uri = await captureRef(reportRef, { format: "png", quality: 0.95 });
    await Sharing.shareAsync(uri, { mimeType: "image/png", dialogTitle: "Share report" });
  };
  if (query.isLoading) return <View style={styles.center}><ActivityIndicator /></View>;
  if (query.error || !query.data) return <Screen><Text style={styles.error}>{query.error?.message ?? "Unable to load overview."}</Text></Screen>;
  const data = query.data;
  const metrics = data.metrics;
  const metricRows = [
    ["QR scans", metrics.qr_scans], ["Feedback completed", metrics.feedback_completed],
    ["Google page opened", metrics.google_page_opened], ["Average score", metrics.average_overall_score ?? "—"]
  ];
  return (
    <Screen>
      <PeriodSelector value={period} onChange={setPeriod} />
      <ViewShot ref={reportRef} options={{ format: "png", quality: 0.95 }}>
        <View style={styles.report}>
          <View style={styles.metrics}>
            {metricRows.map(([label, value]) => <Card key={String(label)} style={styles.metric}><Text style={styles.metricValue}>{value}</Text><Text style={styles.metricLabel}>{label}</Text></Card>)}
          </View>
          <Card><Text style={styles.heading}>Overall experience trend</Text><Text style={styles.caption}>{data.response_count} responses · {period} days</Text><TrendChart data={data.trend} /></Card>
          <Card><Text style={styles.heading}>Aspect averages</Text><AspectChart data={data.aspects} /></Card>
          <Card><Text style={styles.heading}>Highlights</Text>{data.highlights.map((item, index) => <Text key={`${item.type}-${index}`} style={styles.highlight}>• {item.text}</Text>)}</Card>
        </View>
      </ViewShot>
      <PrimaryButton title="Share report snapshot" onPress={share} />
    </Screen>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, alignItems: "center", justifyContent: "center" },
  report: { gap: 14, backgroundColor: "#F4F7FB" },
  metrics: { flexDirection: "row", flexWrap: "wrap", gap: 10 },
  metric: { width: "48%" },
  metricValue: { fontSize: 25, fontWeight: "900", color: "#172033" },
  metricLabel: { color: "#667085" },
  heading: { fontSize: 17, fontWeight: "800", color: "#172033" },
  caption: { color: "#667085" },
  highlight: { color: "#344054", lineHeight: 21 },
  error: { color: "#B42318" }
});
