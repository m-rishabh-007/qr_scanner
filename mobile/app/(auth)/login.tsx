import { zodResolver } from "@hookform/resolvers/zod";
import { Link, router } from "expo-router";
import React, { useState } from "react";
import { StyleSheet, Text, View } from "react-native";
import { Controller, useForm } from "react-hook-form";
import { z } from "zod";

import { FormField } from "@/components/FormField";
import { PrimaryButton } from "@/components/PrimaryButton";
import { Screen } from "@/components/Screen";
import { useAuth } from "@/store/auth";

const schema = z.object({ email: z.string().email(), password: z.string().min(1) });
type FormData = z.infer<typeof schema>;

export default function LoginScreen() {
  const { signIn } = useAuth();
  const [serverError, setServerError] = useState("");
  const { control, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>({ resolver: zodResolver(schema), defaultValues: { email: "", password: "" } });

  const submit = handleSubmit(async (values) => {
    setServerError("");
    try {
      await signIn(values.email.trim().toLowerCase(), values.password);
      router.replace("/(tabs)");
    } catch (error) {
      setServerError((error as Error).message);
    }
  });

  return (
    <Screen style={styles.content}>
      <View style={styles.logo}><Text style={styles.logoText}>R</Text></View>
      <Text style={styles.title}>Merchant sign in</Text>
      <Text style={styles.subtitle}>Use the approved merchant account for your physical location.</Text>
      <Controller control={control} name="email" render={({ field: { onChange, onBlur, value } }) => <FormField label="Email" keyboardType="email-address" autoComplete="email" onBlur={onBlur} onChangeText={onChange} value={value} error={errors.email?.message} />} />
      <Controller control={control} name="password" render={({ field: { onChange, onBlur, value } }) => <FormField label="Password" secureTextEntry autoComplete="current-password" onBlur={onBlur} onChangeText={onChange} value={value} error={errors.password?.message} />} />
      {!!serverError && <Text style={styles.error}>{serverError}</Text>}
      <PrimaryButton title="Sign in" loading={isSubmitting} onPress={submit} />
      <Text style={styles.center}><Link href="/(auth)/forgot-password" style={styles.link}>Forgot password?</Link></Text>
      <Text style={styles.center}>New merchant? <Link href="/(auth)/register" style={styles.link}>Create an account</Link></Text>
      <Text style={styles.note}>Email verification and administrator approval are required before sign-in.</Text>
    </Screen>
  );
}

const styles = StyleSheet.create({
  content: { flexGrow: 1, justifyContent: "center", gap: 14 },
  logo: { width: 60, height: 60, borderRadius: 18, backgroundColor: "#172033", alignItems: "center", justifyContent: "center" },
  logoText: { color: "#FFFFFF", fontSize: 28, fontWeight: "900" },
  title: { fontSize: 28, fontWeight: "900", color: "#172033" },
  subtitle: { color: "#667085", lineHeight: 21 },
  error: { color: "#B42318" },
  center: { textAlign: "center", color: "#667085" },
  link: { color: "#2457D6", fontWeight: "700" },
  note: { color: "#667085", fontSize: 12, textAlign: "center" }
});
