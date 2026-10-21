"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import type { UseAskResult } from "@hooks/ask/useAsk";

import {
  Card,
  CardTitle,
  CardHeader,
  CardContent,
  CardDescription,
} from "@components/ui/card";
import { Label } from "@components/ui/label";
import { Input } from "@components/ui/input";
import { Button } from "@components/ui/button";

import { askFormSchema, type AskForm } from "@schemas/ask/ask";

export interface AskPanelProps {
  ask: UseAskResult;
  disabled: boolean;
}

export default function AskPanel({ ask, disabled }: AskPanelProps) {
  const form = useForm<AskForm>({
    resolver: zodResolver(askFormSchema),
    defaultValues: {
      question: "",
    },
  });

  const streaming = ask.status === "streaming";

  return (
    <Card className="w-full max-w-xl">
      <CardHeader>
        <CardTitle>Ask this file</CardTitle>

        <CardDescription>
          {disabled
            ? "Upload a file to ask a question."
            : "Ask a question about your active file."}
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-6">
        <form
          className="space-y-4"
          onSubmit={form.handleSubmit(({ question }) => ask.submit(question))}
        >
          <div className="space-y-2">
            <Label htmlFor="question">Question</Label>

            <Input
              id="question"
              {...form.register("question")}
              disabled={disabled || streaming}
            />

            {form.formState.errors.question && (
              <p
                id="question-error"
                role="alert"
                className="text-sm text-destructive"
              >
                {form.formState.errors.question.message}
              </p>
            )}
          </div>

          <Button type="submit" disabled={disabled || streaming}>
            {streaming ? "Answering…" : "Ask"}
          </Button>
        </form>

        {streaming && (
          <p role="status" className="text-sm text-muted-foreground">
            Answering… Text is provisional until complete.
          </p>
        )}

        {ask.status === "success" && (
          <p role="status" className="text-sm text-muted-foreground">
            Answer complete.
          </p>
        )}

        {ask.error && (
          <p role="alert" className="text-sm text-destructive">
            {ask.error}
          </p>
        )}

        {ask.answer && (
          <section className="space-y-2">
            <h2 className="font-medium">Answer</h2>

            <div
              data-testid="answer"
              className="whitespace-pre-wrap wrap-break-word rounded-lg border p-4 text-sm"
            >
              {ask.answer}
            </div>
          </section>
        )}
      </CardContent>
    </Card>
  );
}
