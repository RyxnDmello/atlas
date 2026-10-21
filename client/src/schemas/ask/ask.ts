import { z } from "zod";

export const askFormSchema = z.object({
  question: z.string().trim().min(1, "Enter a question."),
});

export type AskForm = z.infer<typeof askFormSchema>;

export const atlasErrorSchema = z.object({
  error: z.string().min(1),
  code: z.string().min(1),
});

export const answerSchema = z.object({
  text: z.string(),
});

export const citationSchema = z.object({
  index: z.number().int().nonnegative(),
  page: z.number().int().nullable(),
  heading: z.string().nullable(),
  section: z.string().nullable(),
  excerpt: z.string(),
});

export const citationsSchema = z.object({
  citations: z.array(citationSchema),
});

export const doneSchema = z.object({
  status: z.literal("completed"),
});

export type Citation = z.infer<typeof citationSchema>;
