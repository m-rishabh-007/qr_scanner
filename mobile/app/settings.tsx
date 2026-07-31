import React, { useState } from "react";
import { Alert, Linking, StyleSheet, Text } from "react-native";

import { authenticatedRequest } from "@/api/client";
import { Card } from "@/components/Card";
import { FormField } from "@/components/FormField";
import { PrimaryButton } from "@/components/PrimaryButton";
import { Screen } from "@/components/Screen";
import { API_BASE_URL } from "@/lib/config";
import { useAuth } from "@/store/auth";

export default function SettingsScreen() {
  const { accessToken, refresh, signOut } = useAuth();
  const [password, setPassword] = useState("");
  const deleteAccount = () => {
    Alert.alert("Delete account?", "This disables merchant access and starts the configured deletion process.", [
      { text: "Cancel", style: "cancel" },
      { text: "Delete", style: "destructive", onPress: async () => {
        if (!accessToken) return;
        try {
          await authenticatedRequest("/api/auth/delete-account/", accessToken, refresh, { method: "POST", body: JSON.stringify({ password }) });
          await signOut();
        } catch (error) {
          Alert.alert("Deletion failed", (error as Error).message);
        }
      } }
    ]);
  };
  return (
    <Screen>
      <Card>
        <Text style={styles.heading}>Account</Text>
        <PrimaryButton title="Sign out" onPress={signOut} />
      </Card>
      <Card>
        <Text style={styles.heading}>Privacy and support</Text>
        <Text style={styles.link} onPress={() => Linking.openURL(`${API_BASE_URL}/privacy/`)}>Privacy notice</Text>
        <Text style={styles.link} onPress={() => Linking.openURL(`${API_BASE_URL}/account-deletion/`)}>External deletion page</Text>
      </Card>
      <Card>
        <Text style={styles.heading}>Delete account</Text>
        <Text style={styles.note}>Enter your password, then confirm the destructive action.</Text>
        <FormField label="Current password" value={password} onChangeText={setPassword} secureTextEntry />
        <PrimaryButton title="Delete account" destructive disabled={!password} onPress={deleteAccount} />
      </Card>
    </Screen>
  );
}

const styles = StyleSheet.create({
  heading: { fontSize: 18, fontWeight: "900", color: "#172033" },
  link: { color: "#2457D6", fontWeight: "700", paddingVertical: 6 },
  note: { color: "#667085" }
});
