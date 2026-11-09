import { z } from "zod";

const email = z.email().transform((value) => value.toLowerCase());
const password = z.string().min(8).max(128);

export const registrationSchema = z.strictObject({
  name: z.string().trim().min(1).max(100),
  email,
  password,
});

export const loginSchema = z.strictObject({
  email,
  password,
});

export const resendSchema = z.strictObject({
  email,
});

export const verificationSchema = z.strictObject({
  email,
  otp: z.string().regex(/^\d{6}$/),
});

export const userSchema = z.strictObject({
  id: z.uuid(),
  name: z.string(),
  email: z.email(),
});

export const authenticatedSchema = z.strictObject({
  user: userSchema,
  access_token: z.string().min(1).max(32768),
});

export const verificationRequiredSchema = z.strictObject({
  status: z.literal("verification_required"),
});

export const authErrorSchema = z.strictObject({
  code: z.string(),
  error: z.string(),
});

export type Login = z.infer<typeof loginSchema>;
export type Registration = z.infer<typeof registrationSchema>;

export type AuthenticatedUser = z.infer<typeof userSchema>;
export type AuthenticatedResponse = z.infer<typeof authenticatedSchema>;

export type Resend = z.infer<typeof resendSchema>;
export type Verification = z.infer<typeof verificationSchema>;
export type VerificationRequired = z.infer<typeof verificationRequiredSchema>;
