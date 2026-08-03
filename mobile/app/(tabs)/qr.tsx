import * as FileSystem from "expo-file-system/legacy";
import * as Sharing from "expo-sharing";
import React, { useMemo, useState } from "react";
import { ActivityIndicator, Alert, Image, Linking, Pressable, StyleSheet, Text, View } from "react-native";

import { authenticatedRequest } from "@/api/client";
import { useDomains, useLocation, useSaveLocation } from "@/api/hooks";
import { Card } from "@/components/Card";
import { FormField } from "@/components/FormField";
import { PrimaryButton } from "@/components/PrimaryButton";
import { Screen } from "@/components/Screen";
import { API_BASE_URL } from "@/lib/config";
import { useAuth } from "@/store/auth";

export default function QrScreen() {
  const { accessToken, refresh } = useAuth();
  const locationQuery = useLocation();
  const domainsQuery = useDomains();
  const saveLocation = useSaveLocation();
  const [nameOverride, setNameOverride] = useState<string | null>(null);
  const [domainIdOverride, setDomainIdOverride] = useState<number | null>(null);
  const [googleUrlOverride, setGoogleUrlOverride] = useState<string | null>(null);
  const [message, setMessage] = useState("");

  const qrSource = useMemo(() => accessToken ? { uri: `${API_BASE_URL}/api/merchant/location/qr.png`, headers: { Authorization: `Bearer ${accessToken}` } } : undefined, [accessToken]);

  if (locationQuery.isPending) {
    return (
      <Screen>
        <Card style={styles.centeredCard}>
          <ActivityIndicator />
          <Text style={styles.message}>Loading location...</Text>
        </Card>
      </Screen>
    );
  }

  if (locationQuery.isError) {
    return (
      <Screen>
        <Card>
          <Text style={styles.heading}>Unable to load location</Text>
          <Text style={styles.message}>{locationQuery.error.message}</Text>
          <PrimaryButton title="Retry" onPress={() => void locationQuery.refetch()} />
        </Card>
      </Screen>
    );
  }

  const location = locationQuery.data ?? null;
  const name = nameOverride ?? location?.name ?? "";
  const domainId = domainIdOverride ?? location?.domain?.id ?? null;
  const googleUrl = googleUrlOverride ?? location?.google_review_url ?? "";

  const save = async () => {
    if (!domainId) return;
    setMessage("");
    try {
      await saveLocation.mutateAsync({
        exists: !!location,
        location: { name, domain_id: domainId, google_review_url: googleUrl, default_language: "en" }
      });
      setMessage("Location saved. Test the Google link before printing the QR.");
    } catch (error) {
      setMessage((error as Error).message);
    }
  };

  const verify = async () => {
    if (!accessToken) return;
    try {
      await authenticatedRequest("/api/merchant/location/verify-google-link/", accessToken, refresh, { method: "POST", body: "{}" });
      await locationQuery.refetch();
      setMessage("Link format verified. Confirm the correct physical listing opens.");
    } catch (error) {
      setMessage((error as Error).message);
    }
  };

  const rotateQr = () => {
    Alert.alert(
      "Rotate QR token?",
      "Every printed copy of the current QR will stop working. Use this only if the token is compromised.",
      [
        { text: "Cancel", style: "cancel" },
        {
          text: "Rotate",
          style: "destructive",
          onPress: async () => {
            if (!accessToken) return;
            try {
              await authenticatedRequest("/api/merchant/location/rotate-qr/", accessToken, refresh, {
                method: "POST",
                body: JSON.stringify({ confirmation: "ROTATE" })
              });
              await locationQuery.refetch();
              setMessage("QR token rotated. Replace all printed materials.");
            } catch (error) {
              setMessage((error as Error).message);
            }
          }
        }
      ]
    );
  };

  const shareQr = async () => {
    if (!accessToken || !(await Sharing.isAvailableAsync())) return;
    if (!FileSystem.cacheDirectory) throw new Error("Temporary file storage is unavailable.");
    const destination = `${FileSystem.cacheDirectory}reviewflow-qr.png`;
    const result = await FileSystem.downloadAsync(`${API_BASE_URL}/api/merchant/location/qr.png`, destination, { headers: { Authorization: `Bearer ${accessToken}` } });
    await Sharing.shareAsync(result.uri, { mimeType: "image/png", dialogTitle: "Share QR code" });
  };

  return (
    <Screen>
      <Card>
        <Text style={styles.heading}>{location ? "Location configuration" : "Create your location"}</Text>
        <FormField label="Location name" value={name} onChangeText={setNameOverride} autoCapitalize="words" />
        <Text style={styles.label}>Domain</Text>
        {domainsQuery.isPending && <Text style={styles.message}>Loading domains...</Text>}
        {domainsQuery.isError && <Text style={styles.errorText}>{domainsQuery.error.message}</Text>}
        <View style={styles.domains}>
          {domainsQuery.data?.map((domain) => <Pressable key={domain.id} onPress={() => setDomainIdOverride(domain.id)} style={[styles.domain, domainId === domain.id && styles.domainActive]}><Text style={[styles.domainText, domainId === domain.id && styles.domainTextActive]}>{domain.name}</Text></Pressable>)}
        </View>
        <FormField label="Official Google review-request link" value={googleUrl} onChangeText={setGoogleUrlOverride} keyboardType="url" autoCapitalize="none" />
        <PrimaryButton title={location ? "Save changes" : "Create location"} loading={saveLocation.isPending} disabled={!name.trim() || !domainId || !googleUrl.trim() || domainsQuery.isError} onPress={save} />
        {!!location && <PrimaryButton title="Validate Google link format" onPress={verify} />}
        {!!message && <Text style={styles.message}>{message}</Text>}
      </Card>

      {!!location && (
        <Card style={styles.qrCard}>
          <Text style={styles.heading}>Stable location QR</Text>
          {!!qrSource && <Image source={qrSource} style={styles.qr} resizeMode="contain" />}
          <Text style={styles.url}>{location.public_url}</Text>
          <PrimaryButton title="Share / download QR" onPress={shareQr} />
          <PrimaryButton title="Preview customer flow" onPress={() => Linking.openURL(location.public_url)} />
          <PrimaryButton title="Test Google review link" onPress={() => Linking.openURL(location.google_review_url)} />
          <Text style={styles.note}>Changing questions, branding or the Google link does not change this QR token.</Text>
          <Pressable onPress={rotateQr}><Text style={styles.dangerLink}>Advanced: rotate compromised QR token</Text></Pressable>
        </Card>
      )}
    </Screen>
  );
}

const styles = StyleSheet.create({
  heading: { fontSize: 18, fontWeight: "900", color: "#172033" },
  label: { fontWeight: "700", color: "#172033" },
  centeredCard: { alignItems: "center" },
  domains: { flexDirection: "row", flexWrap: "wrap", gap: 8 },
  domain: { borderRadius: 999, backgroundColor: "#EAECF0", paddingVertical: 8, paddingHorizontal: 12 },
  domainActive: { backgroundColor: "#2457D6" },
  domainText: { color: "#475467" },
  domainTextActive: { color: "#FFFFFF" },
  message: { color: "#475467" },
  errorText: { color: "#B42318" },
  qrCard: { alignItems: "center" },
  qr: { width: 250, height: 250 },
  url: { color: "#667085", fontSize: 12, textAlign: "center" },
  note: { color: "#667085", lineHeight: 19, textAlign: "center" },
  dangerLink: { color: "#B42318", fontWeight: "700", paddingVertical: 8 }
});
