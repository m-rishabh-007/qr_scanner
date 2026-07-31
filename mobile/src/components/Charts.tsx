import React from "react";
import { StyleSheet, Text, View, useWindowDimensions } from "react-native";
import Svg, { Circle, Line, Polyline, Rect, Text as SvgText } from "react-native-svg";

export function TrendChart({ data }: { data: { day: string; average: number }[] }) {
  const { width } = useWindowDimensions();
  const chartWidth = Math.max(260, width - 64);
  const height = 180;
  const pad = 24;
  if (!data.length) return <Text style={styles.empty}>Not enough data for a trend yet.</Text>;
  const points = data.map((item, index) => {
    const x = data.length === 1 ? chartWidth / 2 : pad + (index / (data.length - 1)) * (chartWidth - pad * 2);
    const y = height - pad - ((item.average - 1) / 4) * (height - pad * 2);
    return { x, y, ...item };
  });
  return (
    <Svg width={chartWidth} height={height} accessibilityLabel="Overall experience trend chart">
      {[1, 2, 3, 4, 5].map((value) => {
        const y = height - pad - ((value - 1) / 4) * (height - pad * 2);
        return <Line key={value} x1={pad} x2={chartWidth - pad} y1={y} y2={y} stroke="#EAECF0" />;
      })}
      <Polyline points={points.map((p) => `${p.x},${p.y}`).join(" ")} fill="none" stroke="#2457D6" strokeWidth="3" />
      {points.map((point) => <Circle key={point.day} cx={point.x} cy={point.y} r="4" fill="#2457D6" />)}
    </Svg>
  );
}

export function AspectChart({ data }: { data: { label: string; average: number }[] }) {
  const { width } = useWindowDimensions();
  const chartWidth = Math.max(260, width - 64);
  if (!data.length) return <Text style={styles.empty}>No aspect ratings yet.</Text>;
  const rowHeight = 42;
  const labelWidth = Math.min(120, chartWidth * 0.38);
  const height = data.length * rowHeight;
  return (
    <Svg width={chartWidth} height={height} accessibilityLabel="Average aspect scores">
      {data.map((item, index) => {
        const y = index * rowHeight + 8;
        const barWidth = ((chartWidth - labelWidth - 42) * item.average) / 5;
        return (
          <React.Fragment key={item.label}>
            <SvgText x="0" y={y + 16} fontSize="12" fill="#344054">{item.label.slice(0, 18)}</SvgText>
            <Rect x={labelWidth} y={y} width={chartWidth - labelWidth - 42} height="18" rx="5" fill="#EAECF0" />
            <Rect x={labelWidth} y={y} width={barWidth} height="18" rx="5" fill="#2457D6" />
            <SvgText x={chartWidth - 36} y={y + 15} fontSize="12" fill="#172033">{item.average.toFixed(1)}</SvgText>
          </React.Fragment>
        );
      })}
    </Svg>
  );
}

const styles = StyleSheet.create({ empty: { color: "#667085", paddingVertical: 18 } });
