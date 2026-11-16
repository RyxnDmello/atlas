import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import useAsk from "@hooks/ask/useAsk";

import { Input } from "@components/ui/input";
import { Button } from "@components/ui/button";
import CitationList from "@components/Citations/CitationList";

import { askFormSchema, type AskForm } from "@schemas/ask/ask";

interface AskPanelProps {
  fileId: string;
  onDenied(status: number, code: string): Promise<void>;
}

export default function AskPanel({ fileId, onDenied }: AskPanelProps) {
  const { askState, askQuestion } = useAsk(fileId, onDenied);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<AskForm>({
    resolver: zodResolver(askFormSchema),
    defaultValues: {
      question: "",
    },
  });

  const pending = isSubmitting || askState.status === "streaming";

  const onSubmit = async (form: AskForm) => {
    await askQuestion(form.question);
  };

  return (
    <section className="space-y-4">
      <h2 className="text-lg font-semibold">Ask this file</h2>

      <form className="space-y-3" onSubmit={handleSubmit(onSubmit)}>
        <label className="block space-y-2">
          <span>Question</span>
          <Input disabled={pending} {...register("question")} />
        </label>

        {errors.question && <p role="alert">{errors.question.message}</p>}

        <Button type="submit" disabled={pending}>
          {pending ? "Asking…" : "Ask"}
        </Button>
      </form>

      {askState.status === "streaming" && (
        <p role="status">Answering… This answer is provisional.</p>
      )}

      {askState.error && <p role="alert">{askState.error}</p>}

      {askState.answer && (
        <p className="whitespace-pre-wrap wrap-anywhere">{askState.answer}</p>
      )}

      {askState.status === "success" && (
        <>
          <p role="status">Answer complete.</p>
          <CitationList citations={askState.citations} />
        </>
      )}
    </section>
  );
}
