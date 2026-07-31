import React, { useState } from "react";
import { StyleSheet, Text } from "react-native";

import { rawRequest } from "@/api/client";
import { FormField } from "@/components/FormField";
import { PrimaryButton } from "@/components/PrimaryButton";
import { Screen } from "@/components/Screen";

export default function ForgotPasswordScreen() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const submit = async () => {
    setLoading(true);
    try {
      const result = await rawRequest<{ detail: string }>("/api/auth/password-reset/", { method: "POST", body: JSON.stringify({ email }) });
      setMessage(result.detail);
    } catch (error) {
      setMessage((error as Error).message);
    } finally {
      setLoading(false);
    }
  };
  return <Screen><Text style={styles.title}>Reset password</Text><Text style={styles.note}>A one-time reset link will be sent if the account exists.</Text><FormField label="Email" value={email} onChangeText={setEmail} keyboardType="email-address" autoComplete="email" /><PrimaryButton title="Send reset link" loading={loading} disabled={!email.trim()} onPress={submit} />{!!message && <Text>{message}</Text>}</Screen>;
}

const styles = StyleSheet.create({ title: { fontSize: 28, fontWeight: "900", color: "#172033" }, note: { color: "#667085" } });
