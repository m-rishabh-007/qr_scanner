import { zodResolver } from "@hookform/resolvers/zod";
import { Link } from "expo-router";
import React, { useState } from "react";
import { StyleSheet, Text } from "react-native";
import { Controller, useForm } from "react-hook-form";
import { z } from "zod";

import { registerMerchant } from "@/api/hooks";
import { FormField } from "@/components/FormField";
import { PrimaryButton } from "@/components/PrimaryButton";
import { Screen } from "@/components/Screen";

const schema = z.object({
  business_name: z.string().min(2).max(180),
  email: z.string().email(),
  password: z.string().min(10)
});
type FormData = z.infer<typeof schema>;

export default function RegisterScreen() {
  const [message, setMessage] = useState("");
  const [serverError, setServerError] = useState("");
  const { control, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>({ resolver: zodResolver(schema), defaultValues: { business_name: "", email: "", password: "" } });

  const submit = handleSubmit(async (values) => {
    setServerError("");
    setMessage("");
    try {
      const result = await registerMerchant({ ...values, email: values.email.trim().toLowerCase() });
      setMessage(result.detail);
    } catch (error) {
      setServerError((error as Error).message);
    }
  });

  return (
    <Screen>
      <Text style={styles.title}>Create merchant account</Text>
      <Text style={styles.subtitle}>One approved account manages one physical Google Maps listing in the MVP.</Text>
      <Controller control={control} name="business_name" render={({ field: { onChange, value } }) => <FormField label="Business name" autoCapitalize="words" onChangeText={onChange} value={value} error={errors.business_name?.message} />} />
      <Controller control={control} name="email" render={({ field: { onChange, value } }) => <FormField label="Email" keyboardType="email-address" autoComplete="email" onChangeText={onChange} value={value} error={errors.email?.message} />} />
      <Controller control={control} name="password" render={({ field: { onChange, value } }) => <FormField label="Password" secureTextEntry autoComplete="new-password" onChangeText={onChange} value={value} error={errors.password?.message} />} />
      {!!serverError && <Text style={styles.error}>{serverError}</Text>}
      {!!message && <Text style={styles.success}>{message}</Text>}
      <PrimaryButton title="Register" loading={isSubmitting} onPress={submit} />
      <Text style={styles.center}><Link href="/(auth)/login" style={styles.link}>Back to sign in</Link></Text>
    </Screen>
  );
}

const styles = StyleSheet.create({
  title: { fontSize: 28, fontWeight: "900", color: "#172033", marginTop: 18 },
  subtitle: { color: "#667085", lineHeight: 21 },
  error: { color: "#B42318" },
  success: { color: "#027A48" },
  center: { textAlign: "center" },
  link: { color: "#2457D6", fontWeight: "700" }
});
